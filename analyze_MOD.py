import copy
import lumi
import fastjet as fj
from match_jets import match_jets
from Event import Event
from AK5 import AK5
import write_dat

def analyze_MOD(MOD_file, dat_file, lumi_runs_and_blocks, event_limit):
    good_event = True
    count = 0
    valid_event_count = 0
    section_name = ''
    k = 1000 #Provide commentary every k events
    
    #Dictionary of trigger ranges, s.t. key=trigger label, entry=true cut-off range squared
    squared_trigger_ranges = {"default":0., "HLT_Jet30":900., "HLT_Jet60":8100., 
    "HLT_Jet80":12100., "HLT_Jet110":22500., "HLT_Jet150":44100., "HLT_Jet190":72900., 
    "HLT_Jet240":96100., "HLT_Jet300":152100., "HLT_Jet370":230400.}
    
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
                    selected_trigger = highest_lower_trig_threshold                         
                    selected_trigger_prescale = current_prescales[current_triggers_fired.index(highest_lower_trig_threshold)]
                if highest_lower_trig_threshold not in current_triggers_fired:
                    good_event = False
                    if (count-1)%k == 0 and count>0:
                        print("the hardest AK5 pT squared is " + str(current_hardest_AK5[-1]) + " and the trigger is " + highest_lower_trig_threshold + " with threshold " + str(squared_trigger_ranges[highest_lower_trig_threshold]))
                
                #Check that the hardest AK5 matches the highest trigger
                if squared_trigger_ranges[current_trigger_fired] > ak5_hardest.pT2():
                    
                    good_event = False
                    if (count-1)%k == 0:
                        print("the hardest AK5 pT squared is " + str(ak5_hardest.pT2()) + " and the trigger is " + current_trigger_fired + " with threshold " + str(squared_trigger_ranges[current_trigger_fired]))
                        print("Rejected, exiting event")
                    continue
                
                #Check that the hardest AK5 satisfies loose quality criteria
                elif ak5_hardest.calc_quality() == 0:
                    good_event = False
                    if (count-1)%k == 0:
                        print("the hardest AK5 is ", ak5_hardest)
                        print("loose JQC failed, exiting event")
                    continue
                else:
                    if (count-1)%k == 0:
                        print("the hardest AK5 is ", current_hardest_AK5)
                        print("the current triggers are ",selected_trigger)
                        print("trigger fired properly, loose JQC passed, jet quality set to 1, continue to process event")

                        print("the hardest AK5 is ", ak5_hardest)
                        print("the current trigger is " + current_trigger_fired)
                        print("trigger fired properly, loose JQC passed, jet quality set to " + str(ak5_hardest.quality()) + " , continue to process event")
            
            #Begin reading the new section
            section_name = row[1]
            if (count-1)%k == 0:
                print("beginning to read in section " + section_name)
            continue
        
        #Perform lumi checks for 2011 data and initialise new event
        if section_name == "Cond":
            if lumi.search_lumi((row[1], row[3]), lumi_runs_and_blocks):
                
                #Initialise variables for new event
                [ak5_hardest, ak5_second, pseudojet_particles, current_jets, current_prescale,
                current_jec, current_jet_quality, current_trigger_fired] = init_event_vars()
                
                if (count-1)%k == 0 and count>0:
                    print("the event # " + str(count)+ " passed the check with lumi block (" + row[1] + ", " + row[3] + ")")
                continue
            else:
                good_event = False
                if (count-1)%k == 0:
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
            ak5 = AK5(row)
            
            if ak5.pT2() > ak5_hardest.pT2():
                ak5_second = copy.deepcopy(ak5_hardest)
                ak5_hardest = copy.deepcopy(ak5)
            elif ak5.pT2() > ak5_second.pT2():
                ak5_second = copy.deepcopy(ak5)
            continue

        #Update list of PFC four-momenta
        if row[0] == "PFC":
            Pseudojet_particles.append(fj.PseudoJet(float(row[1]),float(row[2]),float(row[3]),float(row[4])))
            continue

        #End event; perform FastJet checks
        if row[0] == "EndEvent":
            if (count-1)%k == 0:
                print('Reached end of event # ' + str(count))

            if not ak5_hardest.valid() or not ak5_second.valid():
                print("\033[93m###################### WARNING ###################### \nat least one AK5 not initialised. Event number " + str(count) + '\033[0m')
                continue

            #Run Fastjet checks: create pseudo jets from PFCs, match with hardest AK5s
            fastjets = jet_def(Pseudojet_particles)
            fastjets_observables = [[j.px(),j.py(),j.pz(),j.e(),j.rap(),j.phi(),len(j.constituents())] for j in fastjets]
            matching_output = match_jets(ak5_hardest, ak5_second, fastjets_observables)
            
            #Check if jets have matched
            if matching_output[0] is False:
                good_event = False
                if (count-1)%k == 0:
                    print("Fastjet matching failed, discarding event.")
                continue
            else:
                #Save two hardest jets
                fj_hardest = fastjets[matching_output[1]]
                fj_second = fastjets[matching_output[2]]
                
                if (count-1)%k == 0:
                    print("Fastjet matching passed, writing event to dat file.")
                
                #Write to the Event class and then to the .dat file
                event = Event([fj_hardest, fj_second], current_prescale, ak5_hardest.jec(),
                              ak5_hardest.quality(), current_trigger_fired)

                write_dat.write_dat_event(dat_file, event)

                if (count-1)%k == 0:
                    valid_event_count += 1
                    print("Event validated with fastjet, and written to .dat, event #: ",str(count),'accepted event #:',valid_event_count)
                    print('##############################################################')
            if valid_event_count == event_limit:
                break
            continue
    
    return valid_event_count
