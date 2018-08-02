import csv

#Open lumi file to identify 'good' events
def read_lumi_runs_and_blocks(lum_file_dir):
    lumi_runs_and_blocks = {}
    count = 0
    
    with open(lum_file_dir) as file:
        reader = csv.reader(file, delimiter=',')
        
        for row in reader:
            if not '#' in row[0]:
                run = row[0].split(':')[0]
                block = int(row[1].split(':')[0])
                
                if not run in lumi_runs_and_blocks:
                    lumi_runs_and_blocks[run] = []
                if not block in lumi_runs_and_blocks[run]:
                    lumi_runs_and_blocks[run].append(block)
                    count += 1
                    if count%1000 == 0:
                        print("writing lum block No. " + str(count))
    return lumi_runs_and_blocks

#Check if the pair run_and_block=(<string run #>, <int block #>) is in lumi_runs_and_blocks
def search_lumi(run_and_block, lumi_runs_and_blocks):
    if not run_and_block[0] in lumi_runs_and_blocks:
        return False
    if not run_and_block[1] in lumi_runs_and_blocks[run_and_block[0]]:
        return False
    return True

#Read in line numbers (<start>, <end>) of good events into line_no_list
def get_line_no_good_lumi(MOD_file, line_no_list, lumi_runs_and_blocks, event_limit):
    good_event_started = False
    count = 0
    total_event_count = 0
    
    if event_limit == 0:
        return 0
    
    for row in MOD_file:
        if row[0] == "Cond":
            total_event_count += 1
            if search_lumi((row[1], int(row[3])), lumi_runs_and_blocks):
                good_event_started = True
                event_start_line_no = MOD_file.line_num
        
        if row[0] == "EndEvent" and good_event_started == True:
            line_no_list.append((event_start_line_no, MOD_file.line_num))
            count += 1
            good_event_started = False 
            if count%1000 == 0 and count>0:
                print("writing event No. " + str(count)+" and the line # is (" + str(line_no_list[-1][0]) + ", " + str(line_no_list[-1][1]) + ") ")
            if total_event_count == event_limit:
                break
    return total_event_count
