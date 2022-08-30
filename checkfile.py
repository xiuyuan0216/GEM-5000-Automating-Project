import os
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 

def checkfile(path):
    if os.path.exists(path):
        return True 
    else:
        return False

path = "\\\sysdatprod1\\Cartridge Complaint Data\\GEM5000\\16010208\\000000000500139439\\000000000500139439_20210223_090023\\SENSOR.csv"
print(checkfile(path))