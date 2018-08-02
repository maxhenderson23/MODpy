#This program takes two arguments
#First argument: directory to input MOD files
#Second argument (optional): total number of events to be processed
#The result is stored in event_list

#import modules
from collections import Counter
import csv
import time
import lumi
import trigger
import load_events
import plot
import sys
import os
import matplotlib.pyplot as pl

############################ INPUT FILES ############################

#Get the directories of all MOD files
input_directory = sys.argv[1]
data_files = os.listdir(input_directory)

data_files_2011 = []

for data_file in data_files:
    if data_file.endswith(".mod"):
        data_files_2011.append(input_directory + data_file)

#Load good lumi block numbers
lumi_runs_and_blocks = lumi.read_lumi_runs_and_blocks("./2011lumibyls.csv")

#Limit the number of events to be processed (intended method didnt work)
try:
    total_event_limit = int(sys.argv[2])
except:
    total_event_limit = -1

############################ LOAD VALID EVENT LINE NO AFTER LUMI ############################

#Dictionary of MOD file directories, the keys are directories, and values are lists of valid events in that directory
#total event count counts all events (including invalid event), and is used to calculate cross section
valid_event_line_no_2011 = {}
total_event_count = 0

for data_file in data_files_2011:
    valid_event_line_no_2011[data_file] = []
    
    raw_MOD_file = open(data_file)
    MOD_file = csv.reader(raw_MOD_file, delimiter=' ', skipinitialspace = 1)
    total_event_count += lumi.get_line_no_good_lumi(MOD_file, valid_event_line_no_2011[data_file], lumi_runs_and_blocks, total_event_limit - total_event_count)

############################ LOAD EVENTS INTO EVENT LIST ############################

event_list = []

load_events.load_valid_event_entries(valid_event_line_no_2011, event_list, "PFC", ["px", "total_px", "e", "total_e"])

############################ LOAD VALID EVENT LINE NO AFTER TRIGGER ############################

for data_file in data_files_2011:
    raw_MOD_file = open(data_file)
    MOD_file = csv.reader(raw_MOD_file, delimiter=' ', skipinitialspace = 1)
    valid_event_line_no_2011[data_file] = trigger.get_line_no_trigger_fired(MOD_file, valid_event_line_no_2011[data_file])

############################ LOAD EVENTS INTO EVENT LIST ############################

event_list_with_trigger = []

load_events.load_valid_event_entries(valid_event_line_no_2011, event_list_with_trigger, "PFC", ["px", "total_px", "e", "total_e"])

############################ PLOT ############################

pl.close('all')

plot.plot('Total Momentum components of Jets per Event Histogram', 'Total Momentum components of Jets per Event', [[event["total_px"] for event in event_list], [event["total_px"] for event in event_list_with_trigger]], ['$p_x$ before trigger', '$p_x$ after trigger'], ['Momenta Component Totals per Event $[GeV]$', 'Frequency density $[GeV^{-1}]$'], True)
plot.plot('Total Momentum components of Jets per Event Histogram', 'Total Momentum components of Jets per Event', [[event["total_e"] for event in event_list], [event["total_e"] for event in event_list_with_trigger]], ['$E$ before trigger', '$E$ after trigger'], ['Momenta Component Totals per Event $[GeV]$', 'Frequency density $[GeV^{-1}]$'], True)

