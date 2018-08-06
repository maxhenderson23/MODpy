#Read in line numbers (<start>, <end>) of good events into line_no_list
def analyze_MOD(MOD_file, lumi_runs_and_blocks, total_event_limit):
    good_event = True
    count = 0
    section_name = ''
    
    for row in MOD_file:
        
        if row[0] == '#':
            section_name = row[1]
            continue
        
        if section_name == "Cond":
            if search_lumi((row[1], row[3]), lumi_runs_and_blocks):
                good_event = True
            else:
                good_event = False
            continue
        
        if not good_event:
            continue
        
        if row[0] == "EndEvent":
            line_no_list.append((event_start_line_no, MOD_file.line_num))
            count += 1
            if count == total_event_limit:
                break
            if count%1000 == 0 and count>0:
                print("writing event No. " + str(count)+" and the line # is (" + str(line_no_list[-1][0]) + ", " + str(line_no_list[-1][1]) + ")")
            continue