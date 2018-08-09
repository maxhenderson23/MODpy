import copy
import lumi
import numpy as np
import fastjet as fj
from Event import Event
from AK5 import AK5
import write_dat

def analyze_MOD(MOD_file, dat_file, lumi_runs_and_blocks, event_limit):
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
    '''AK5 jets stored as a list of strings corresponding to each entry of the row in the MOD file.
    The last entry is pT**2, saved as a floating point variable.'''
    
    def init_event_vars():
        return (AK5([]), AK5([]), [], [], 1.0, 1.0, -1, "default")
    #to use this function, copy the next line
    [ak5_hardest, ak5_second, pseudojet_particles, current_jets, current_prescale,
    current_jec, current_jet_quality, current_trigger_fired] = init_event_vars()

    #Write the .dat header
    write_dat.write_dat_header(dat_file)
    
    for row in MOD_file:
        
        if row[0] == "BeginEvent":
            good_event = True
            section_name = "BeginEvent"
            count += 1
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
                    continue
                
                #Check that a trigger has fired
                if current_trigger_fired == "default":
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
                    continue
                
                #Check that the hardest AK5 matches the highest trigger
                if squared_trigger_ranges[current_trigger_fired] > ak5_hardest.pT2():
                    
                    good_event = False
                    if (count-1)%k == 0:
                        print("the hardest AK5 pT squared is " + str(ak5_hardest.pT2()) + " and the trigger is " + current_trigger_fired + " with threshold " + str(squared_trigger_ranges[current_trigger_fired]))
                        print("the hardest AK5 (with JEC) is smaller than the trigger fired, hence this event is rejected, exiting event")
                    continue
                
                #Check that the hardest AK5 satisfies loose quality criteria
                elif ak5_hardest.calc_quality() > 0:
                    good_event = False
                    if (count-1)%k == 0:
                        print("the hardest AK5 is ", ak5_hardest)
                        print("loose JQC failed, exiting event")
                    continue
                else:
                    if (count%k-1) == 0:
                        print("the hardest AK5 is ", ak5_hardest)
                        print("the current trigger is " + current_trigger_fired)
                        print("trigger fired properly, loose JQC passed, jet quality set to " + str(ak5_hardest.quality()) + " , continue to process event")
            
            #Begin reading the new section
            section_name = row[1]
            if (count%k-1) == 0:
                print("beginning to read in section " + section_name)
            continue
        
        #Perform lumi checks for 2011 data and initialise new event
        if section_name == "Cond":
            if lumi.search_lumi((row[1], row[3]), lumi_runs_and_blocks):
                
                #Initialise variables for new event
                [ak5_hardest, ak5_second, pseudojet_particles, current_jets, current_prescale,
                current_jec, current_jet_quality, current_trigger_fired] = init_event_vars()
                if (count-1%k) == 0:
                    print("the event # " + str(count)+ " passed the check with lumi block (" + row[1] + ", " + row[3] + ")")
                continue
            else:
                good_event = False
                if (count-1%k) == 0:
                    print("this event does not exist in the good lumi block file, exiting event")
            continue
        
        #Update hardest trigger
        if section_name == "Trig":
            trigger_title = row[1].rpartition('_')[0]
            #Only consider HLT_Jet trigger types that have fired
            if trigger_title in squared_trigger_ranges and row[4] == "1":
                #Only update if trigger cut-off is larger than current cut-off in consideration
                if squared_trigger_ranges[trigger_title] > squared_trigger_ranges[current_trigger_fired]:
                    current_trigger_fired, current_prescale = (trigger_title, float(row[2])*float(row[3]))
            continue

        #Update two hardest AK5s
        if row[0] == "AK5":
            ak5 = AK5(row)
            
            if ak5.pT2() > ak5_hardest.pT2():
                ak5_second = copy.deepcopy(ak5_hardest)
                ak5_hardest = copy.deepcopy(ak5)
            elif ak5.pT2() > ak5_second.pT2():
                ak5_second = copy.deepcopy(ak5)
            continue

        #Update list of PFC four-momenta
        if row[0] == "PFC":
            pseudojet_particles.append(fj.PseudoJet(float(row[1]),float(row[2]),float(row[3]),float(row[4])))
            continue

        #End event; perform FastJet checks
        if row[0] == "EndEvent":
            if (count-1)%k == 0:
                print("Reaching Endevent of # " + str(count))

            if not ak5_hardest.valid() or not ak5_second.valid():
                print("NOoooo")
                continue

            #Run Fastjet checks: create pseudo jets from PFCs, match with hardest AK5s
            fastjets = jet_def(pseudojet_particles)
            fastjets_observables = [[fj.px(),fj.py(),fj.pz(),fj.e(),fj.rap(),fj.phi(),len(fj.constituents())] for fj in fastjets]
            matching_output = match_jets(ak5_hardest, ak5_second, fastjets_observables)
            
            #Check if jets have matched
            if matching_output[0] is False:
                good_event = False
                continue
            else:
                #Save two hardest jets
                fj_hardest = fastjets[matching_output[1]]
                fj_second = fastjets[matching_output[2]]
                
                print("Fastjet matching passed, writing event to dat file.")
                
                #Write to the Event class and then to the .dat file
                event = Event([fj_hardest, fj_second], current_prescale, ak5_hardest.jec(),
                              ak5_hardest.quality(), current_trigger_fired)
                write_dat.write_dat_event(dat_file, event)
            
            #Check to see if valid event count has reached its limit
            if valid_event_count == event_limit:
                break
            continue
    
    return valid_event_count

#Function to match hardest 2 jets with fastjet jets
def match_jets(ak5_hardest, ak5_second, fastjets):
    """ Function to check fastjet generated 2 hardest jets, match the AK5 two hardest jets in (rap,phi) multiplicity and 4-vector to within 1MeV
    Input 2 hardest AK5s, and list of Pseudojet clusters from fastjet
    Output True or False if there is a match, and the indices of the hardest fj jets if True"""
            
    #Define these 2 hardest jet rapidity and phi
    ak5_hardest.calc_eta_phi()
    ak5_second.calc_eta_phi()
 
    #Initialise with arbitrary high values
    min_delta_R_sq1 = 1000000.
    min_delta_R_sq2 = 1000000.
    min_delta_R_sq1_save2 = 1000000.
    fj_hardest_index = 0

    #Loop through all fj jets
    for fj_index in range(len(fastjets)):
        
        #Calculate the minimum azimuth difference between the current fj jet and AK5 hardest 2 jets
        phi1 = fastjets[fj_index][5]-ak5_hardest.phi()
        phi2 = fastjets[fj_index][5]-ak5_second.phi()
        delta_phi1 = min([phi1,phi1+2*np.pi,phi1-2*np.pi],key=abs)
        delta_phi2 = min([phi2,phi2+2*np.pi,phi2-2*np.pi],key=abs)
        
        #Calculate the delR squared values to the hardest 2 AK5 jets
        current_delta_R_sq1 = (fastjets[fj_index][4]-ak5_hardest.eta())**2+delta_phi1**2
        current_delta_R_sq2 = (fastjets[fj_index][4]-ak5_second.eta())**2+delta_phi2**2
        
        #Check if new delR1 is less than minimum, if so save it
        if current_delta_R_sq1 < min_delta_R_sq1:
            
            #If delR1 min is being updated, check to see if its old value could update the delR2 value, if so update it also with the old value
            if min_delta_R_sq1_save2 < min_delta_R_sq2:
                min_delta_R_sq2 = min_delta_R_sq2
                fj_second_index = fj_hardest_index
            min_delta_R_sq1 = current_delta_R_sq1
            min_delta_R_sq1_save2 = current_delta_R_sq2
            fj_hardest_index = fj_index
            
        #Otherwise directly compare to delR2 value and update
        elif current_delta_R_sq2 < min_delta_R_sq2:
            min_delta_R_sq2 = current_delta_R_sq2
            fj_second_index = fj_index
    
    #Check if good event: constituents, 4-momenta... if good return True and the indices of hardest 2 fastjet jets
    if (np.abs(fastjets[fj_hardest_index][6]) - ak5_hardest.mul() > 0.1   or
        np.abs(fastjets[fj_hardest_index][0]) - ak5_hardest.px()  > 0.001 or
        np.abs(fastjets[fj_hardest_index][1]) - ak5_hardest.py()  > 0.001 or
        np.abs(fastjets[fj_hardest_index][2]) - ak5_hardest.pz()  > 0.001 or
        np.abs(fastjets[fj_hardest_index][3]) - ak5_hardest.e()   > 0.001 or
        np.abs(fastjets[fj_second_index][6])  - ak5_second.mul()  > 0.1   or
        np.abs(fastjets[fj_second_index][0])  - ak5_second.px()   > 0.001 or
        np.abs(fastjets[fj_second_index][1])  - ak5_second.py()   > 0.001 or
        np.abs(fastjets[fj_second_index][2])  - ak5_second.pz()   > 0.001 or
        np.abs(fastjets[fj_second_index][3])  - ak5_second.e()    > 0.001):
        return [False,0,0]
    else:
        return [True,fj_hardest_index,fj_second_index]