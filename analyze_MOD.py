import copy
import lumi
import numpy as np
import fastjet as fj
from Event import Event
import write_dat

def analyze_MOD(MOD_file, dat_file, lumi_runs_and_blocks, event_limit):
    good_event = True
    count = 0
    valid_event_count = 0
    section_name = ''
    k = 1
    accepted_events_counter = 0
    
    #Define FastJet parameters, and the algorithm
    R = 0.5
    jet_def = fj.JetDefinition(fj.antikt_algorithm, R)

    #initialize the parameters for the current event
    '''AK5 jets stored as a list of strings corresponding to each entry of the row in the MOD file.
    The last entry is pT**2, saved as a floating point variable.'''
    
    def init_event_vars():
        return (["default", 0.0], ["default", 0.0], [], [], [], 1.0, -1, [])
    #to use this function, copy the next line
    current_hardest_AK5, current_second_AK5, Pseudojet_particles, current_jets, current_prescales, current_jec, current_jet_quality, current_triggers_fired = init_event_vars()

    #Write the .dat header
    write_dat.write_dat_header(dat_file)
    
    for row in MOD_file:
        
        if row[0] == "BeginEvent":
            good_event = True
            section_name = "BeginEvent"
            count += 1
            #Initialise dictionary of trigger ranges, s.t. key=trigger label, entry=true cut-off range squared ...no 300 trigger in initialisation
            squared_trigger_ranges = {"default":0., "HLT_Jet30":900., "HLT_Jet60":8100., "HLT_Jet80":12100., "HLT_Jet110":22500., "HLT_Jet150":44100., "HLT_Jet190":72900., "HLT_Jet240":96100., "HLT_Jet370":230400.} 

            #Provide commentary on every kth event
            if (count-1)%k == 0:
                print("starting to process event # " + str(count))
            continue
        
        if not good_event:
            continue
        
        if row[0] == '#' and not ".mod" in row[1]:
        
            #New section. First check that sections follow on in the correct order. Then perform checks on the data stored from the previous section.
            if section_name == "Trig":
                #Check that the AK5 section follows the Trig section
                if row[1] != "AK5":
                    good_event = False 
                    if (count-1)%k == 0:
                        print("no AK5s in mod file for this event, hence ignore event")
                    continue
                if len(current_triggers_fired) == 0:
                    good_event = False
                    if (count-1)%k == 0:
                        print("this event failed to fire any trigger, exiting event")
                    continue
                else:
                    if (count-1)%k == 0:
                        print("this event managed to fire some triggers, continue to process the event")
                        
            elif section_name == "AK5":
                #Check that the PFC section follows the AK5 section
                if row[1] != "PFC": 
                    good_event = False 
                    if (count-1)%k == 0:
                        print("no PFCs in mod file for this event, hence ignore event")
                    continue
                #If trigger condition is not satisfied, this event is bad
                highest_lower_trig_threshold = 0.
                for i in squared_trigger_ranges:
                    if squared_trigger_ranges[i] < current_hardest_AK5[-1]:
                        highest_lower_trig_threshold = i
                #Save the trigger equivalent to the current pT, and respective prescale
                if highest_lower_trig_threshold in current_triggers_fired:
                    Selected_trigger = highest_lower_trig_threshold                         
                    Selected_trigger_prescale = current_prescales[current_triggers_fired.index(highest_lower_trig_threshold)]
                if highest_lower_trig_threshold not in current_triggers_fired:
                    good_event = False
                    if count%k == 0 and count>0:
                        print("the hardest AK5 pT squared is " + str(current_hardest_AK5[-1]) + " and the trigger is " + highest_lower_trig_threshold + " with threshold " + str(squared_trigger_ranges[highest_lower_trig_threshold]))
                        print("the hardest AK5 (with JEC) is smaller than the trigger fired, hence this event is rejected, exiting event")
                    continue
                
                #Check that the hardest AK5 satisfies loose quality criteria
                elif float(current_hardest_AK5[7]) <= 1. or float(current_hardest_AK5[8]) <= 0. or float(current_hardest_AK5[9]) >= 0.99 or float(current_hardest_AK5[10]) >= 0.99 or float(current_hardest_AK5[11]) <= 0. or float(current_hardest_AK5[12]) >= 0.99:
                    good_event = False
                    if (count-1)%k == 0:
                        print("the hardest AK5 is ", current_hardest_AK5)
                        print("loose JQC failed, exiting event")
                    continue
                else:
                    #For jets that have passed loose quality criteria, check tight quality criteria
                    if float(current_hardest_AK5[7]) > 1. and float(current_hardest_AK5[8]) > 0. and float(current_hardest_AK5[9]) < 0.9 and float(current_hardest_AK5[10]) < 0.9 and float(current_hardest_AK5[11]) > 0. and float(current_hardest_AK5[12]) < 0.99:
                        current_jet_quality = 3
                        
                    #Check medium quality criteria
                    elif float(current_hardest_AK5[7]) > 1. and float(current_hardest_AK5[8]) > 0. and float(current_hardest_AK5[9]) < 0.95 and float(current_hardest_AK5[10]) < 0.95 and float(current_hardest_AK5[11]) > 0. and float(current_hardest_AK5[12]) < 0.99:
                        current_jet_quality = 2
                    else:
                        current_jet_quality = 1
                    if (count%k-1) == 0:
                        print("the hardest AK5 is ", current_hardest_AK5)
                        print("the current triggers are ",Selected_trigger)
                        print("trigger fired properly, loose JQC passed, jet quality set to 1, continue to process event")
            
            #Begin reading the new section
            section_name = row[1]
            if (count%k-1) == 0:
                print("beginning to read in section " + section_name)
            continue
        
        #Perform lumi checks for 2011 data and initialise new event
        if section_name == "Cond":
            if lumi.search_lumi((row[1], row[3]), lumi_runs_and_blocks):
                current_hardest_AK5, current_second_AK5, Pseudojet_particles, current_jets, current_prescales, current_jec, current_jet_quality, current_triggers_fired = init_event_vars()
                if count%k == 0 and count>0:
                    print("the event # " + str(count)+ " passed the check with lumi block (" + row[1] + ", " + row[3] + ")")
                continue
            else:
                good_event = False
                if (count%k-1) == 0:
                    print("this event does not exist in the good lumi block file, exiting event")
            continue
        
        #Update hardest trigger
        if section_name == "Trig":
            trigger_title = row[1].rpartition('_')[0]
            if trigger_title == 'HLT_Jet300': #If event has a 300 trigger, add it to the list of triggers to check
                squared_trigger_ranges["HLT_Jet300"] = 152100.
            if trigger_title in squared_trigger_ranges and row[4] == "1": #Save all HLT_Jet trigger types that have fired (and equivalent prescales)
                current_triggers_fired.append(trigger_title)
                current_prescales.append(float(row[2])*float(row[3]))
            continue

        #Update two hardest AK5s
        if row[0] == "AK5":
            pT_squared_for_this_AK5 = (float(row[1])**2 + float(row[2])**2)*(float(row[5])**2)
            if pT_squared_for_this_AK5 > current_hardest_AK5[-1]:
                current_second_AK5 = copy.deepcopy(current_hardest_AK5)
                current_hardest_AK5 = copy.deepcopy(row)
                current_hardest_AK5.append(pT_squared_for_this_AK5)
            elif pT_squared_for_this_AK5 > current_second_AK5[-1]:
                current_second_AK5 = copy.deepcopy(row)
                current_second_AK5.append(pT_squared_for_this_AK5)
            continue

        #Update list of PFC four-momenta
        if row[0] == "PFC":
            Pseudojet_particles.append(fj.PseudoJet(float(row[1]),float(row[2]),float(row[3]),float(row[4])))
            continue

        elif row[0] == "EndEvent":
            #Run Fastjet checks: create pseudo jets from PFCs, match with hardest AK5s
            fastjets = jet_def(Pseudojet_particles)
            fastjets_observables = [[j.px(),j.py(),j.pz(),j.e(),j.rap(),j.phi(),len(j.constituents())] for j in fastjets]
            matching_output = match_jets(current_hardest_AK5, current_second_AK5, fastjets_observables)
            
            #Check if jets have matched
            if matching_output[0] is False:
                good_event = False
                print('event rejected based on fastjet comparison')
                continue
            else:
                #Save two hardest jets
                FJ_hardest = fastjets[matching_output[1]]
                FJ_second_hardest = fastjets[matching_output[2]]

                event = Event([FJ_hardest, FJ_second_hardest], Selected_trigger_prescale, current_jec, current_jet_quality, Selected_trigger)
                write_dat.write_dat_event(dat_file, event)
                if count%k == 0 and count>0:
                    accepted_events_counter += 1
                    print("Event validated with fastjet, and written to .dat, event #: ",str(count),'accepted event #:',accepted_events_counter)
                    print('##############################################################')
            if valid_event_count == event_limit:
                break
            valid_event_count += 1
            continue
    
    return valid_event_count

#Function to match hardest 2 jets with fastjet jets
def match_jets(AK5_hardest,AK5_hardest2,pFJ):
    """ Function to check fastjet generated 2 hardest jets, match the AK5 two hardest jets in (rap,phi) multiplicity and 4-vector to within 1MeV
    Input 2 hardest AK5s, and list of Pseudojet clusters from fastjet
    Output True or False if there is a match, and the indices of the hardest fj jets if True"""
            
    #Define these 2 hardest jet rapidity and phi
    AK5_hardest_rap = np.arctanh(float(AK5_hardest[3])/float(AK5_hardest[4]))
    AK5_hardest_phi = np.arctan2(float(AK5_hardest[2]),float(AK5_hardest[1]))
    AK5_sechardest_rap = np.arctanh(float(AK5_hardest2[3])/float(AK5_hardest2[4]))
    AK5_sechardest_phi = np.arctan2(float(AK5_hardest2[2]),float(AK5_hardest2[1]))
 
    #Initialise with arbitrary high values
    min_delta_R_sq1 = 1000000.
    min_delta_R_sq2 = 1000000.
    min_delta_R_sq1_save2 = 1000000.
    fj_hardest_index = 0

    #Loop through all fj jets
    for fj_index in range(len(pFJ)):
        
        #Calculate the minimum azimuth difference between the current fj jet and AK5 hardest 2 jets
        phi1 = pFJ[fj_index][5]-AK5_hardest_phi
        phi2 = pFJ[fj_index][5]-AK5_sechardest_phi
        delta_phi1 = min([phi1,phi1+2*np.pi,phi1-2*np.pi],key=abs)
        delta_phi2 = min([phi2,phi2+2*np.pi,phi2-2*np.pi],key=abs)
        
        #Calculate the delR squared values to the hardest 2 AK5 jets
        current_delta_R_sq1 = (pFJ[fj_index][4]-AK5_hardest_rap)**2+delta_phi1**2
        current_delta_R_sq2 = (pFJ[fj_index][4]-AK5_sechardest_rap)**2+delta_phi2**2
        
        #Check if new delR1 is less than minimum, if so save it
        if current_delta_R_sq1 < min_delta_R_sq1:
            
            #If delR1 min is being updated, check to see if its old value could update the delR2 value, if so update it also with the old value
            if min_delta_R_sq1_save2 < min_delta_R_sq2:
                min_delta_R_sq2 = min_delta_R_sq2
                fj_sechardest_index = fj_hardest_index
            min_delta_R_sq1 = current_delta_R_sq1
            min_delta_R_sq1_save2 = current_delta_R_sq2
            fj_hardest_index = fj_index
            
        #Otherwise directly compare to delR2 value and update
        elif current_delta_R_sq2 < min_delta_R_sq2:
            min_delta_R_sq2 = current_delta_R_sq2
            fj_sechardest_index = fj_index
    
    #Check if good event: constituents, 4-momenta... if good return True and the indices of hardest 2 fastjet jets
    if np.abs(pFJ[fj_hardest_index][6]-float(AK5_hardest[7])) > 0. or np.abs(pFJ[fj_hardest_index][0]-float(AK5_hardest[1])) > 0.001 or np.abs(pFJ[fj_hardest_index][1]-float(AK5_hardest[2])) > 0.001 or np.abs(pFJ[fj_hardest_index][2]-float(AK5_hardest[3])) > 0.001 or np.abs(pFJ[fj_hardest_index][3]-float(AK5_hardest[4])) > 0.001: # or np.abs(pFJ[fj_sechardest_index][6]-float(AK5_hardest2[7])) > 0. or np.abs(pFJ[fj_sechardest_index][0]-float(AK5_hardest2[1])) > 0.001 or np.abs(pFJ[fj_sechardest_index][1]-float(AK5_hardest2[2])) > 0.001 or np.abs(pFJ[fj_sechardest_index][2]-float(AK5_hardest2[3])) > 0.001 or np.abs(pFJ[fj_sechardest_index][3]-float(AK5_hardest2[4])) > 0.001:
        ####################remive hash in above line after testing
        return [False,0,0]
    else:
        return [True,fj_hardest_index,fj_sechardest_index]