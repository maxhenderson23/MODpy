#This program takes one argument
#First arguemnt: directory to input MOD files
#The result is written in .dat file

#import modules
from collections import Counter
import csv
import time
import lumi
import sys
import os
import analyze_MOD


#Initialise script run time
start_time = time.clock()

############################ INPUT FILES ############################

#Get the directories of all MOD files
input_directory = sys.argv[1]
data_files = os.listdir(input_directory)

data_files_2011 = []

for data_file in data_files:
    if data_file.endswith(".mod"):
        data_files_2011.append(input_directory + data_file)
   
'''     
#Count all events in all mod files considered
count_all_events = 0
for data_file in data_files_2011:
    MOD_file = csv.reader(open(data_file), delimiter=' ', skipinitialspace = 1)
    for row in MOD_file:
        if row[0] == "BeginEvent":
           count_all_events += 1 
print(count_all_events)
'''

#Load good lumi block numbers
lumi_runs_and_blocks = lumi.read_lumi_runs_and_blocks('./2011lumibyls.csv')

############################ Analyzing and Writing into .dat Files ############################

for data_file in data_files_2011:
    MOD_file = csv.reader(open(data_file), delimiter=' ', skipinitialspace = 1)
    print("there are " + str(analyze_MOD.analyze_MOD(MOD_file, lumi_runs_and_blocks, 100000)) + "events in this MOD file")


#Output final script run time
print('Script run time:',time.clock()-start_time,'seconds')
