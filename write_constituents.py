spacing = 30

constituents_header = ['# MODpy_entry', 'E', 'px', 'py', 'pz']

def write_dat_header(writer):
    
    dat_row = []
    
    for col in dat_header:
        dat_row.append(col)
        
        #add extra spaces up to a multiple of 2     
        extraspace = spacing - len(dat_row[-1])
        dat_row.append(' '*(int(extraspace/2) - 1))
    
    writer.writerow(dat_row)

def write_dat_event(writer, event):
    
    dat_row = []
    
    for col in dat_header:
        if col == '# MODpy_entry':
            dat_row.append(' MODpy_entry')
        elif col == 'prescale':
            dat_row.append(str(event.prescale()))
        elif col == 'mul_pre_SD':
            dat_row.append(str(event.mul_pre_SD()))
        elif col == 'mass_pre_SD':
            dat_row.append(str(event.mass_pre_SD()))
        elif col == 'hardest_pT':
            dat_row.append(str(event.hardest_pT()))
        elif col == 'hardest_eta':
            dat_row.append(str(event.hardest_eta()))
        elif col == 'hardest_phi':
            dat_row.append(str(event.hardest_phi()))
        elif col == 'hardest_area':
            dat_row.append(str(event.hardest_area()))
        elif col == 'jec':
            dat_row.append(str(event.jec()))
        elif col == 'jet_quality':
            dat_row.append(str(event.jet_quality()))
        elif col == 'trigger_fired':
            dat_row.append(str(event.trigger_fired()))
        else:
            dat_row.append('nan')

        #add extra spaces up to a multiple of 2     
        extraspace = spacing - len(dat_row[-1])
        dat_row.append(' '*(int(extraspace/2) - 1))
    
    writer.writerow(dat_row)