#Read in line numbers (<start>, <end>) of good events into line_no_list
def analyze_MOD(MOD_file, lumi_runs_and_blocks, total_event_limit):
    good_event = True
    count = 0
    
    for row in MOD_file:
        
        if row[0] == "Cond":
            if search_lumi((row[1], row[3]), lumi_runs_and_blocks):
                good_event_started = True
                event_start_line_no = MOD_file.line_num
        
        if row[0] == "EndEvent" and good_event_started == True:
            line_no_list.append((event_start_line_no, MOD_file.line_num))
            if count == event_limit:
                break
            count += 1
            good_event_started = False 
            if count%1000 == 0 and count>0:
                print("writing event No. " + str(count)+" and the line # is (" + str(line_no_list[-1][0]) + ", " + str(line_no_list[-1][1]) + ")")
    
    return count