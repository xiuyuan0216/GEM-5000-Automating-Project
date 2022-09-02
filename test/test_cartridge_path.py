import sys
sys.path.append('.')

from Select_copyIL import *
from Main_parse import *
from Sensor_parse import *
from Event_log_parse import *

copyIL = Select_copyIL()
sensor_path, event_log_path, cartridge_path = Main_parse(copyIL)
print(cartridge_path)

