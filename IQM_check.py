import json 
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns

def IQMcheck(sensor_file_path, event_log_path):

    with open("json/limit_bound.json",'r') as file1:
        limit_bound = json.load(file1)

    with open("json/mapping.json",'r') as file2:
        mapping = json.load(file2)

    with open("json/slope_bound.json",'r') as file3:
        slope_bound = json.load(file3)

    sensor_file = pd.read_csv(sensor_file_path)

    if sensor_file.columns[1] != "'CartAge'":
        search = sensor_file.iloc[:,1].to_list()
        index = 0 
        while search[index]!="'CartAge'":
            index+=1
        sensor_file.columns = sensor_file.iloc[index,:]
        sensor_file = sensor_file.iloc[index+1,:]

    event_log = pd.read_csv(event_log_path)
    event_log = event_log.dropna(subset=['Cartridge S/N'])
    event_log['Cartridge S/N'] = event_log['Cartridge S/N'].astype(int)
    extract_CartSerialNo = sensor_file[sensor_file["'CartAge'"]== "'CartSerialNo'"]
    CartSerialNo = extract_CartSerialNo["'Hct'"]
    CartSerialNo = int(CartSerialNo)
    event_log_relavant = event_log[event_log["Cartridge S/N"]==CartSerialNo]


    messages = event_log_relavant['Message'].dropna().to_list()
    sensor_failure_messages = []

    for i in messages:
        if 'Sensor Disabled by iQM' in i: 
            sensor_failure_messages.append(i)

    sensor_failure = dict()
    for i in sensor_failure_messages: 
        temp = i.split(':')
        fail_type = temp[1]
        fail_substance = temp[2].split(',')
        sensor_failure[fail_type] = fail_substance
    
    columns = 2
    rows = 0
    for key in sensor_failure.keys():
        for value in sensor_failure[key]:
            if value in mapping.keys():
                rows+=1

    plot_num = 1
    
    plt.figure(figsize=(100,80))
    for type in sensor_failure.keys():
        for sensor in sensor_failure[type]:
            if sensor not in mapping.keys():
                continue

            caltype = "'"+type+"-DRIFT"+"'"
            meas = "'"+type+"-MEAS"+"'"
            sensor_file_relavant = sensor_file[sensor_file["'CalType'"] == caltype]
            sensor_file_meas = sensor_file[sensor_file["'CalType'"]==meas]
            sensor_name = mapping[sensor]
            sensor_real = "'"+sensor_name+"'"
            print(sensor_file_relavant.shape)
            sensor_file_relavant = sensor_file_relavant.dropna(subset=[sensor_real])
            errs = sensor_file[sensor_file["'CalType'"]=="'ERRS'"]

            index = 0
            for i, j in enumerate(errs[sensor_real].to_list()): 
                if j == "'IQMFAILED'": 
                    index = i
                    break

            timestamp = errs.iloc[index:index+1,0:1].values[0][0]
            cart_age = errs.iloc[index:index+1,1:2].values[0][0]
            age = sensor_file_relavant["'CartAge'"]
            sensor_data = sensor_file_relavant[sensor_real]
            age.reset_index(drop=True,inplace=True)
            sensor_data.reset_index(drop=True, inplace=True)
            sensor_data = sensor_data.astype(np.float32)
            age = age.astype(np.float32)

            sensor_meas = sensor_file_meas[sensor_real]
            sensor_meas.reset_index(drop=True, inplace=True)
            sensor_meas = sensor_meas.astype(np.float32)

            print("Sensor "+sensor_name+" Failed at Calibration Type "+caltype)
            print("Sensor Disabled time:"+timestamp)
            print("Sensor Disabled age:",cart_age,"hrs")
            print("Sensor data maximum value", sensor_data.max())
            print("Sensor data minimum value", sensor_data.min())
            print("-----------------------------------------")
            upper_limit = 0
            lower_limit = 0
            if type == "SLOPE":
                upper_limit = slope_bound[sensor_name][1]
                lower_limit = slope_bound[sensor_name][0]
            else:
                mapping_word = type+"-DRIFT"+"_"+sensor_name
                upper_limit = limit_bound[mapping_word][1]
                lower_limit = limit_bound[mapping_word][0]

    
            plt.subplot(rows,columns,plot_num)
            plot_num+=1
            sns.lineplot(x=age, y=sensor_data, label='Sensor Drift Data')
            plt.axhline(upper_limit, c='red',label="Limit bound")
            plt.axhline(lower_limit, c='red')
            cart_age = np.float32(cart_age)
            plt.axvline(cart_age, c='green', label='Sensor Disabled')
            #plt.text(cart_age, sensor_data.max(),'Sensor Disabled')
            #plt.legend(loc=1)
            title1 = "Sensor "+sensor_name+" "+caltype
            plt.title(title1)

            plt.subplot(rows, columns, plot_num)
            plot_num+=1
            sns.lineplot(x=age, y=sensor_meas, label='Sensor Meas Data')
            plt.axvline(cart_age, c='green', label='Sensor Disabled')
            #plt.text(cart_age, sensor_data.max(),'Sensor Disabled')
            #plt.legend(loc=1)
            title2 = "Sensor "+sensor_name+" "+meas
            plt.title(title2)

    plt.subplots_adjust(hspace=1, wspace=1)
    plt.show()

            
sensor_file_path = "\\\sysdatprod1\\Cartridge Complaint Data\\GEM5000\\16040283\\000000000500192713\\000000000500192713_20210904_064939\\SENSOR.csv"
event_log_path = "\\\sysdatprod1\\Cartridge Complaint Data\\GEM5000\\16040283\\000000000500192713\\000000000500192713_20210904_064939\\EVENT_LOG.csv"
IQMcheck(sensor_file_path, event_log_path)
    