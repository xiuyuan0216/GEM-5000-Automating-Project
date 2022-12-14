import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os 

# go through the copyIL path, find path of sensor, event_log, cartridge, chart_ec_samp file
def Main_parse(copyILPath):
    sensor_path =''
    event_log_path = ''
    cartridge_path = ''
    chart_ec_samp = ''
    for root, dirs, files in os.walk(copyILPath):
        if 'SENSOR.csv' in files:
            sensor_path = os.path.join(root, 'SENSOR.csv')
        if 'EVENT_LOG.CSV' in files:
            event_log_path = os.path.join(root, 'EVENT_LOG.CSV')
        if 'cartridge.csv' in files:
            cartridge_path = os.path.join(root, 'cartridge.csv')
        if 'CHART_EC_SAMP.csv' in files:
            chart_ec_samp = os.path.join(root, 'CHART_EC_SAMP.csv')
    return sensor_path, event_log_path, cartridge_path, chart_ec_samp