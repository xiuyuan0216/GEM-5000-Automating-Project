import sys 
sys.path.append('.')

from Select_copyIL import *
from Main_parse import *
from Sensor_parse import *
from Event_log_parse import *
from Error_code_extract import *
from Error_message_extract import *

# test case for error message extract

copyIL = Select_copyIL()
sensor_path, event_log_path, cartridge_path, chart_ec_samp = Main_parse(copyIL)
sensor_file, serialNo = Sensor_parse(sensor_path)
event_log_relavant = Event_log_parse(event_log_path, serialNo)
error_code = Error_code_extract(event_log_relavant)
print(Error_message_extract(error_code))


