#The first input argument is the directory to the .dat files
#The second input argument is the string of variable we want to plot

import numpy as np
import matplotlib.pyplot as pl
import sys
import os

prescale_factors =  {"HLT_Jet30": 25000.0, "HLT_Jet60": 1000.0, "HLT_Jet80": 200.0, "HLT_Jet110": 60.0, "HLT_Jet150": 20.0, "HLT_Jet190": 1.0, "HLT_Jet240": 1.0, "HLT_Jet300": 1.0, "HLT_Jet370": 1.0}

list_of_colors = ['r', 'b', 'k']

input_directory = sys.argv[1]
data_files = os.listdir(input_directory)

var_name = sys.argv[2]

def read_dat_to_list(var_name):
    ds

def plot(name, title, list_of_data, list_of_labels, axis_labels, trigger_list, y_log = False):
    pl.figure(name)
    pl.title(title)

    hists = []
    for data in list_of_data:
        hists.append(np.histogram(data, bins=100, weights = [1.0/prescale_factors[trigger] for trigger in trigger_list]))

    for i, hist in enumerate(hists):
        pl.plot((hist[1][:-1] + hist[1][1:])/2, hist[0], label=list_of_labels[i], color=list_of_colors[i])

    pl.xlabel(axis_labels[0])
    pl.ylabel(axis_labels[1])
    if y_log:
        pl.yscale('log')
    pl.legend(loc='best')
    pl.grid()

    pl.show()
