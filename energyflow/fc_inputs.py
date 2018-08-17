import numpy as np
import csv

constsfiles = ['../../MODpy_output/000D4260-D23E-E311-A850-02163E008D77.consts',
               '../../MODpy_output/00E41BFD-D93E-E311-A91D-0025901D5DEC.consts']

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

# remove ignorable jets from dataset and convert to numpy array format in the correct dimensions
def refine_data(pre_X, pre_y, num_events):
    
    #find the event with the most constituents
    most_consts = 0
    
    for x in pre_X:
        if len(x) > most_consts:
            most_consts = len(x)
    
    #construct X and y in the correct shape
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

def load_fc_data(num_events=-1):
    
    event_count = -1
    X    = []
    etas = []
    
    #get data from consts files
    for file in constsfiles:
        reader = csv.reader(open(file), delimiter=' ', skipinitialspace=True)
        is_header = True
        
        for row in reader:
            
            #ignore_header
            if is_header:
                is_header = False
                continue
            
            #new event: record eta
            if row[0] == '#':
                event_count += 1
                etas.append(float(row[-1]))
                X.append([])
                continue
            
            X[-1].append([float(val) for val in row])
        
    if num_events == -1:
        num_events = event_count
        print('num_events set to ' + str(event_count))
    
    #get X,y in the correct form
    y = get_tags(etas)
    return refine_data(X, y, num_events)