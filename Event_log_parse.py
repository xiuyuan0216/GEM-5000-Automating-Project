import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

# return the event log dataframe of the specific cartridge
def Event_log_parse(event_log_path, CartSerialNo):
    event_log = pd.read_csv(event_log_path)
    event_log = event_log.dropna(subset=['Cartridge S/N'])
    event_log['Cartridge S/N'] = event_log['Cartridge S/N'].astype(int)
    event_log_relavant = event_log[event_log["Cartridge S/N"]==CartSerialNo]

    return event_log_relavant
