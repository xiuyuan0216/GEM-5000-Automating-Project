import sys
sys.path.append('.')

from Select_copyIL import *
from Main_parse import *
from Sensor_parse import *
from Event_log_parse import *

# test case for cartridge.csv parse

copyIL = Select_copyIL()
sensor_path, event_log_path, cartridge_path, chart_ec_samp = Main_parse(copyIL)
print(cartridge_path)

