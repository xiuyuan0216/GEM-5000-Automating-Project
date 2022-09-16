import sys 
sys.path.append('.')

import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

from Select_copyIL import *
from Main_parse import *
from Sensor_parse import *
from Event_log_parse import *
from IQM_check import *

# test case for IQM check

copyIL = Select_copyIL()
sensor_path, event_log_path, cartridge_path, chart_ec_samp = Main_parse(copyIL)
sensor_file, serialNo = Sensor_parse(sensor_path)
event_log_relavant = Event_log_parse(event_log_path, serialNo)
IQM_check(sensor_file, event_log_relavant, serialNo)


