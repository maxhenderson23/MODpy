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

#This function returns a list of events trat passed the trigger check
#Each event is in the format [event_start_line_no, event_end_line_no, trigger_string_without_version_no] 
def get_line_no_trigger_fired(MOD_file, line_no_list):
    """ Inputs: each MOD_file and the list of good events line numbers
        Outputs: the updated list with bad trigger events removed
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
    for event in line_no_list:
        trigger = ["default", 1.] #Initialise event max trigger arbitrarily, with format: [Trigger label, Composite Prescale factor]
        max_pT_squared = 0.
        
        #Iterate to line until the first line of current event
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
                    current_pT_squared = float(row[1])**2 + float(row[2])**2
                    if current_pT_squared > max_pT_squared: #Find max Jet transverse momentum (only updating max if next jets value is larger than current)
                        max_pT_squared = current_pT_squared
                elif header_is_AK5 == True:
                    break

                (i, row) = next_MOD_file(i, MOD_file) #End of iteration 


        #Only record event with a trigger fired and that trigger matches the max pT
        #Recording a list of [event_start_line_no, event_end_line_no, trigger_string_without_version_no] 
        if trigger[0] != "default" and max_pT_squared != 0.:

            #Find trigger range for max pt and check if the hardest trigger fired matches 
            trigger_for_max_pT = "default"
            for key in squared_trigger_ranges:
                if squared_trigger_ranges[key] <= max_pT_squared and squared_trigger_ranges[key] > squared_trigger_ranges[trigger_for_max_pT]:
                    trigger_for_max_pT = key
            if trigger[0] == trigger_for_max_pT: 
                line_no_list_trigger_fired.append([event[0], event[1], trigger[0]]) #Adding event to list if creteria are satisfied

    line_no_list = line_no_list_trigger_fired 
    
    return 

def next_MOD_file(i, MOD_file):
    return (i+1, next(MOD_file))
