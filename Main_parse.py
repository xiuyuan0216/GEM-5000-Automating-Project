import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os 

def Main_parse(copyILPath):
    sensor_path =''
    event_log_path = ''
    for root, dirs, files in os.walk(copyILPath):
        if 'SENSOR.csv' in files:
            sensor_path = os.path.join(root, 'SENSOR.csv')
        if 'EVENT_LOG.CSV' in files:
            event_log_path = os.path.join(root, 'EVENT_LOG.CSV')
    return sensor_path, event_log_path