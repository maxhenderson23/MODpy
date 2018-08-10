#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 12:37:54 2018

@author: mod
"""

#Dat file length checker
import csv
import os
import sys

#Input dat files
Dat1 = sys.argv[1]
Dat2 = sys.argv[2]

#Count events in both dat files
counter1 = 0
reader1 = csv.reader(open(Dat1), delimiter=' ', skipinitialspace = 1)
for row in reader1:
    if row[0] == 'Entry':
        counter1 += 1
        
counter2 = 0
reader2 = csv.reader(open(Dat2), delimiter=' ', skipinitialspace = 1)
for row in reader2:
    if row[0] == 'Entry':
        counter2 += 1

#Print counters
print('# Events in dat file 1: ',counter1)
print('# Events in dat file 2: ',counter2)
      