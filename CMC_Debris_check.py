import numpy as np 
import pandas as pd 


def CMCDebrisCheck(path):
    data = pd.read_csv(path)

    # if the first row is not the header, search and set the correct header

    # select A-COOx in CalType, extract cartAge and tHbMeas from the table
    relavant_data = data[data["'CalType'"]=='A-COOx']
    relavant_data = relavant_data.dropna()
    CartAge = relavant_data["'CartAge'"].to_list()
    sensor = relavant_data["'tHbMeas'"].to_list()


    pivot = 0   # the first sensor data, used as a pivot for later data
    num_threshold = 3   # the threshold for CMC debris
    num = 0     # the number of consecutive abnormal point
    CMC_debris = False
    CMC_debris_detect_time = 0
    for i in range(len(sensor)):
        if i == 0:
            # set the pivot
            pivot = sensor[i]
        if sensor[i] < pivot*0.95:
            # count consecutive abnormal points
            num+=1
        else:
            # set num to zero if finding a normal point
            num = 0
        if num>num_threshold:
            CMC_debris = True
            CMC_debris_detect_time = CartAge[i]
            break

    if CMC_debris == True:
        print("CMC Debris detected at "+str(CMC_debris_detect_time))
    else:
        print("CMC Debris not detected")


path = "\\\sysdatprod1\\Cartridge Complaint Data\\GEM5000\\16020226\\000000000500112445\\000000000500112445_20210117_165952\\SENSOR.csv"
CMCDebrisCheck(path)