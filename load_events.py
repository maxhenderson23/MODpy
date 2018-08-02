import csv

#Read in good events to event_list
#type is "AK5" or "PFC"
#keys is a list of keys we want to be loaded

def load_valid_event_entries(valid_event_line_no, event_list, type, keys):
    count = 0
    
    PFC_key_dic = {"px": 1,
                   "py": 2,
                   "pz": 3,
                   "e": 4,
                   "pdgId": 5}
    
    PFC_tot_dic = {"total_px": 1,
                   "total_py": 2,
                   "total_pz": 3,
                   "total_e": 4}

    for MOD_file_dir in valid_event_line_no:
        raw_MOD_file = open(MOD_file_dir)
        MOD_file = csv.reader(raw_MOD_file, delimiter=' ', skipinitialspace = 1)
        i = 0
        
        for event in valid_event_line_no[MOD_file_dir]:
            event_list.append({type:[]})
            count += 1
            if count%1000 == 0 and count > 1:
                print("loading event # " + str(count) + " with value " + str(event_list[-2]["total_px"]))
            
            event_list[-1]["trigger"] = event[2]
            
            for key in keys:
                if not key in PFC_key_dic:
                    event_list[-1][key] = 0.0
            
            while i < event[0]:
                row = next(MOD_file)
                i += 1
            
            while i < event[1] - 1:
                row = next(MOD_file)
                
                if row[0] == type:
                    event_list[-1][type].append({})
                    
                    for key in keys:
                        if key in PFC_key_dic:
                            event_list[-1][type][-1][key] = float(row[PFC_key_dic[key]])
                        
                        elif key in PFC_tot_dic:
                            shortkey = key.split('_')[1]
                            event_list[-1][key] += float(row[PFC_key_dic[shortkey]])
                elif len(event_list[-1][type]) > 0:
                    break

                i += 1

    return
