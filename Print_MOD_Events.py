#Print MOD file events
import csv
import sys

#Input MOD file as argument
MOD = sys.argv[1]

reader_mod = csv.reader(open(MOD), delimiter=' ', skipinitialspace = 1)

#Range of events in input MOD file to print
events_to_print = range(4972,4978)

event_counter = 0
row = next(reader_mod) 
row_counter = 1

#Loop through MOD file rows, print selected events
while True:
    if row[0] == 'BeginEvent':
        event_counter += 1
        if event_counter in events_to_print:
            print('Event#:',event_counter)
            while row[0] != 'EndEvent':
                print(row)
                row = next(reader_mod)
                row_counter += 1
    row = next(reader_mod)
    row_counter += 1
                   