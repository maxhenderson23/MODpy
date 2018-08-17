#This is the file to produce data plot
#You will need the proper effective_luminosity_by_trigger.csv under MODpy folder with entries of .dat files to be processed
#You can put input in plot_input.csv under MODpy folder

import numpy as np
import matplotlib.pyplot as pl
import os
from operator import add
import csv
import math 

# default_range = {"hardest_pT": (0, 2000), "mul_pre_SD": (0, 100), "hardest_eta": (-5, 5), "hardest_phi": (0, 2*math.pi), "hardest_area": (0.68, 1.1)}
# default_title = {"hardest_pT": "hardest jet $p_T$", "mul_pre_SD": "mul. of the hardest jet", "hardest_eta": "hardest jet $\eta$", "hardest_phi": "hardest jet $\phi$", "hardest_area": "hardest jet area"}
# default_axis_labels = {"hardest_pT": ("hardest jet $p_T$ $[GeV]$", "diff. cross-section $[\mu b/GeV]$"), "mul_pre_SD": ("multiplicity", "diff. cross-section $[\mu b]$"), "hardest_eta": ("hardest jet $\eta$", "diff. cross-section $[\mu b]$"), "hardest_phi": ("hardest jet $\phi$", "diff. cross-section $[\mu b]$"), "hardest_area": ("hardest jet area", "diff. cross-section $[\mu b]$")}
get_symbol = {"hardest_pT": "$p_T^\mathrm{hardest\; jet}$", "jet_quality": "JQ", "hardest_eta": "$\eta^\mathrm{hardest\; jet}$"}
get_unit = {"hardest_pT": " GeV", "jet_quality": "", "hardest_eta": ""}

#This function load effective lumi info and calculate the weight to convert data count to diff. cross section, stored in scaling_factors
def load_effective_lumi(effective_lumi_file_dir, data_files):
    data_file_list = [data_file.replace(".dat", ".mod") for data_file in data_files]
    total_effective_lumi = {"HLT_Jet30": 0.0, "HLT_Jet60": 0.0, "HLT_Jet80": 0.0, "HLT_Jet110": 0.0, "HLT_Jet150": 0.0, "HLT_Jet190": 0.0, "HLT_Jet240": 0.0, "HLT_Jet300": 0.0, "HLT_Jet370": 0.0}
    effective_lumi_file = csv.reader(open(effective_lumi_file_dir), delimiter=',')
    
    #We look for effective lumi for each key, and add them up into total effective lumi
    for row in effective_lumi_file:
        if len(row) == 3:
            if row[0] in data_file_list:
                total_effective_lumi[row[1]] += float(row[2])

    print(total_effective_lumi)

    #We scale by inverse the total lumi
    scaling_factors = {}
    for x in total_effective_lumi:
        scaling_factors[x] = 1.0/total_effective_lumi[x]

    return scaling_factors

#This function produces a list of data values, and another list of scaling weights to scale from event count to diff. cross section
def read_dat_to_list(var_name, effective_lumi_dic_for_DAT_file, DAT_file, constraints):
    var_list = []
    scale_list = []
    column_keys = {}

    for row in DAT_file:
        if row[0]=="#":
            for i, key in enumerate(row[1:]):
                column_keys[key] = i
        else:
            constraints_satisfied = True
            for key in constraints:
                if not constraints[key][0] <= float(row[column_keys[key]]) <= constraints[key][1]:
                    constraints_satisfied = False
                    break
                ###PATCH for central forward splitting in eta
                if cen_forw == 1: #central
                    if not -0.8 <= float(row[column_keys["hardest_eta"]]) <= 0.8:
                        constraints_satisfied = False
                        break
                if cen_forw == 2: #forward
                    if -0.8 <= float(row[column_keys["hardest_eta"]]) <= 0.8:
                        constraints_satisfied = False
                        break
                ###PATCH end
            if constraints_satisfied:
                var_list.append(float(row[column_keys[var_name]]))
                scale_list.append(scaling_factors[row[column_keys["trigger_fired"]]])
    
    return (var_list, scale_list)

##################################################################################################################################################################################

eta_range_check_2point4 = False
hardest_pT_lower_bound = 0.0

#plot_data is a list of data to be plotted, which is a dic {<data directory>, <label>, <format>}
plot_data = []
# constraints is a dictionary of contraints, with ranges as entries
constraints ={}
plot_input = csv.reader(open("./plot_input.csv"), delimiter=',')
for row in plot_input:
    try:
        if row[0] == "Settings":
            var_name = row[1]
            plot_name = row[2]
            plot_title = row[3]
            x_axis = row[4]
            y_axis = row[5]
            x_range = (float(row[6].split(":")[0][1:]), float(row[6].split(":")[1][:-1]))
            no_of_bins = int(row[7])
            if row[8] == "True":
                y_scale_log = True
            else:
                y_scale_log = False
            for constraint in row[9:]:
                constraints[constraint.split(":")[0]] = (float(constraint.split(":")[1]), float(constraint.split(":")[2]))

        elif row[0] == "Data":
            plot_data.append({"dir":row[1], "label":row[2], "fmt":row[3]})
    except:
        pass

#######################################################################################################################################################

pl.figure(plot_name)
pl.title(plot_title)

###################################################################################################################
#PATCH for central(1)-forward(2) plotting
for cen_forw in [1,2]:
#PATCH end
    for data in plot_data:
        data_files = os.listdir(data["dir"])
        data_files = [os.path.split(data_file)[1] for data_file in data_files if ".dat" in os.path.split(data_file)[1]]
        
        scaling_factors = load_effective_lumi("./effective_luminosity_by_trigger.csv", data_files)
    
        hist_data = []
        bin_edges = []
        sum_squared_weights = []
        count = 0
    
        for i in range(no_of_bins):
            hist_data.append(0.0)
            sum_squared_weights.append(0.0)
        
        for data_file in data_files:
            DAT_file = csv.reader(open(data["dir"] + data_file), delimiter=' ', skipinitialspace = 1)
        
            (var_list, scale_list) = read_dat_to_list(var_name, scaling_factors, DAT_file, constraints)
            (current_hist_data, bin_edges) = np.histogram(var_list, bins=no_of_bins, range = x_range, weights = [x*no_of_bins/(x_range[1]-x_range[0]) for x in scale_list])
            hist_data = list(map(add, current_hist_data, hist_data))
            (current_sum_squared_weights, whatever) = np.histogram(var_list, bins=no_of_bins, range = x_range, weights = [(x*no_of_bins/(x_range[1]-x_range[0])) * (x*no_of_bins/(x_range[1]-x_range[0])) for x in scale_list])
            sum_squared_weights = list(map(add, sum_squared_weights, current_sum_squared_weights))
            count += len(var_list)
        
        ###PATCH for central forward splitting 
        if cen_forw == 1:
            pl.errorbar((bin_edges[:-1] + bin_edges[1:])/2, hist_data, yerr=np.sqrt(sum_squared_weights), label='central', fmt = 'r.')
        if cen_forw == 2:
            pl.errorbar((bin_edges[:-1] + bin_edges[1:])/2, hist_data, yerr=np.sqrt(sum_squared_weights), label='forward', fmt = 'b.')
        ###PATCH end, unhash subsequent line
        #pl.errorbar((bin_edges[:-1] + bin_edges[1:])/2, hist_data, yerr=np.sqrt(sum_squared_weights), label=data["label"], fmt = data["fmt"])
    
        print("the total cross section is " + str(sum(hist_data)*(x_range[1]-x_range[0])/no_of_bins))
        print("the number of events plotted for files in " + data["dir"] + " is " + str(count))
    
######################################################################################################################################################

def stringify_number(number):
    bound_for_float = 7.0
    if -bound_for_float<number<bound_for_float and number!=0.0:
        return str(number)
    return str(int(number))

pl.xlabel(x_axis)
pl.ylabel(y_axis)
if y_scale_log:
    pl.yscale('log')
pl.legend(loc='best')
constraint_text_horizontal_position = 0.94 - len(plot_data)*0.07
for key in constraints:
    constraint_text = get_symbol[key]
    if math.isinf(constraints[key][1]):
        if math.isinf(constraints[key][0]):
            continue
        else:
            constraint_text += "$\geq$" + stringify_number(constraints[key][0]) + get_unit[key]
    else:
        if not math.isinf(constraints[key][0]):
            constraint_text = stringify_number(constraints[key][0]) + get_unit[key] + "$\leq$" + constraint_text
        constraint_text += "$\leq$" + stringify_number(constraints[key][1]) + get_unit[key]
    pl.text(0.97, constraint_text_horizontal_position, constraint_text, horizontalalignment='right', transform=pl.gca().transAxes)
    constraint_text_horizontal_position -= 0.07
pl.grid()
pl.show()
