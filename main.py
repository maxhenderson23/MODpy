#This program takes two arguments
#First arguemnt: directory to input MOD files
#Second argument: directory to the 2011lumibyls.csv file
#The result is stored in event_list

#import modules
from collections import Counter
import csv
import time
import read_file
import sys
import os

#Initialise script run time
start_time = time.clock()

############################ INPUT FILES ############################

#Get the directories of all MOD files
input_directory = '/Users/mod/ProducedMOD/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000/' #sys.argv[1]
data_files = os.listdir(input_directory)

data_files_2011 = []

for data_file in data_files:
    if data_file.endswith(".mod"):
        data_files_2011.append(input_directory + data_file)

#Load good lumi block numbers
lumi_runs_and_blocks = read_file.read_lumi_runs_and_blocks('/Users/mod/Downloads/MODAnalyzer-prekshan-patch-1/2011lumibyls.csv')  #sys.argv[2])

############################ LOAD MOD FILES ############################

#Dictionary of MOD file directories, in each of which a list of each valid event's start and end line # is stored
valid_event_line_no_2011 = {}

for data_file in data_files_2011:
    valid_event_line_no_2011[data_file] = []
    
    raw_MOD_file = open(data_file)
    MOD_file = csv.reader(raw_MOD_file, delimiter=' ', skipinitialspace = 1)
    read_file.get_valid_line_no(MOD_file, valid_event_line_no_2011[data_file], lumi_runs_and_blocks)

#print(len(valid_event_line_no_2011[data_files_2011[0]]))

#Update data files with bad trigger events removed
for data_file in data_files_2011:
    raw_MOD_file = open(data_file)
    MOD_file = csv.reader(raw_MOD_file, delimiter=' ', skipinitialspace = 1)
    read_file.remove_bad_trigger_events(MOD_file, valid_event_line_no_2011[data_file])

#print(len(valid_event_line_no_2011[data_files_2011[0]]))


#Output final script run time
print('Script run time:',time.clock()-start_time,'seconds')
