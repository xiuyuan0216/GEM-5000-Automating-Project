import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 

def Solenoid_and_bubbles_check(data):
    relavant_data = data[data["'CalType'"]=='S']
    sensors_list = ["'Na'","'K'","'Ca'","'BUN'","'Cl'","'pO2'","'pH'","'HCO3'","'Crea'","'Cr'","'Lac'","'Glu'"]
    for sen in sensors_list:
        features = ["'CartAge'",sen]
        table = relavant_data[features].dropna()
        CartAge = table["'CartAge'"]
        sensor = table[sen]
            
        CartAge = CartAge.astype(np.float32)
        sensor = sensor.astype(np.float32)
        CartAge = CartAge.to_list()
        sensor = sensor.to_list()

        solenoid = False
        bubbles = False 
        solenoid_detect_time = 0 
        curve_num = 0 
        bubble_num = 0 
        time_threshold = 0.02 
        curr = 0 
        nxt = 0 
        diff = 0 
        prev_diff = 0 
        curr_time = 0 
        nxt_time = 0 
        maxValue = -float('inf')
        maxPoint = 0
        minPoint = 0
        minValue = float('inf')
        startIndex = 0
        endIndex = 0
        new = True 
        average = 0 
        rmse = 0
        rmse_threshold = 1.0
        diff_threshold = 10 
        diff_num = 0

        if sen != "'pO2'" and sen != "'Glu'": 
            rmse_threshold = 1.0
        else:
            rmse_threshold = 2.0 

        for i in range(len(sensor)-1):
            if new == True:
                maxValue = -float('inf')
                minValue = float('inf')
                prev_diff = sensor[i+1] - sensor[i]
                startIndex = i 
                curve_num+=1 
                average = 0 
                rmse = 0
                new = False
                diff_num = 0
            
            curr = sensor[i]
            nxt = sensor[i+1]
            diff = nxt - curr 
            if ((diff>0 and prev_diff<0) or (diff<0 and prev_diff>0)) and abs(prev_diff-diff)>0.1:
                diff_num+=1
            
            prev_diff = diff

            if curr>maxValue:
                maxValue = curr 
                maxPoint = i 
            if curr<minValue: 
                minValue = curr 
                minPoint = i
            
            curr_time = CartAge[i]
            nxt_time = CartAge[i+1]

            if nxt_time-curr_time>time_threshold: 
                endIndex = i 
                new = True 
                if sensor[endIndex]>(minValue+(maxValue-minValue)/5) and sensor[endIndex] <(maxValue-(maxValue-minValue)/5) and ((maxPoint>(startIndex+(endIndex-startIndex)/3) and maxPoint<(endIndex-(endIndex-startIndex)/3)) or (minPoint>(startIndex+(endIndex-startIndex)/3) and minPoint<(endIndex-(endIndex-startIndex)/3))):
                    bubble_num+=1 
                    bubbles = True 
                if solenoid != True: 
                    y = sensor[startIndex:endIndex+1]
                    x = range(1,len(y)+1)
                    arr = np.polyfit(np.log(x),y,deg=1)
                    for j in range(len(x)):
                        average+=(y[j]-(arr[0]*np.log(x[j])+arr[1]))**2
                    rmse = np.sqrt(average/len(x))
                    if rmse > rmse_threshold and diff_num>diff_threshold:
                        solenoid_detect_time = CartAge[endIndex]
                        solenoid = True
        
        if solenoid == True:
            print("Sticky Solenoid detected on "+sen+" at "+str(solenoid_detect_time))
        else:
            print("No sticky solenoid detected on "+sen)
        if bubbles == True:
            print("Total number of bubbles detected on "+sen+": "+str(bubble_num))
            print("Total number of curves on "+sen+": "+str(curve_num))
            percent = bubble_num/curve_num*100
            print("Bubble percentage on "+sen+" {}%".format(percent))
        else:
            print("No bubble detected on "+sen)
        print("--------------------------")



        