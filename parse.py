#This program takes two arguments
#First argument: directory to input MOD files
#Second argument (optional): total number of events to be processed
#The result is stored in event_list

#import modules
import time
import lumi
import analyze_MOD
import sys
import os

#Initialise start time
start_time = time.clock()

############################ INPUT FILES ############################

#Get the directories of all MOD files
input_directory = sys.argv[1] #'/Users/mod/ProducedMOD/eos/opendata/cms/Run2011A/Jet/MOD/12Oct2013-v1/20000/'
data_files = os.listdir(input_directory)

data_files_2011 = []

for data_file in data_files:
    if data_file.endswith(".mod"):
        data_files_2011.append(input_directory + data_file)

#Load good lumi block numbers
lumi_runs_and_blocks = lumi.read_lumi_runs_and_blocks("./2011lumibyls.csv")

#Limit the number of events to be processed
try:
    total_event_limit = int(sys.argv[2])
except:
    total_event_limit = -1

############################ ANALYZE MOD FILES ############################

#Analyzes MOD files and produces .dat files
for data_file in data_files_2011:
    analyze_MOD(open(data_file), lumi_runs_and_blocks, total_event_limit)

#Print final script run time
print('Script runtime:',time.clock() - start_time)