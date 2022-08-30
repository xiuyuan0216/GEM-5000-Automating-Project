import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import datetime

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


def DelaminationCheck(DataFrames, CartDict):
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
