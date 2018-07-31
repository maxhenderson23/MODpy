import csv
import numpy as np

def remove_bad_trigger_events(MOD_file, line_no_list):
    """ Inputs: each MOD_file and the list of good events line numbers
        Outputs: the updated list with bad trigger events removed
        """
    #Initialise csv reader at first line
    next(MOD_file)
    Current_line = 0
    
    #Dictionary of trigger ranges, s.t. key=trigger label, entry=true cut-off range squared
    Trigger_ranges = {30.:900.,60.:8100.,80.:12100.,110.:22500.,150.:44100.,190.:72900.,240.:96100.,300.:152100.,370.:230400.}
    
    #Loop through all listed events in MOD_file
    for event in line_no_list:
        Trigger = [0.,1.] #Initialise event max trigger arbitrarily, with format: [Trigger label, Composite Prescale factor]
        Max_pT_squared = 0.
        
        #Iterate to line before the first line of current event
        while Current_line < event[0]-1:
            next(MOD_file)
            Current_line += 1
    
        #Loop through lines of this event
        for line_no in range(event[0],event[1]+1):
            Line = next(MOD_file) #Read in current line to reduce multiple line calls
            Current_line += 1
            
            if Line[0] == "Trig" and len(Line[1]) <= 13 and Line[4] == 1:   #Only consider HLT_Jet trigger types that have fired
                if float(Line[1][7:-3]) > Trigger[0]:                       #Only update if trigger cut-off is larger than current cut-off in consideration
                    Trigger = [float(Line[1][7:-3]),float(Line[2])*float(Line[3])]
        
            elif Line[0] == "AK5":
                if Trigger == [0.,1.]: #If no triggers fired, remove event
                    line_no_list.remove(event)
                    break
                if np.sqrt(Line[1]**2+Line[2]**2) > Max_pT_squared: #Find max Jet transverse momentum (only updating max if next jets value is larger than current)
                    Max_pT_squared = np.sqrt(Line[1]**2+Line[2]**2)

        #Remove event if Maximum jet transverse momentum does not exceed the true trigger cut-off for the highest fired trigger label
        if Trigger[0] != 0.:
            if Max_pT_squared < Trigger_ranges[Trigger[0]]:
                line_no_list.remove(event)
    
    return ######Return the Prescale factor too?
