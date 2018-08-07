import csv
import numpy as np
import copy

#This function returns a list of events trat passed the trigger check
#Each event is in the format [event_start_line_no, event_end_line_no, trigger_string_without_version_no]
def get_line_no_trigger_fired(MOD_file, line_no_list):
    """ Inputs: each MOD_file and the list of good events line numbers
        Outputs: the updated list with bad trigger events and those whose hardest jet don't satsfy the JQC removed
        """
    #Initialize the new line_no_list
    #We rewrite the list to avoid confusion when removing directly from the loop
    line_no_list_trigger_fired = []
    
    #Initialise csv reader at zeroth line with index i=-1
    i = -1
    row = []
    
    #Dictionary of trigger ranges, s.t. key=trigger label, entry=true cut-off range squared
    squared_trigger_ranges = {"default":0., "HLT_Jet30":900., "HLT_Jet60":8100., "HLT_Jet80":12100., "HLT_Jet110":22500., "HLT_Jet150":44100., "HLT_Jet190":72900., "HLT_Jet240":96100., "HLT_Jet300":152100., "HLT_Jet370":230400.}
    
    #Loop through all listed events in MOD_file
    for (idx, event) in enumerate(line_no_list):
        if idx%1000 == 0 and i>0:
            print("Checking trigger for event # " + str(idx))
        
        #Create a list to store the hardest jet data for each event, to allow comparison with the JQC
        Hardest_Jet_row = []
        
        trigger = ["default", 1.] #Initialise event max trigger arbitrarily, with format: [Trigger label, Composite Prescale factor]
        max_pT_squared = 0.
        
        #Iterate to the first line of current event
        #The iterator is increased at the end of iterator, so that
        #when the while loop is broken, we are at the line number ? for "while i < ?" as written in the while condition
        while i < event[0]:
            #Potential body text

            (i, row) = next_MOD_file(i, MOD_file) #End of iteration
        #The loop end with i = event[0] and row at event[0]
        
        #Loop through lines of this event where the header is "Trig"
        #If there is no trigger for this event, the loop will run to the end of event with trigger still at inital value
        #We will be at the first line where row[0] != "Trig" when we break the loop
        header_is_Trig = False
        while i < event[1]:
            
            if row[0] == "Trig":
                header_is_Trig = True
                trigger_title = row[1].rpartition('_')[0]
                if trigger_title in squared_trigger_ranges and row[4] == "1": #Only consider HLT_Jet trigger types that have fired
                    if squared_trigger_ranges[trigger_title] > squared_trigger_ranges[trigger[0]]: #Only update if trigger cut-off is larger than current cut-off in consideration
                        trigger = [trigger_title, float(row[2])*float(row[3])]
            elif header_is_Trig == True:
                break
            
            (i, row) = next_MOD_file(i, MOD_file) #End of iteration

        #Loop through lines of this event where the header is "AK5"
        #If there is no trigger for this event, the loop will run to the end of event with max pT squared still at inital value
        if trigger[0] != "default": #Only check AK5 when a trigger is fired
            header_is_AK5 = False
            while i < event[1]:
                
                if row[0] == "AK5":
                    header_is_AK5 = True
                    current_pT_squared = (float(row[1])**2 + float(row[2])**2)*float(row[5])**2 #Scale p_T by the JEC factor
                    if current_pT_squared > max_pT_squared: #Find max Jet transverse momentum (only updating max if next jets value is larger than current)
                        max_pT_squared = current_pT_squared
                        Hardest_Jet_row = copy.deepcopy(row)
                elif header_is_AK5 == True:
                    break
                
                (i, row) = next_MOD_file(i, MOD_file) #End of iteration

        #Only record event with a trigger fired and that trigger matches the max pT
        #Recording a list of [event_start_line_no, event_end_line_no, trigger_string_without_version_no]
        if trigger[0] != "default" and max_pT_squared != 0.:
    
            #Find trigger range for max pt and check if the hardest trigger fired matches
            if squared_trigger_ranges[trigger[0]] <= max_pT_squared:
                #apply 'loose' JQC to the hardest Jet, and only accept events whose hardest jet satisfies them
                if float(Hardest_Jet_row[7]) > 1. and float(Hardest_Jet_row[8]) > 0. and float(Hardest_Jet_row[9]) < 0.99 and float(Hardest_Jet_row[10]) < 0.99 and float(Hardest_Jet_row[11]) > 0. and float(Hardest_Jet_row[12]) < 0.99:
                    line_no_list_trigger_fired.append([event[0], event[1], trigger[0]]) #Adding event to list if creteria are satisfied
                        
                        
    return line_no_list_trigger_fired

def next_MOD_file(i, MOD_file):
    return (i+1, next(MOD_file))
