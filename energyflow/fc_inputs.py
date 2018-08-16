import numpy as np
import csv

constsfile = '../../MODpy_output/000D4260-D23E-E311-A850-02163E008D77.consts'

# return the tag 0 for a central jet, 1 for a forwards jet
def get_tags(etas):
    
    y = []
    
    for eta in etas:
        abs_eta = np.abs(eta)
    
        # central event
        if abs_eta < 0.8: 
            y.append(0)
        
        # forwards event
        elif abs_eta < 2.4:
            y.append(1)
        
        # ignorable event
        else:
            y.append(-1)
    
    return y

# remove ignorable jets from dataset and convert to linear algebra format
def refine_data(pre_X, pre_y, num_events):
    
    #find the event with the most constituents
    most_consts = 0
    
    for x in pre_X:
        if len(x) > most_consts:
            most_consts = len(x)
    
    #
    new_X = np.empty((num_events, most_consts, 4))
    new_y = np.empty((num_events), dtype=bool)
    
    event_count = 0
    
    for tag in pre_y:
        if tag != -1:
            new_X[event_count][0:len(pre_X[event_count])] = np.array(pre_X[event_count][:])
            new_y[event_count] = tag
        
        event_count += 1
        if event_count == num_events:
            break
    
    return [new_X, new_y]

def load_fc_data(num_events):
    reader = csv.reader(open(constsfile), delimiter=' ', skipinitialspace=True)
    event_count = -1
    
    X    = []
    etas = []
    
    for row in reader:
        
        #new event: record eta
        if row[0] == '#':
            event_count += 1
            etas.append(float(row[-1]))
            X.append([])
            continue
        
        #ignore_header
        if event_count == -1:
            continue
        
        X[-1].append([float(val) for val in row])
    
    print(event_count)
    
    y = get_tags(etas)
    return refine_data(X, y, num_events)