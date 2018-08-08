#The first input argument is the directory to the .dat files
#The second input argument is the string of variable we want to plot

import numpy as np
import matplotlib.pyplot as pl
import sys
import os
import lumi
from ast import literal_eval as make_tuple
from operator import add
import csv
import math 

default_range = {"hardest_pT": (0, 2000), "mul_pre_SD": (0, 100), "hardest_eta": (-5, 5), "hardest_phi": (0, 2*math.pi), "hardest_area": (0.68, 1.1)}
default_title = {"hardest_pT": "hardest jet $p_T$", "mul_pre_SD": "mul. of the hardest jet", "hardest_eta": "hardest jet $\eta$", "hardest_phi": "hardest jet $\phi$", "hardest_area": "hardest jet area"}
default_axis_labels = {"hardest_pT": ("hardest jet $p_T$ $[GeV]$", "diff. cross-section $[\mu b/GeV]$"), "mul_pre_SD": ("multiplicity", "diff. cross-section $[\mu b]$"), "hardest_eta": ("hardest jet $\eta$", "diff. cross-section $[\mu b]$"), "hardest_phi": ("hardest jet $\phi$", "diff. cross-section $[\mu b]$"), "hardest_area": ("hardest jet area", "diff. cross-section $[\mu b]$")}

prescale_factors = {"HLT_Jet30": 1, "HLT_Jet60": 1, "HLT_Jet80": 1, "HLT_Jet110": 1, "HLT_Jet150": 1, "HLT_Jet190": 1, "HLT_Jet240": 1, "HLT_Jet300": 1, "HLT_Jet370": 1}

def load_effective_lumi(effective_lumi_file_dir, data_files):
    data_file_list = [data_file.replace(".dat", ".mod") for data_file in data_files]
    total_effective_lumi = {"HLT_Jet30": 0.0, "HLT_Jet60": 0.0, "HLT_Jet80": 0.0, "HLT_Jet110": 0.0, "HLT_Jet150": 0.0, "HLT_Jet190": 0.0, "HLT_Jet240": 0.0, "HLT_Jet300": 0.0, "HLT_Jet370": 0.0}
    effective_lumi_file = csv.reader(open(effective_lumi_file_dir), delimiter=',')
    total_lumi = 0.0
    for row in effective_lumi_file:
        if len(row) == 3:
            if row[0] in data_file_list:
                total_effective_lumi[row[1]] += float(row[2])

    scaling_factors = {}
    for x in total_effective_lumi:
        scaling_factors[x] = 1.0/total_effective_lumi[x]
    return scaling_factors

def read_dat_to_list(effective_lumi_dic_for_DAT_file, DAT_file, eta_range_check_2point4):
    var_list = []
    scale_list = []
    prescale_list = []
    
    var_index = None
    trigger_fired_index = None
    
    reading_zeroth_line = True
    for row in DAT_file:
        if reading_zeroth_line:
            column_keys = row[1:]
            try:
                var_index = column_keys.index(var_name)
            except:
                print("invalid variable name, check if exit in every .dat file ")
                sys.exit()
            try:
                trigger_fired_index = column_keys.index("trigger_fired")
            except:
                print("cannot find 'trigger_fired' variable, check if exit in every .dat file ")
                sys.exit()
            try:
                hardest_eta_index = column_keys.index("hardest_eta")
            except:
                print("cannot find 'hardest_eta' variable, check if exit in every .dat file ")
                sys.exit()
            
            reading_zeroth_line = False
        elif (not eta_range_check_2point4) or -2.4<=float(row[hardest_eta_index])<=2.4:
            var_list.append(float(row[var_index]))
            scale_list.append(scaling_factors[row[trigger_fired_index]])
            prescale_list.append(prescale_factors[row[trigger_fired_index]])
    
    return (var_list, scale_list, prescale_list)

##################################################################################################################################################################################

input_directory = sys.argv[1]
data_files = os.listdir(input_directory)
data_files = [os.path.split(data_file)[1] for data_file in data_files if ".dat" in os.path.split(data_file)[1]]

var_name = sys.argv[2]

#Set up default values
var_range = default_range[var_name]
var_title = default_title[var_name]
var_x_label, var_y_label = default_axis_labels[var_name]
y_scale_log = True
with_error_bar = True
no_of_bins = 100
eta_range_check_2point4 = False
var_label = "2011 data"

######################

#Read in input flag arguments 
for (i, arg) in enumerate(sys.argv):
    if arg == "--range":
        try:
            var_range = make_tuple(sys.argv[i+1])
        except:
            print("please enter valid range, 'default_range', or a tuple with two entries, do not put empty space in the tuple ")
            sys.exit()
    elif arg == "--y_linear":
        y_scale_log = False
    elif arg == "--no_error_bar":
        with_error_bar = False
    elif arg == "--bins":
        try:
            no_of_bins = int(sys.argv[i+1])
        except:
            print("please enter valid number of bins")
            sys.exit()
    elif arg == "--eta_range_2.4":
        eta_range_check_2point4 = True


scaling_factors = load_effective_lumi("./effective_luminosity_by_trigger.csv", data_files)

hist_data = []
bin_edges = []
no_of_events_in_bins = []

for i in range(no_of_bins):
    hist_data.append(0.0)
    no_of_events_in_bins.append(0.0)

for data_file in data_files:
    DAT_file = csv.reader(open(input_directory + data_file), delimiter=' ', skipinitialspace = 1)

    (var_list, scale_list, prescale_list) = read_dat_to_list(scaling_factors, DAT_file, eta_range_check_2point4)
    (current_hist_data, bin_edges) = np.histogram(var_list, bins=no_of_bins, range = var_range, weights = [x*no_of_bins/(var_range[1]-var_range[0]) for x in scale_list])
    hist_data = list(map(add, current_hist_data, hist_data))
    (no_of_events_in_bins_for_current_MOD, whatever) = np.histogram(var_list, bins=no_of_bins, range = var_range, weights = prescale_list)
    no_of_events_in_bins = list(map(add, no_of_events_in_bins, no_of_events_in_bins_for_current_MOD))

print("there are " + str(int(sum(no_of_events_in_bins))) + " events ")

if eta_range_check_2point4:
    var_title += " with $|\eta|\leq2.4$"
pl.figure(var_title)
pl.title(var_title)
if with_error_bar:
    y_error = []
    for (sigma, n) in zip(hist_data, no_of_events_in_bins):
        if n <= 0.0:
            y_error.append(0.0)
        else:
            y_error.append(sigma/math.sqrt(n))
    
    pl.errorbar((bin_edges[:-1] + bin_edges[1:])/2, hist_data, yerr=y_error, label=var_label,fmt = 'r.')
else:
    pl.plot((bin_edges[:-1] + bin_edges[1:])/2, hist_data, label=var_label, color='r')
pl.xlabel(var_x_label)
pl.ylabel(var_y_label)
if y_scale_log:
    pl.yscale('log')
pl.legend(loc='best')
pl.grid()
pl.show()
