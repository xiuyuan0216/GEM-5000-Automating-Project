# Werfen Summer Internship 2022: GEM 5000 Automation Project
# Developer: Kevin Truong, Raymond Li, Ronnie Yuan
# Purpose: Takes a CopyIL directory as an input and returns information about the cartridge failure to the user.

# Data Pipeline [UPDATED 8/10/22]
# -----
# User inputs CopyIL File
# Convert cartridge, sensor, and event log .csv files to pandas dataframe and store in DataFrames
# Collect the information needed for each failure check into the CartDict as a modified dataframe from the DataFrames
# Run each of the failure checks on the associated CartDict entries
# Parse through general CartDict to find possible reason for failure
# Connect to dashboard (Plotly-Dash, pymongo)
# Return reason for failure to user through the dashboard

import pandas as pd
import json
from tkinter import filedialog
from pathlib import Path
from collections import deque
from datetime import datetime

# These modules are for the leak detection algorithm.
import numpy as np
import matplotlib.pyplot as plt


# CartDict holds the information that each check function needs to determine if a certain failure occurred.
# This information is collected from the processed DataFrames of each .csv file.
CartDict = {"General": dict(), "Leaks": dict(), "Peroxide Exposure": dict(), "Sticky Solenoid": dict(),
            "Bubbles on Sensor": dict(), "Delamination": dict()}

# DataFrames holds the pandas dataframe version of the .csv files, where the key is the file name and the key is the
# processed dataframe from the parsing functions.
DataFrames = {"Sensor": dict(), "Event Log": dict(), "Cartridge": dict()}

Medians = {}


# I don't even remember why this naming convention exists. Allows us to access the needed .csv files when just
# given the CopyIL directory.
CopyIL = ''
CopyILPath = ''
CopyILDirectory = ''

# Allows us to collect a list of sensors that were disabled by the iQM when parsing sensor file.
SensorErrorMessages = []

# Accesses Ronnie's json files so that we can output error code reasoning in read only mode.
with open("error_code.json", 'r') as file:
    file_dict = json.load(file)
with open("error_reason.json", 'r') as f:
    file_reason = json.load(f)


# Allows the user to select a CopyIL directory to parse through, should change to use a try-except clause for
# when user inputs an invalid directory/file.
def SelectCopyIL():
    global CopyIL
    CopyIL = filedialog.askdirectory()
    global CopyILPath
    CopyILPath = Path(CopyIL)


# The meat and potatoes function, calls on each individual parsing method along with each of the failure mode's
# collect and check functions.
def MainParse():
    try:
        for filename in CopyILPath.iterdir():
            if '00000' in filename.name and filename.is_dir():
                global CopyILDirectory
                CopyILDirectory = Path(CopyIL + '/' + filename.name)

                # Gives complete absolute path to the main file.
                CopyILDirectory.resolve()

        # Stored in DataFrames.
        ParseCartridge()
        ParseEventLog()
        ParseSensor()

        # Stored in CartDict.
        PeroxideExposureCollect()
        LeakCollect()
        # DelaminationCollect()

        # Returns boolean values.
        PeroxideExposureCheck()
        LeakCheck()
        # DelaminationCheck()

    except FileNotFoundError:
        print("Could not find CopyIL file directory.")


# Parses the cartridge file and turns it into a dataframe, for mostly general information. Called by MainParse.
def ParseCartridge():
    # Some naughty lines hiding in these .csv files...
    CartridgePath = str(CopyILDirectory.resolve()) + '\cartridge.csv'
    CartridgeDF = pd.read_csv(CartridgePath, on_bad_lines='skip')

    DataFrames["Cartridge"] = CartridgeDF

    # Accesses specific part of dataframe, should try to make sure that it works for all CopyIL examples.
    cartSerialNumber = int(CartridgeDF.iloc[9, 4])
    cartAge = int(CartridgeDF.iloc[31, 4])

    CartDict["General"]["Serial Number"] = cartSerialNumber
    CartDict["General"]["Age"] = cartAge


# Parses the event log file and turns it into a dataframe. Called by MainParse.
def ParseEventLog():
    # Resolve() is to make sure we get the absolute path.
    EventLogPath = str(CopyILDirectory.resolve()) + '\EVENT_LOG.csv'
    EventLogDF = pd.read_csv(EventLogPath)

    DataFrames["Event Log"] = EventLogDF

    # Ronnie's code chunk here, I believe this is for searching through sensor file later.
    # TO-DO: Check that it's the right cartridge, cross-reference with serial number.
    messages = EventLogDF['Message'].dropna().to_list()
    for message in messages:
        if 'Sensor Disabled by iQM' in message:
            SensorErrorMessages.append(message)

    # This section of code will prove very helpful later I figure.
    sensor_failure = dict()
    for i in SensorErrorMessages:
        temp = i.split(':')
        fail_type = temp[1]
        fail_substance = temp[2].split(',')
        sensor_failure[fail_type] = fail_substance

    # Grabs the error code from the dataframe messages series.
    for index, row in EventLogDF.iterrows():
        try:
            if row['Cartridge S/N'] == CartDict["General"]["Serial Number"] and 'Cartridge removed' in row['Message']:
                messageSplit = row['Message'].split()

                # Grabs error code from event log message column
                cartErrorCode = messageSplit[2]
                cartErrorCode = cartErrorCode.rstrip(cartErrorCode[-1])
                CartDict["General"]["Error Code"] = int(cartErrorCode)
            else:
                CartDict["General"]["Error Code"] = 0

        except IndexError:
            print('Index Error Detected.')
        except UnboundLocalError:
            print('Cartridge probably ejected almost immediately.')


# Parses the sensor file and turns it into a dataframe. Called by MainParse.
def ParseSensor():
    # No idea why it gives a warning unless I set low_memory to False, shrug.
    SensorPath = str(CopyILDirectory.resolve()) + '\SENSOR.csv'
    SensorDataFrame = pd.read_csv(SensorPath, low_memory=False)

    DataFrames["Sensor"] = SensorDataFrame


# Collects the needed information for the PeroxideExposureCheck from the Dataframes.
def PeroxideExposureCollect():
    SensorDF = DataFrames["Sensor"]

    # Creates new condensed dataframe and stores into CartDict.
    BmV = SensorDF[SensorDF["'CalType'"] == "B"]
    BmVDataFrame = BmV[["'Crea'", "'Cr'", "'Lac'", "'Glu'"]].reset_index(drop=True)
    BmVDataFrame = BmVDataFrame.drop(labels=0, axis=0)

    BDrift = SensorDF[SensorDF["'CalType'"] == "'B-DRIFT'"]
    BDriftDataFrame = BDrift[["'Crea'", "'Cr'", "'Lac'", "'Glu'"]].reset_index(drop=True)

    # For their associated check functions.
    CartDict["Peroxide Exposure"]["BmV"] = BmVDataFrame
    CartDict["Peroxide Exposure"]["B Drift"] = BDriftDataFrame


# If H2O2 is detected, it will mess with the sensor measurements.
# All three conditions must be met for at least 4 out of 12 B calibrations, which occur every 30 minutes.
# 1. Glucose B drift greater than 6 or Glucose B drift is incalculable.
# 2. Lactate B drift greater than 0.3 or Lactate B drift is incalculable.
# 3. Creatine and Creatinine BmV less than or equal to -15.
def PeroxideExposureCheck():
    detected = False
    RollingQueue = deque()

    BDF = CartDict["Peroxide Exposure"]["BmV"]
    BDriftDF = CartDict["Peroxide Exposure"]["B Drift"]

    # Zip allows us to iterate through two dataframes at the same time.
    for (BmV, row1), (BDrift, row2) in zip(BDF.iterrows(), BDriftDF.iterrows()):
        holder = [row1["'Crea'"], row1["'Cr'"], row1["'Lac'"], row1["'Glu'"], row2["'Crea'"], row2["'Cr'"],
                  row2["'Lac'"], row2["'Glu'"]]

        # Ensures that we are only looking at the current rolling 12 queue.
        if len(RollingQueue) == 12:
            RollingQueue.append(holder)
            RollingQueue.popleft()
        else:
            RollingQueue.append(holder)

        # Will check if the conditions have been met.
        counter = 0
        for hold in RollingQueue:
            if (float(hold[0]) <= -15 and float(hold[1]) <= -15) \
                    and (float(hold[6]) > 0.3 or float(hold[6]) == "'INCALC'") \
                    and (float(hold[7]) > 6 or float(hold[7]) == "'INCALC'"):
                counter = counter + 1

        if counter >= 4:
            detected = True

    if detected:
        print("Peroxide Exposure Signature Detected.")
    else:
        print("Peroxide Exposure Not Detected.")

    return detected


# Helper function for leak detection, modified z score is more robust when dealing with small data samples and will
# more account for outliers' effects on the mean with the usage of median.
def ModifiedZScore(ZScore, Median, MAD):
    return (float(ZScore) - Median) * 0.675 / MAD


def MedianSubtractNaA(row):
    return float(row[:]) - Medians["Na A"]


def MedianSubtractKA(row):
    return float(row[:]) - Medians["K A"]


def MedianSubtractCaA(row):
    return float(row[:]) - Medians["Ca A"]


def MedianSubtractClA(row):
    return float(row[:]) - Medians["Cl A"]


def MedianSubtractNaB(row):
    return float(row[:]) - Medians["Na B"]


def MedianSubtractKB(row):
    return float(row[:]) - Medians["K B"]


def MedianSubtractCaB(row):
    return float(row[:]) - Medians["Ca B"]


def MedianSubtractClB(row):
    return float(row[:]) - Medians["Cl B"]


# Collects the needed information for the LeakCheck from the Dataframes. We are specifically looking for leaks that
# result in air leakage into the fluidic system and messes with sensor measurements.
def LeakCollect():
    SensorDF = DataFrames["Sensor"]
    EventLogDF = DataFrames["Event Log"]
    SerialNumber = CartDict["General"]["Serial Number"]

    # Creates new condensed dataframe and stores into CartDict.
    ADrift = SensorDF[SensorDF["'CalType'"] == "'A-DRIFT'"]
    ADriftDataFrame = ADrift[["'Na'", "'K'", "'Ca'", "'Cl'"]].reset_index(drop=True)

    BDrift = SensorDF[SensorDF["'CalType'"] == "'B-DRIFT'"]
    BDriftDataFrame = BDrift[["'Na'", "'K'", "'Ca'", "'Cl'"]].reset_index(drop=True)

    PO2Disabled = EventLogDF[EventLogDF['Message'] == "Sensor Disabled by iQM: "]
    # PCSNDError = []

    CartDict["Leaks"]["A Drift"] = ADriftDataFrame
    CartDict["Leaks"]["B Drift"] = BDriftDataFrame


# Leaks will usually fail as pO2 iQM disabled messages, and sometimes PCSND too.
# Will usually present itself as significant spikes in B drift, and sometimes A drift too, on multiple sensors at the
# same time. Looking to use Modified Z-Score as an adjustable metric to detect outliers.

def LeakCheck():
    detected = False
    ModifiedZScoreLimit = 4
    # check out iqm sensor drift retry amounts
    SensorOutlierTrigger = 6
    SensorsUntilFailure = 4

    # Other parameters we can tinker with later to make this prediction more precise.
    LengthOfSpike = 1
    RequirePO2Disabled = False
    RequirePCSNDDisabled = False
    ConstantMultiplier = 0.675

    ADriftDF = CartDict["Leaks"]["A Drift"]
    BDriftDF = CartDict["Leaks"]["B Drift"]

    # could use a "for col in df:" type of thing
    Medians["Na A"] = ADriftDF.loc[:, "'Na'"].median()
    Medians["K A"] = ADriftDF.loc[:, "'K'"].median()
    Medians["Ca A"] = ADriftDF.loc[:, "'Ca'"].median()
    Medians["Cl A"] = ADriftDF.loc[:, "'Cl'"].median()

    Medians["Na B"] = BDriftDF.loc[:, "'Na'"].median()
    Medians["K B"] = BDriftDF.loc[:, "'K'"].median()
    Medians["Ca B"] = BDriftDF.loc[:, "'Ca'"].median()
    Medians["Cl B"] = BDriftDF.loc[:, "'Cl'"].median()

    NaMADA = np.abs(ADriftDF.loc[:, ["'Na'"]].apply(MedianSubtractNaA, axis=1)).median()
    KMADA = np.abs(ADriftDF.loc[:, ["'K'"]].apply(MedianSubtractKA, axis=1)).median()
    CaMADA = np.abs(ADriftDF.loc[:, ["'Ca'"]].apply(MedianSubtractCaA, axis=1)).median()
    ClMADA = np.abs(ADriftDF.loc[:, ["'Cl'"]].apply(MedianSubtractClA, axis=1)).median()

    NaMADB = np.abs(BDriftDF.loc[:, ["'Na'"]].apply(MedianSubtractNaB, axis=1)).median()
    KMADB = np.abs(BDriftDF.loc[:, ["'K'"]].apply(MedianSubtractKB, axis=1)).median()
    CaMADB = np.abs(BDriftDF.loc[:, ["'Ca'"]].apply(MedianSubtractCaB, axis=1)).median()
    ClMADB = np.abs(BDriftDF.loc[:, ["'Cl'"]].apply(MedianSubtractClB, axis=1)).median()

    # print("MAD Values: " + str(NaMAD) + " " + str(KMAD) + " " + str(CaMAD) + " " + str(ClMAD))

    Outliers = {"NaADriftOutliers": 0, "KADriftOutliers": 0, "CaADriftOutliers": 0, "ClADriftOutliers": 0,
                "NaBDriftOutliers": 0, "KBDriftOutliers": 0, "CaBDriftOutliers": 0, "ClBDriftOutliers": 0}

    SensorFailures = 0

    for index, row in ADriftDF.iterrows():
        if np.abs(ModifiedZScore(row["'Na'"], Medians["Na A"], NaMADA)) > ModifiedZScoreLimit:
            # print("Spike detected in the A Drift calculation of the Sodium Sensor: Modified Z Score = " + str(ModifiedZScore(row["'Na'"], Medians["Na A"], NaMADA)))
            Outliers["NaADriftOutliers"] += 1
        if np.abs(ModifiedZScore(row["'K'"], Medians["K A"], KMADA)) > ModifiedZScoreLimit:
            # print("Spike detected in the A Drift calculation of the Potassium Sensor: Modified Z Score = " + str(ModifiedZScore(row["'K'"], Medians["K A"], KMADA)))
            Outliers["KADriftOutliers"] += 1
        if np.abs(ModifiedZScore(row["'Ca'"], Medians["Ca A"], CaMADA)) > ModifiedZScoreLimit:
            # print("Spike detected in the A Drift calculation of the Calcium Sensor: Modified Z Score = " + str(ModifiedZScore(row["'Ca'"], Medians["Ca A"], CaMADA)))
            Outliers["CaADriftOutliers"] += 1
        if np.abs(ModifiedZScore(row["'Cl'"], Medians["Cl A"], ClMADA)) > ModifiedZScoreLimit:
            # print("Spike detected in the A Drift calculation of the Chloride Sensor: Modified Z Score = " + str(ModifiedZScore(row["'Cl'"], Medians["Cl A"], ClMADA)))
            Outliers["ClADriftOutliers"] += 1

    for index, row in BDriftDF.iterrows():
        if np.abs(ModifiedZScore(row["'Na'"], Medians["Na B"], NaMADB)) > ModifiedZScoreLimit:
            # print("Spike detected in the B Drift calculation of the Sodium Sensor: Modified Z Score = " + str(ModifiedZScore(row["'Na'"], Medians["Na B"], NaMADB)))
            Outliers["NaBDriftOutliers"] += 1
        if np.abs(ModifiedZScore(row["'K'"], Medians["K B"], KMADB)) > ModifiedZScoreLimit:
            # print("Spike detected in the B Drift calculation of the Potassium Sensor: Modified Z Score = " + str(ModifiedZScore(row["'K'"], Medians["K B"], KMADB)))
            Outliers["KBDriftOutliers"] += 1
        if np.abs(ModifiedZScore(row["'Ca'"], Medians["Ca B"], CaMADB)) > ModifiedZScoreLimit:
            # print("Spike detected in the B Drift calculation of the Calcium Sensor: Modified Z Score = " + str(ModifiedZScore(row["'Ca'"], Medians["Ca B"], CaMADB)))
            Outliers["CaBDriftOutliers"] += 1
        if np.abs(ModifiedZScore(row["'Cl'"], Medians["Cl B"], ClMADB)) > ModifiedZScoreLimit:
            # print("Spike detected in the B Drift calculation of the Chloride Sensor: Modified Z Score = " + str(ModifiedZScore(row["'Cl'"], Medians["Cl B"], ClMADB)))
            Outliers["ClBDriftOutliers"] += 1

    for sensor in Outliers:
        # print(str(sensor) + " " + str(Outliers[sensor]))
        if Outliers[sensor] > SensorOutlierTrigger:
            SensorFailures += 1

    # Artificial Conditions, for now...
    if SensorFailures >= SensorsUntilFailure:
        detected = True
        print("Leak Signature Detected.")
    else:
        print("Leak Not Detected.")

    return detected


# Collects the needed information for the DelaminationCheck from the Dataframes.
def DelaminationCollect():
    SensorDF = DataFrames["Sensor"]

    BmV = SensorDF[SensorDF["'CalType'"] == "B"]
    BmVDataFrame = BmV[["'pO2'"]].reset_index(drop=True)
    BmVDataFrame = BmVDataFrame.drop(labels=0, axis=0)

    AmV = SensorDF[SensorDF["'CalType'"] == "A"]
    AmVDataFrame = AmV[["'pO2'"]].reset_index(drop=True)
    AmVDataFrame = AmVDataFrame.drop(labels=0, axis=0)

    TotalSeconds = SensorDF.iloc[:, 0]
    TotalSecondsSeries = TotalSeconds.reset_index(drop=True)
    TotalSecondsSeries = TotalSecondsSeries.drop(labels=0, axis=0)

    TotalSecondsInitial = TotalSecondsSeries.iloc[0]
    TotalSecondsInitial = TotalSecondsInitial[1:-5]
    TotalSecondsInitial = datetime.strptime(TotalSecondsInitial, "%m/%d/%y %H:%M:%S")
    TotalSecondsInitial = TotalSecondsInitial.timestamp()

    # very slow, pls fix (pandas has datetime objects, look into pandas built in functions
    # (pandas time delta)
    for index, row in TotalSecondsSeries.iteritems():
        PreDate = row[:][1:-5]
        Date = datetime.strptime(PreDate, "%m/%d/%y %H:%M:%S")
        TotalSecs = Date.timestamp() - TotalSecondsInitial
        TotalSecondsSeries = TotalSecondsSeries.replace(row, TotalSecs)

    # print(TotalSecondsSeries)

    CartDict["Delamination"]["AmV"] = AmVDataFrame
    CartDict["Delamination"]["BmV"] = BmVDataFrame
    CartDict["Delamination"]["Total Seconds"] = TotalSecondsSeries


def DelaminationCheck():
    detected = False
    CartAge = CartDict["General"]["Age"]

    PriorTwentyPercent = 0

    AmV = CartDict["Delamination"]["AmV"]
    BmV = CartDict["Delamination"]["BmV"]
    TotalSeconds = CartDict["Delamination"]["Total Seconds"]
    LastFiveAmV = AmV.tail(5)
    LastTenBmV = BmV.tail(10)

    LastFiveAmVPrior = pd.DataFrame()
    LastTenBmVPrior = pd.DataFrame()

    if CartAge >= 500 * 60 * 60:
        PriorTwentyPercent = 400 * 60 * 60
    else:
        PriorTwentyPercent = CartAge * 0.8

    for (AmV, row1), (TotalSeconds, row2) in zip(AmV.iteritems(), TotalSeconds.iteritems()):
        if len(LastFiveAmVPrior) != 5 and row2[:] >= PriorTwentyPercent:
            LastFiveAmVPrior.append(row1[:])

    for (BmV, row1), (TotalSeconds, row2) in zip(BmV.iteritems(), TotalSeconds.iteritems()):
        if len(LastTenBmVPrior) != 10 and row2[:] >= PriorTwentyPercent:
            LastTenBmVPrior.append(row1[:])

    if LastFiveAmV.mean() >= LastFiveAmVPrior.mean() * 1.1 and LastTenBmV.mean() >= LastTenBmVPrior.mean * 1.1:
        detected = True

    if detected:
        print("Delamination Signature Detected.")
    else:
        print("Delamination Not Detected.")


# Collects the needed information for the StickySolenoidCheck from the Dataframes.
def StickySolenoidCollect():
    SensorDF = DataFrames["Sensor"]


# Valves are not fully closing/opening when needed. This is seen in noisy soak patterns in CHART_EC_SAMP files.
# This file will only show up when a blood sample is run.
# When graphed, curves are not smooth, steps are discrete and bumpy.
def StickySolenoidCheck():
    detected = False
    return detected


# Collects the needed information for the BubblesCheck from the Dataframes.
def BubblesCollect():
    SensorDF = DataFrames["Sensor"]


# Air bubbles on the sensor membrane. This is seen in noisy soak patterns in CHART_EC_SAMP files.
# This file will only show up when a blood sample is run.
# When graphed, curves are generally not monotonic.
def BubblesCheck():
    detected = False
    return detected


if __name__ == '__main__':
    SelectCopyIL()
    MainParse()
    # print("Printing the Cartridge Dictionary...")
    # print(CartDict["Leaks"]["A Drift"])
    # print(" ")

    if file_reason.get(str(CartDict["General"]["Error Code"])) is not None:
        print(file_dict[str(CartDict["General"]["Error Code"])])
        print(file_reason[str(CartDict["General"]["Error Code"])])
    else:
        print(" ")
        print("Error code has no mapped reason.")
