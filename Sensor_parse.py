import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

def Sensor_parse(sensor_path):
    sensor_file = pd.read_csv(sensor_path)
    if sensor_file.columns[1] != "'CartAge'":
        search = sensor_file.iloc[:,1].to_list()
        index = 0 
        while search[index]!="'CartAge'":
            index+=1
        sensor_file.columns = sensor_file.iloc[index,:]
        sensor_file = sensor_file.iloc[index+1,:]
    
    extract_CartSerialNo = sensor_file[sensor_file["'CartAge'"]== "'CartSerialNo'"]
    CartSerialNo = extract_CartSerialNo["'Hct'"]
    CartSerialNo = int(CartSerialNo)

    return sensor_file, CartSerialNo

