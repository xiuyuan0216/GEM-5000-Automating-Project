import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 

# check PSC-C error 
# parameter: data: sensor dataframe
# return: PSC-C message
def PSC_C_check(data):

    # extract pO2 sensor data of I-C type
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

    time_threshold = 0.02   # time threshold to differentiate two curves
    pivot = 0               # anchor point, for other points to compare with
    num_threshold = 3       # maximum number of consecutive points that are percent_threshold lower than pivot 
    current_num = 0         # current number of consecutive points that are percent_threshold lower than pivot
    first = True 
    detect_time = 0
    failure = False
    curr_time = 0 
    next_time = 0
    percent_threshold = 0.5 # maximum tolerable percent decrease compared to pivot

    for i in range(len(CartAge)-1):
        curr_time = CartAge[i]
        next_time = CartAge[i+1]

        # set the pivot as the lowest point of the first curve
        if first == True and next_time-curr_time>time_threshold: 
            first == False
            pivot = sensor[i]
            continue
        
        if next_time-curr_time>time_threshold:
            if sensor[i]>(1+percent_threshold)*pivot:
                # count one more point
                current_num+=1
            else:
                # find one normal point, set current_num to 0
                current_num = 0
        
        if current_num>num_threshold:
            detect_time = CartAge[i]
            failure = True
            break

    if failure == True:
        return "PSC-C Failure on pO2 detected at "+str(detect_time)
    else:
        return "No PSC-C Failure on pO2 sensor detected"


