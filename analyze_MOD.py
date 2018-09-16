import copy
import lumi
import fastjet as fj
from match_jets import match_jets
from Event import Event
from AK5 import AK5
import write_dat
import write_consts

def analyze_MOD(MOD_file, dat_file, lumi_runs_and_blocks, event_limit):
    good_event = True
    count = 0
    valid_event_count = 0
    section_name = ''
    entry_dic = {}
    k = 1000 #Provide commentary every k events
    
    trigger_ranges = {"default":0., "HLT_Jet30":30., "HLT_Jet60":90., "HLT_Jet80":110., "HLT_Jet110":150., "HLT_Jet150":210., "HLT_Jet190":270., "HLT_Jet240":290., "HLT_Jet300":390., "HLT_Jet370":480.}
    
    #initialize info to calculate effective luminosity for respective trigger
    effective_luminosity = {"HLT_Jet30":0., "HLT_Jet60":0., "HLT_Jet80":0., "HLT_Jet110":0., "HLT_Jet150":0., "HLT_Jet190":0., "HLT_Jet240":0., "HLT_Jet300":0., "HLT_Jet370":0.}
    appeared_lumi_run_block_trigger = {}
    
    #Define FastJet parameters, and the algorithm
    R = 0.5
    jet_def = fj.JetDefinition(fj.antikt_algorithm, R)

    #initialize the parameters for the current event
    def init_event_vars():
        return (AK5([], {}), AK5([], {}), [], [], 1.0, 1.0, -1, [], '', [], 1.0, {})
    #to use this function, copy the next line
    [ak5_hardest, ak5_second, pseudojet_particles, current_jets, current_prescale,
    current_jec, current_jet_quality, current_triggers_fired, selected_trigger,
    current_prescales, selected_prescale, current_triggers_prescales] = init_event_vars()

    #Write the file headers
    write_dat.write_dat_header(dat_file)
    
    for row in MOD_file:
        
        if row[0] == "BeginEvent":
            good_event = True
            section_name = "BeginEvent"
            count += 1
            
            if (count-1)%k == 0:
                print()
                print(">>>>>>>>>>>>>>>>>>starting to process event # " + str(count) + " <<<<<<<<<<<<<<<<<<<<<<")
            continue
        
        if not good_event:
            continue
        
        if row[0] == '#' and len(row) > 1:
            
            #Skip the MOD file name line
            if ".mod" in row[1]:
                continue
            
            #New section. First check that sections follow on in the correct order. Then perform checks on the data stored from the previous section.
            if section_name == "Trig":
                #Write in effective luminosity
                
                
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
                highest_lower_trig_threshold = 'default'
                for i in trigger_ranges:
                    if trigger_ranges[highest_lower_trig_threshold] < trigger_ranges[i] < ak5_hardest.pT():
                        highest_lower_trig_threshold = i
                        
                #Save the trigger equivalent to the current pT, and respective prescale
                if highest_lower_trig_threshold not in current_triggers_fired:
                    good_event = False
                    if (count-1)%k == 0 and count>0:
                        print("the hardest AK5 pT is " + str(ak5_hardest.pT()) + " and the trigger is " + highest_lower_trig_threshold + " with threshold " + str(trigger_ranges[highest_lower_trig_threshold]))
                        print("Hardest possible trigger not fired, ejecting event")
                    continue

                selected_trigger = highest_lower_trig_threshold
                selected_prescale = current_prescales[current_triggers_fired.index(highest_lower_trig_threshold)]
                
                #Check that the hardest AK5 satisfies loose quality criteria
                if ak5_hardest.calc_quality() == 0:
                    good_event = False
                    if (count-1)%k == 0:
                        print("the hardest AK5 is ", ak5_hardest)
                        print("loose JQC failed, exiting event")
                    continue
                else:
                    if (count-1)%k == 0:
                        print("the hardest AK5 is ", ak5_hardest)
                        print("the selected trigger is ",selected_trigger)
                        print("trigger fired properly, loose JQC passed, jet quality set to " + str(ak5_hardest.quality()) + " , continue to process event")
            
            #Begin reading the new section, updating section name and entry_dic to record the relation between column name and index
            section_name = row[1]
            entry_dic = {}
            for i, entry in enumerate(row[1:]):
                entry_dic[entry] = i
            if (count-1)%k == 0:
                print("beginning to read in section " + section_name)
            continue
        
        #Perform lumi checks for 2011 data and initialise new event
        if section_name == "Cond":
            if lumi.search_lumi((row[entry_dic["RunNum"]], row[entry_dic["LumiBlock"]]), lumi_runs_and_blocks):
                
                #Initialise variables for new event
                [ak5_hardest, ak5_second, pseudojet_particles, current_jets, current_prescale,
                current_jec, current_jet_quality, current_triggers_fired, selected_trigger,
                current_prescales, selected_prescale] = init_event_vars()
                
                if (count-1)%k == 0 and count>0:
                    print("the event # " + str(count)+ " passed the check with lumi block (" + row[entry_dic["RunNum"]] + ", " + row[entry_dic["LumiBlock"]] + ")")
                continue
            else:
                good_event = False
                if (count-1)%k == 0:
                    print("Not in good lumi block, exiting event")
            continue
        
        #Update hardest trigger
        if section_name == "Trig":
            trigger_title = row[entry_dic["Name"]].rpartition('_')[0] #cut out the version number
            if trigger_title in trigger_ranges:
                current_triggers_prescales[trigger_title] = {"Fired?":(row[entry_dic["Fired?"]] == "1"), "prescale":float(row[entry_dic["Prescale_1"]])*float(row[entry_dic["Prescale_2"]])}
            if trigger_title in trigger_ranges and row[entry_dic["Fired?"]] == "1": #Save all HLT_Jet trigger types that have fired (and equivalent prescales)
                current_triggers_fired.append(trigger_title)
                current_prescales.append(float(row[entry_dic["Prescale_1"]])*float(row[entry_dic["Prescale_2"]]))
            continue

        #Update two hardest AK5s
        if section_name == "AK5":
            ak5 = AK5(row, entry_dic)
            
            if ak5.pT() > ak5_hardest.pT():
                ak5_second = copy.deepcopy(ak5_hardest)
                ak5_hardest = copy.deepcopy(ak5)
            elif ak5.pT() > ak5_second.pT():
                ak5_second = copy.deepcopy(ak5)
            continue

        #Update list of PFC four-momenta
        if row[0] == "PFC":
            psJ = fj.PseudoJet(float(row[entry_dic["px"]]),float(row[entry_dic["py"]]),float(row[entry_dic["pz"]]),float(row[entry_dic["energy"]]))
            psJ.set_user_index(int(row[entry_dic["pdgId"]]))
            pseudojet_particles.append(psJ)
            continue

        #End event; perform FastJet checks
        if row[0] == "EndEvent":
            if (count-1)%k == 0:
                print('Reached end of event # ' + str(count))

            if not ak5_hardest.valid() or not ak5_second.valid():
                print("\033[93m###################### WARNING ###################### \nat least one AK5 not initialised. Event number " + str(count) + '\033[0m')
                continue

            #Run Fastjet checks: create pseudo jets from PFCs, match with hardest AK5s
            fastjets = jet_def(pseudojet_particles)
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
                
                #Write to the Event class and then to the .dat file (Note this is just one event per line in the dat file (for both hardest jets))
                event = Event([fj_hardest, fj_second], selected_prescale, ak5_hardest.jec(),
                              ak5_hardest.quality(), selected_trigger)

                write_dat.write_dat_event(dat_file, event)

                valid_event_count += 1

                if (count-1)%k == 0:
                    print("Event validated with fastjet, and written to .dat, event #: ",str(count),', accepted event #:',valid_event_count)
                    print('##############################################################')

            if valid_event_count == event_limit:
                break
            continue
    
    return valid_event_count
