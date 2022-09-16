import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from collections import deque


# Collects the needed information for the PeroxideExposureCheck from the Dataframes.
def Peroxide_Exposure_Collect(DataFrames, CartDict):
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
def Peroxide_Exposure_check(SensorDF):
    BmV = SensorDF[SensorDF["'CalType'"] == "B"]
    BmVDataFrame = BmV[["'Crea'", "'Cr'", "'Lac'", "'Glu'"]].reset_index(drop=True)
    BmVDataFrame = BmVDataFrame.drop(labels=0, axis=0)

    BDrift = SensorDF[SensorDF["'CalType'"] == "'B-DRIFT'"]
    BDriftDataFrame = BDrift[["'Crea'", "'Cr'", "'Lac'", "'Glu'"]].reset_index(drop=True)

    CartDict = dict()
    CartDict["BmV"] = BmVDataFrame
    CartDict["B Drift"] = BDriftDataFrame

    detected = False
    RollingQueue = deque()

    BDF = CartDict["BmV"]
    BDriftDF = CartDict["B Drift"]

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
        return "Peroxide Exposure Signature Detected."
    else:
        return "Peroxide Exposure Not Detected."
