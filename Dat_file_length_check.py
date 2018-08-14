#Check length of .dat files - crosschecking mechanism to dat files between MODAnalyzer and MODpyAnalyser
#Dat file length checker
import csv
import sys

#Input dat files
Dat1 = sys.argv[1]
Dat2 = sys.argv[2]

#Count events in both dat files
counter1 = 0
reader1 = csv.reader(open(Dat1), delimiter=' ', skipinitialspace = 1)
for row in reader1:
    if row[0] == 'Entry' or row[0] == 'MODpy_entry':
        counter1 += 1
        
counter2 = 0
reader2 = csv.reader(open(Dat2), delimiter=' ', skipinitialspace = 1)
for row in reader2:
    if row[0] == 'Entry' or row[0] == 'MODpy_entry':
        counter2 += 1

#Print counters
print('# Events in dat file 1: ',counter1)
print('# Events in dat file 2: ',counter2)

#Direct checks: output first different event jet between dat files if theres a difference in length      
if counter1 != counter2:
    reader1 = csv.reader(open(Dat1), delimiter=' ', skipinitialspace = 1)
    reader2 = csv.reader(open(Dat2), delimiter=' ', skipinitialspace = 1)
    countera = 0
    counterb = 0
    new_disagreeing_rows = [[],[]]
    while True:
        row_a = next(reader1)
        countera += 1
        row_b = next(reader2) 
        counterb += 1
        
        while row_a[0] != 'Entry' and row_a[0] != 'MODpy_entry':
               row_a = next(reader1)
               countera += 1 
        while row_b[0] != 'Entry' and row_b[0] != 'MODpy_entry':
               row_b = next(reader2)
               counterb += 1
               
        #Compare prescale, mul_pre_sd, trigger_fired
        if abs(float(row_a[1])-float(row_b[1])) > 0.0001 or abs(float(row_a[3])-float(row_b[3])) > 0.0001 or row_a[10] != row_b[10]:
           #append and then print disagreeing rows
           new_disagreeing_rows[0].append(row_a) 
           new_disagreeing_rows[1].append(row_b) 
           break
       
    print(countera,counterb)
    print(new_disagreeing_rows[0])
    print(new_disagreeing_rows[1])
    
       
       
       
       
       
       
       
       
       