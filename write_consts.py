spacing = 30

consts_header = ['E', 'px', 'py', 'pz']

def write_consts_header(writer):
    
    consts_row = []
    
    for col in consts_header:
        consts_row.append(col)
        
        #add extra spaces up to a multiple of 2     
        extraspace = spacing - len(consts_row[-1])
        consts_row.append(' '*(int(extraspace/2) - 1))
    
    writer.writerow(consts_row)

def write_consts_event(writer, event):
    
    writer.writerow(['# MODpy_event, hardest_eta = ' + str(event.hardest_eta())])
    consts = event.hardest_consts()
    
    for consts_row in consts:
        spaced_row = []
    
        for i, col in enumerate(consts_row):
            spaced_row.append(str(col))
            
            # add extra spaces up to a multiple of 2 if not on the last entry
            if i < len(consts_row)-1:
                extraspace = spacing - len(spaced_row[-1])
                spaced_row.append(' '*(int(extraspace/2) - 1))
    
        writer.writerow(spaced_row)