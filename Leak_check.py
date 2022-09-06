import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 


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
def LeakCollect(SensorDF, CartDict):

    # Creates new condensed dataframe and stores into CartDict.
    ADrift = SensorDF[SensorDF["'CalType'"] == "'A-DRIFT'"]
    ADriftDataFrame = ADrift[["'Na'", "'K'", "'Ca'", "'Cl'"]].reset_index(drop=True)

    BDrift = SensorDF[SensorDF["'CalType'"] == "'B-DRIFT'"]
    BDriftDataFrame = BDrift[["'Na'", "'K'", "'Ca'", "'Cl'"]].reset_index(drop=True)

    CartDict["A Drift"] = ADriftDataFrame
    CartDict["B Drift"] = BDriftDataFrame


# Leaks will usually fail as pO2 iQM disabled messages, and sometimes PCSND too.
# Will usually present itself as significant spikes in B drift, and sometimes A drift too, on multiple sensors at the
# same time. Looking to use Modified Z-Score as an adjustable metric to detect outliers.

def Leak_check(SensorDF):
    CartDict = dict()
    global Medians
    Medians = dict()
    LeakCollect(SensorDF, CartDict)

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

    ADriftDF = CartDict["A Drift"]
    BDriftDF = CartDict["B Drift"]

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