import csv
import copy
import lumi

#Read in line numbers (<start>, <end>) of good events into line_no_list
def analyze_MOD(MOD_file, lumi_runs_and_blocks, total_event_limit):
    good_event = True
    count = 0
    section_name = ''
    
    #Dictionary of trigger ranges, s.t. key=trigger label, entry=true cut-off range squared
    squared_trigger_ranges = {"default":0., "HLT_Jet30":900., "HLT_Jet60":8100., "HLT_Jet80":12100., "HLT_Jet110":22500., "HLT_Jet150":44100., "HLT_Jet190":72900., "HLT_Jet240":96100., "HLT_Jet300":152100., "HLT_Jet370":230400.}
    
    #initialize the parameters for the current event
    #AK5 jets are stored as a list of strings, the same format read from the MOD file, appending its pT squared as the last entry, which is NOT a string (a float instead)
    def init_event_vars():
        return (["default", 0.0], ["default", 0.0], [], 1.0, 1.0, -1, "default")
    #to use this function, copy the next line
    current_hardest_AK5, current_second_AK5, current_jets, current_prescale, current_jec, current_jet_quality, current_trigger_fired = init_event_vars()
    
    write_dat_header(datfile)
    
    for row in MOD_file:
        
        if section_name == "Cond":
            if lumi.search_lumi((row[1], row[3]), lumi_runs_and_blocks):
                good_event = True
                current_hardest_AK5, current_second_AK5, current_jets, current_prescale, current_jec, current_jet_quality, current_trigger_fired = init_event_vars()
            else:
                good_event = False
            continue
        
        if not good_event:
            continue
        
        if row[0] == '#':
            #If no trigger is fired, this event is bad
            if section_name == "Trig":
                if current_trigger_fired == "default":
                    good_event = False
                    continue
            elif section_name == "AK5":
                #If trigger condition is not satisfied, this event is bad
                if squared_trigger_ranges[current_trigger_fired] > current_hardest_AK5[-1]:
                    good_event = False
                    continue
                #apply 'loose' JQC to the hardest Jet, and reject the event if any of the followings are the case
                if float(Hardest_Jet_row[7]) <= 1. or float(Hardest_Jet_row[8]) <= 0. or float(Hardest_Jet_row[9]) >= 0.99 or float(Hardest_Jet_row[10]) >= 0.99 or float(Hardest_Jet_row[11]) <= 0. or float(Hardest_Jet_row[12]) >= 0.99:
                    good_event = False
                    continue
            section_name = row[1]
            continue
        
        if section_name == "Trig":
            trigger_title = row[1].rpartition('_')[0]
            if trigger_title in squared_trigger_ranges and row[4] == "1": #Only consider HLT_Jet trigger types that have fired
                if squared_trigger_ranges[trigger_title] > squared_trigger_ranges[current_trigger_fired[0]]: #Only update if trigger cut-off is larger than current cut-off in consideration
                    current_trigger_fired, current_prescale = (trigger_title, float(row[2])*float(row[3]))
            continue

        if row[0] == "AK5":
            #We compared the current AK5 jet's pT to the largest and second
            pT_squared_for_this_AK5 = (float(row[1])**2 + float(row[2])**2)*(float(row[5])**2)
            if pT_squared_for_this_AK5 > current_hardest_AK5[-1]:
                current_second_AK5 = copy.deepcopy(current_hardest_AK5)
                current_hardest_AK5 = copy.deepcopy(row).append(pT_squared_for_this_AK5)
            elif pT_squared_for_this_AK5 > current_second_AK5[-1]:
                current_second_AK5 = copy.deepcopy(row).append(pT_squared_for_this_AK5)
            continue

        
        if row[0] == "EndEvent":
            line_no_list.append((event_start_line_no, MOD_file.line_num))
            count += 1
            if count == total_event_limit:
                break
            if count%1000 == 0 and count>0:
                print("writing event No. " + str(count)+" and the line # is (" + str(line_no_list[-1][0]) + ", " + str(line_no_list[-1][1]) + ")")
            
            event = Event(current_jets, current_prescale, current_jec, current_jet_quality, current_trigger_fired)
            write_dat_event(datfile, event)
            
            continue
        
        if row[0] == "PFC":

