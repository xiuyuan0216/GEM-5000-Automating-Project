import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from utils.json_load import *

# extract error code from event log dataframe of the specific cartridge
# parameter: event log dataframe of the specific cartridge
# return: error code
def Error_code_extract(event_log_relavant):
    for index, row in event_log_relavant.iterrows():
        try:
            if 'Cartridge removed' in row['Message']:
                messageSplit = row['Message'].split()

                # Grabs error code from event log message column
                cartErrorCode = messageSplit[2]
                cartErrorCode = cartErrorCode.rstrip(cartErrorCode[-1])
                if cartErrorCode in error_message.keys():
                    cartErrorCode = int(cartErrorCode)
                    return cartErrorCode
                else:
                    cartErrorCode = 0
                
            else:
                cartErrorCode = 0

        except IndexError:
            print('Index Error Detected.')
        except UnboundLocalError:
            print('Cartridge probably ejected almost immediately.')

    return cartErrorCode