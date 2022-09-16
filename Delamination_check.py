import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from datetime import datetime

# Collects the needed information for the DelaminationCheck from the Dataframes.
def DelaminationCollect(DataFrames, CartDict):
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


def Delamination_check(SensorDF, cartridge_path):
    CartridgeDF = pd.read_csv(cartridge_path, on_bad_lines='skip')
    CartAge = int(CartridgeDF.iloc[31, 4])
    CartDict = dict()
    detected = False

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
    PriorTwentyPercent = 0

    for index, row in TotalSecondsSeries.iteritems():
        PreDate = row[:][1:-5]
        Date = datetime.strptime(PreDate, "%m/%d/%y %H:%M:%S")
        TotalSecs = Date.timestamp() - TotalSecondsInitial
        TotalSecondsSeries = TotalSecondsSeries.replace(row, TotalSecs)

    # print(TotalSecondsSeries)

    CartDict["AmV"] = AmVDataFrame
    CartDict["BmV"] = BmVDataFrame
    CartDict["Total Seconds"] = TotalSecondsSeries

    AmV = CartDict["AmV"]
    BmV = CartDict["BmV"]
    TotalSeconds = CartDict["Total Seconds"]
    LastFiveAmV = AmV.iloc[AmV.shape[0]-5:AmV.shape[0], :]
    LastTenBmV = BmV.iloc[BmV.shape[0]-10:BmV.shape[0], :]
    LastTenBmVPrior = pd.DataFrame()
    LastFiveAmVPrior = pd.DataFrame()

    if CartAge >= 500 * 60 * 60:
        PriorTwentyPercent = 400 * 60 * 60
    else:
        PriorTwentyPercent = CartAge * 0.8

    for (AmV, row1), (TotalSeconds1, row2) in zip(AmVDataFrame.iteritems(), TotalSeconds.iteritems()):
        if len(LastFiveAmVPrior) != 5 and row2 >= PriorTwentyPercent:
            LastFiveAmVPrior.append(row1)

    for (BmV, row1), (TotalSeconds1, row2) in zip(BmVDataFrame.iteritems(), TotalSeconds.iteritems()):
        if len(LastTenBmVPrior) != 10 and row2 >= PriorTwentyPercent:
            LastTenBmVPrior.append(row1)
    LastFiveAmV = LastFiveAmV.reset_index()
    LastTenBmV = LastTenBmV.reset_index()
    LastFiveAmV = LastFiveAmV.astype(np.float32)
    LastTenBmV = LastTenBmV.astype(np.float32)
    LastFiveAmVPrior = LastFiveAmVPrior.astype(np.float32)
    LastTenBmVPrior = LastTenBmVPrior.astype(np.float32)

    LastFiveAmV = LastFiveAmV.iloc[:,1]
    LastTenBmV = LastTenBmV.iloc[:,1]
    LastFiveAmV_mean = LastFiveAmV.mean()
    LastTenBmV_mean = LastTenBmV.mean()

    if LastFiveAmVPrior.shape[0] == 0:
        LastFiveAmVPrior_mean = 0
    else:
        LastFiveAmVPrior = LastFiveAmVPrior.iloc[:,1]
        LastFiveAmVPrior_mean = LastFiveAmVPrior.mean()

    if LastTenBmVPrior.shape[0] == 0:
        LastTenBmVPrior_mean = 0
    else:
        LastTenBmVPrior = LastTenBmVPrior.iloc[:,1]
        LastTenBmVPrior_mean = LastFiveAmVPrior.mean()

    if (LastFiveAmV_mean > LastFiveAmVPrior_mean * 1.1) & (LastTenBmV_mean > LastTenBmVPrior_mean * 1.1):
        detected = True

    if detected:
        return "Delamination Signature Detected."
    else:
        return "Delamination Not Detected."
