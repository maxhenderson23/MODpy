#The first input argument is the directory to the .dat files
#The second input argument is the string of variable we want to plot
#The third arguments is the range (lower_bound,upper_bound), be sure to not leave empty space in between, will use default value if is "default_range"

import numpy as np
import matplotlib.pyplot as pl
import sys
import os
import lumi
from ast import literal_eval as make_tuple
from operator import add
import csv

default_range ={"hardest_pT": (-2000, 2000)}

def load_effective_lumi(effective_lumi_file_dir, data_files):
    data_file_list = [data_file.replace(".dat", ".mod") for data_file in data_files]
    total_effective_lumi = {"HLT_Jet30": 0.0, "HLT_Jet60": 0.0, "HLT_Jet80": 0.0, "HLT_Jet110": 0.0, "HLT_Jet150": 0.0, "HLT_Jet190": 0.0, "HLT_Jet240": 0.0, "HLT_Jet300": 0.0, "HLT_Jet370": 0.0}
    effective_lumi_file = csv.reader(open(effective_lumi_file_dir), delimiter=',')
    for row in effective_lumi_file:
        if len(row) == 3 and row[0] in data_file_list:
            total_effective_lumi[row[1]] += float(row[2])

    scaling_factors = {}
    for x in total_effective_lumi:
        scaling_factors[x] = 1.0/total_effective_lumi[x]
    return scaling_factors

def read_dat_to_list(effective_lumi_dic_for_DAT_file, DAT_file):
    var_list = []
    scale_list = []
    
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
            
            reading_zeroth_line = False
        else:
            var_list.append(float(row[var_index]))
            scale_list.append(scaling_factors[row[trigger_fired_index]])
    
    return (var_list, scale_list)

##################################################################################################################################################################################

input_directory = sys.argv[1]
data_files = os.listdir(input_directory)
data_files = [os.path.split(data_file)[1] for data_file in data_files if ".dat" in os.path.split(data_file)[1]]

var_name = sys.argv[2]

#Set up default values
var_range = default_range[var_name]

######################

#Read in input flag arguments 
for (i, arg) in enumerate(sys.argv):
    if arg[i] == "--range":
        try:
            var_range = make_tuple(arg[i+1])
        except:
            print("please enter valid range, 'default_range', or a tuple with two entries, do not put empty space in the tuple ")
            sys.exit()


scaling_factors = load_effective_lumi("./effective_luminosity_by_trigger.csv", data_files)

no_of_bins = 100
hist_data = []
bin_edges = []

for i in range(no_of_bins):
    hist_data.append(0.0)

for data_file in data_files:
    DAT_file = csv.reader(open(input_directory + data_file), delimiter=' ', skipinitialspace = 1)

    (var_list, scale_list) = read_dat_to_list(scaling_factors, DAT_file)
    print(var_list[:10], no_of_bins, var_range, scale_list[:10])
    (current_hist_data, bin_edges) = np.histogram(var_list, bins=no_of_bins, range = var_range, weights = scale_list)
    hist_data = list(map(add, current_hist_data, hist_data))

pl.plot((bin_edges[:-1] + bin_edges[1:])/2, hist_data, label='', color='r')
pl.yscale('log')
pl.legend(loc='best')
pl.grid()
pl.show()
