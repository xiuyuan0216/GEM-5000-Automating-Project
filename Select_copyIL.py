import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
from tkinter import filedialog 
from pathlib import Path

def Select_copyIL():
    CopyIL = filedialog.askdirectory()
    CopyILPath = Path(CopyIL)
    return CopyILPath