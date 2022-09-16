from utils.json_load import *

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

# return the error message according to the error code
def Error_message_extract(error_code): 
    if error_code == 0:
        return 'No error message found through error code'
    else:
        return error_message[str(error_code)]