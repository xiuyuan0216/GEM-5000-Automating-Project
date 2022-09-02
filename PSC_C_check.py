import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 

def PSC_C_check(data):

    relavant_data = data[data["'CalType'"]=="I-C"]
    features = ["'CartAge'","'pO2'"]
    table = relavant_data[features]
    table = table.dropna()

    CartAge = table["'CartAge'"]
    sensor = table["'pO2'"]
    CartAge = CartAge.astype(np.float32)
    sensor = sensor.astype(np.float32)
    CartAge = CartAge.to_list()
    sensor = sensor.to_list()

    time_threshold = 0.02
    pivot = 0 
    num_threshold = 3 
    current_num = 0 
    first = True 
    detect_time = 0
    failure = False
    curr_time = 0 
    next_time = 0
    percent_threshold = 0.5

    for i in range(len(CartAge)-1):
        curr_time = CartAge[i]
        next_time = CartAge[i+1]
        if first == True and next_time-curr_time>time_threshold: 
            first == False
            pivot = sensor[i]
            continue
        
        if next_time-curr_time>time_threshold:
            if sensor[i]>(1+percent_threshold)*pivot:
                current_num+=1
            else:
                current_num = 0
        
        if current_num>num_threshold:
            detect_time = CartAge[i]
            failure = True
            break

    if failure == True:
        print("PSC-C Failure on pO2 detected at "+str(detect_time))
    else:
        print("No PSC-C Failure on pO2 sensor detected")


