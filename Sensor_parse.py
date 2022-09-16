import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

# return sensor dataframe and cartridge serial number
def Sensor_parse(sensor_path):
    sensor_file = pd.read_csv(sensor_path, low_memory=False, header=None, names=list(range(65)))
    search = sensor_file.iloc[:,1].to_list()
    index = 0 
    while search[index]!="'CartAge'":
        index+=1
    sensor_file.columns = sensor_file.iloc[index,:]
    sensor_file = sensor_file.iloc[index+1:,:]
    sensor_file.reset_index()
    extract_CartSerialNo = sensor_file[sensor_file["'CartAge'"]== "'CartSerialNo'"]
    CartSerialNo = extract_CartSerialNo["'Hct'"]
    CartSerialNo = int(CartSerialNo)

    return sensor_file, CartSerialNo

