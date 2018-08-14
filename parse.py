#This program takes two arguments
#First argument: directory to input MOD files
#First argument: directory to input .dat files
#Second argument (optional): total number of events to be processed
#The result is stored in event_list

#import modules
import csv
import time
import lumi
from analyze_MOD import analyze_MOD
import sys
import os

#Initialise start time
start_time = time.clock()

############################ INPUT FILES ############################

#Get the directories of all MOD files
input_directory = sys.argv[1]
try:
    output_directory = sys.argv[2]
except:
    output_directory = '../MODpy_output/'
    
data_files = os.listdir(input_directory)

MOD_files_2011 = []
dat_files_2011 = []

for data_file in data_files:
    if data_file.endswith(".mod"):
        MOD_files_2011.append(input_directory + data_file)
        dat_files_2011.append(output_directory + data_file.replace('.mod', '.dat'))

#Load good lumi block numbers
lumi_runs_and_blocks = lumi.read_lumi_runs_and_blocks("./2011lumibyls.csv")

#Limit the number of events to be processed
try:
    total_event_limit = int(sys.argv[3])
except:
    total_event_limit = -1
    
event_limit = total_event_limit

############################ ANALYZE MOD FILES ############################

#Analyzes MOD files and produces .dat files
for i in range(len(MOD_files_2011)):
    reader = csv.reader(open(MOD_files_2011[i]), delimiter=' ', skipinitialspace = 1)
    if os.path.exists(dat_files_2011[i]):
        os.remove(dat_files_2011[i])
    writer = csv.writer(open(dat_files_2011[i], 'w+'), delimiter=' ', quoting = csv.QUOTE_NONE, escapechar = ' ')
    event_limit -= analyze_MOD(reader, writer, lumi_runs_and_blocks, event_limit)

#Print files written and final script run time
for i in range(len(MOD_files_2011)):
    if i == 0:
        print('Wrote the files ' + dat_files_2011[i])
    else:
        print('                ' + dat_files_2011[i])
print('Script runtime:',time.clock() - start_time)