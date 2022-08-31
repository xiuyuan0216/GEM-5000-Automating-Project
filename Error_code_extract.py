import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from utils.json_load import *


def Error_code_extract(event_log_relavant, SerialNo):
    for index, row in event_log_relavant.iterrows():
        try:
            if row['Cartridge S/N'] == SerialNo and 'Cartridge removed' in row['Message']:
                messageSplit = row['Message'].split()

                # Grabs error code from event log message column
                cartErrorCode = messageSplit[2]
                cartErrorCode = cartErrorCode.rstrip(cartErrorCode[-1])
                cartErrorCode = int(cartErrorCode)
                return cartErrorCode
                
            else:
                cartErrorCode = 0
                return cartErrorCode

        except IndexError:
            print('Index Error Detected.')
        except UnboundLocalError:
            print('Cartridge probably ejected almost immediately.')