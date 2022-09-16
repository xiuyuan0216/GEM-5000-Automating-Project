import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 

from Select_copyIL import *
from Sensor_parse import *
from Main_parse import *
from Event_log_parse import *
from CMC_Debris_check import *
from Delamination_check import *
from Error_code_extract import *
from Error_message_extract import *
from Error_reason_extract import *
from IQM_check import *
from Leak_check import *
from Peroxide_Exposure_check import *
from PSC_C_check import *
from Solenoid_and_bubbles_check import *

# general approach. After developing the web application, running this file will output nothing in the terminal

copyIL = Select_copyIL()
sensor_path, event_log_path, cartridge, chart_ec_samp = Main_parse(copyIL)
sensor_file, SerialNo = Sensor_parse(sensor_path)
event_log_relavant = Event_log_parse(event_log_path, SerialNo)
error_code = Error_code_extract(event_log_relavant)
message = Error_message_extract(error_code)
reason = Error_reason_extract(error_code)

print("Error code: "+str(error_code))
print("Error message: "+str(message))
print("Error reason: "+str(reason))
print("-------------------------------")

IQM_check(sensor_file, event_log_relavant, SerialNo)
print("-------------------------------")

Leak_check(sensor_file)
print("-------------------------------")

Peroxide_Exposure_check(sensor_file)
print("-------------------------------")

Solenoid_and_bubbles_check(chart_ec_samp)
print("-------------------------------")

PSC_C_check(sensor_file)
print("-------------------------------")

Delamination_check(sensor_file, cartridge)
print("-------------------------------")

CMC_Debris_check(sensor_file)
print("-------------------------------")