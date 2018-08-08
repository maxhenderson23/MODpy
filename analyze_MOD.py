import copy
import lumi
import numpy as np
import fastjet as fj
from Event import Event
import write_dat

#Read in line numbers (<start>, <end>) of good events into line_no_list
def analyze_MOD(MOD_file, dat_file, lumi_runs_and_blocks, total_event_limit):
    good_event = True
    count = 0
    valid_event_count = 0
    section_name = ''
    
    k = 1000
    
    #Dictionary of trigger ranges, s.t. key=trigger label, entry=true cut-off range squared
    squared_trigger_ranges = {"default":0., "HLT_Jet30":900., "HLT_Jet60":8100., "HLT_Jet80":12100., "HLT_Jet110":22500., "HLT_Jet150":44100., "HLT_Jet190":72900., "HLT_Jet240":96100., "HLT_Jet300":152100., "HLT_Jet370":230400.}
    
    
    #Define FastJet parameters, and the algorithm
    R = 0.5
    jet_def = fj.JetDefinition(fj.antikt_algorithm, R)

    #initialize the parameters for the current event
    #AK5 jets are stored as a list of strings, the same format read from the MOD file, appending its pT squared as the last entry, which is NOT a string (a float instead)
    def init_event_vars():
        return (["default", 0.0], ["default", 0.0], [], [], 1.0, 1.0, -1, "default")
    #to use this function, copy the next line
    current_hardest_AK5, current_second_AK5, Pseudojet_particles, current_jets, current_prescale, current_jec, current_jet_quality, current_trigger_fired = init_event_vars()

    write_dat.write_dat_header(dat_file)
    
    for row in MOD_file:
        
        if row[0] == "BeginEvent":
            good_event = True
            section_name = "BeginEvent"
            #The count and limit check should be done at the Endevent section instead, put here for testing
            count += 1
            if count%k == 0 and count>0:
                print("starting to process event # " + str(count))
            if count == total_event_limit:
                break
            continue
        
        elif not good_event:
            continue
        
        elif row[0] == '#' and not ".mod" in row[1]:
            #If no trigger is fired, this event is bad
            if section_name == "Trig":
                if row[1] != "AK5": #Note 34 events in the 2 mod files we tested on didnt have an AK5 section (so failed this check and were ignored)
                    good_event = False 
                    continue
                if current_trigger_fired == "default":
                    good_event = False
                    if count%k == 0 and count>0:
                        print("this event failed to fire any trigger, exiting event")
                    continue
                else:
                    if count%k == 0 and count>0:
                        print("this event managed to fire some triggers, continue to process the event")
            elif section_name == "AK5":
                if row[1] != "PFC": 
                    good_event = False 
                    continue
                #If trigger condition is not satisfied, this event is bad
                if squared_trigger_ranges[current_trigger_fired] > current_hardest_AK5[-1]:
                    good_event = False
                    if count%k == 0 and count>0:
                        print("the hardest AK5 pT squared is " + str(current_hardest_AK5[-1]) + " and the trigger is " + current_trigger_fired + " with threshold " + str(squared_trigger_ranges[current_trigger_fired]))
                        print("the hardest AK5 (with JEC) is smaller than the trigger fired, hence this event is rejected, exiting event")
                    continue
                #apply 'loose' JQC to the hardest Jet, and reject the event if any of the followings are the case
                elif float(current_hardest_AK5[7]) <= 1. or float(current_hardest_AK5[8]) <= 0. or float(current_hardest_AK5[9]) >= 0.99 or float(current_hardest_AK5[10]) >= 0.99 or float(current_hardest_AK5[11]) <= 0. or float(current_hardest_AK5[12]) >= 0.99:
                    good_event = False
                    if count%k == 0 and count>0:
                        print("the hardest AK5 is ", current_hardest_AK5)
                        print("loose JQC failed, exiting event")
                    continue
                else:
                    #Check tight JQC criteria
                    if float(current_hardest_AK5[7]) > 1. or float(current_hardest_AK5[8]) > 0. or float(current_hardest_AK5[9]) < 0.9 or float(current_hardest_AK5[10]) < 0.9 or float(current_hardest_AK5[11]) > 0. or float(current_hardest_AK5[12]) < 0.99:
                        current_jet_quality = 3
                    #Check medium JQC criteria
                    elif float(current_hardest_AK5[7]) > 1. or float(current_hardest_AK5[8]) > 0. or float(current_hardest_AK5[9]) < 0.95 or float(current_hardest_AK5[10]) < 0.95 or float(current_hardest_AK5[11]) > 0. or float(current_hardest_AK5[12]) < 0.99:
                        current_jet_quality = 2
                    #Otherwise is automatically loose JQC, as passed previous test
                    else:
                        current_jet_quality = 1
                    if count%k == 0 and count>0:
                        print("the hardest AK5 is ", current_hardest_AK5)
                        print("the current trigger is " + current_trigger_fired)
                        print("trigger fired properly, loose JQC passed, jet quality set to 1, continue to process event")
                        
            section_name = row[1]
            if count%k == 0 and count>0:
                print("beginning to read in section " + section_name)
            continue
        
        elif section_name == "Cond":
            if lumi.search_lumi((row[1], row[3]), lumi_runs_and_blocks):
                current_hardest_AK5, current_second_AK5, Pseudojet_particles, current_jets, current_prescale, current_jec, current_jet_quality, current_trigger_fired = init_event_vars()
                if count%k == 0 and count>0:
                    print("the event # " + str(count)+ " passed the check with lumi block (" + row[1] + ", " + row[3] + ")")
                continue
            else:
                good_event = False
                if count%k == 0 and count>0:
                    print("this event does not exit in the good lumi block file, exiting event")
            continue
        
        elif section_name == "Trig":
            trigger_title = row[1].rpartition('_')[0]
            if trigger_title in squared_trigger_ranges and row[4] == "1": #Only consider HLT_Jet trigger types that have fired
                if squared_trigger_ranges[trigger_title] > squared_trigger_ranges[current_trigger_fired]: #Only update if trigger cut-off is larger than current cut-off in consideration
                    current_trigger_fired, current_prescale = (trigger_title, float(row[2])*float(row[3]))
            continue

        elif row[0] == "AK5":
            #We compared the current AK5 jet's pT to the largest and second
            pT_squared_for_this_AK5 = (float(row[1])**2 + float(row[2])**2)*(float(row[5])**2)
            if pT_squared_for_this_AK5 > current_hardest_AK5[-1]:
                current_second_AK5 = copy.deepcopy(current_hardest_AK5)
                current_hardest_AK5 = copy.deepcopy(row)
                current_hardest_AK5.append(pT_squared_for_this_AK5)
            elif pT_squared_for_this_AK5 > current_second_AK5[-1]:
                current_second_AK5 = copy.deepcopy(row)
                current_second_AK5.append(pT_squared_for_this_AK5)
            continue

        elif row[0] == "PFC":
            Pseudojet_particles.append(fj.PseudoJet(float(row[1]),float(row[2]),float(row[3]),float(row[4])))
            pass

        elif row[0] == "EndEvent":
            if count%k == 0 and count>0:
                print("Reaching Endevent of # " + str(count))

            #Run Fastjet checks: create pseudo jets from PFCs, match with hardest AK5s
            fastjets = jet_def(Pseudojet_particles)
            fastjets_observables = [[x.px(),x.py(),x.pz(),x.e(),x.rap(),x.phi(),len(x.constituents())] for x in fastjets]
            matching_output = match_jets(current_hardest_AK5,current_second_AK5,fastjets_observables)
            
            #If did not match event is bad, if matched, save the 2 hardest pseudojet objects
            if matching_output[0] is False:
                good_event = False
                continue
            else:
                FJ_hardest = fastjets[matching_output[1]]
                FJ_second_hardest = fastjets[matching_output[2]]
                
                event = Event([FJ_hardest, FJ_second_hardest], current_prescale, current_jec, current_jet_quality, current_trigger_fired)
                write_dat.write_dat_event(dat_file, event)
              
            valid_event_count += 1 
            continue
    
    return 

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
    if np.abs(pFJ[fj_hardest_index][6]-float(AK5_hardest[7])) > 0.1 and np.abs(pFJ[fj_hardest_index][0]-float(AK5_hardest[1])) > 0.001 and np.abs(pFJ[fj_hardest_index][1]-float(AK5_hardest[2])) > 0.001 and np.abs(pFJ[fj_hardest_index][2]-float(AK5_hardest[3])) > 0.001 and np.abs(pFJ[fj_hardest_index][3]-float(AK5_hardest[4])) > 0.001 and np.abs(pFJ[fj_sechardest_index][6]-float(AK5_hardest2[7])) > 0.1 and np.abs(pFJ[fj_sechardest_index][0]-float(AK5_hardest2[1])) > 0.001 and np.abs(pFJ[fj_sechardest_index][1]-float(AK5_hardest2[2])) > 0.001 and np.abs(pFJ[fj_sechardest_index][2]-float(AK5_hardest2[3])) > 0.001 and np.abs(pFJ[fj_sechardest_index][3]-float(AK5_hardest2[4])) > 0.001:
        return [False,0,0]
    else:
        return [True,fj_hardest_index,fj_sechardest_index]