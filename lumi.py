import csv

#Open lumi file to identify 'good' events, a dictionary for {"<run>": {"<block0>":lumi, ...}}
def read_lumi_runs_and_blocks(lum_file_dir):
    lumi_runs_and_blocks = {}
    count = 0
    
    with open(lum_file_dir) as file:
        reader = csv.reader(file, delimiter=',')
        
        for row in reader:
            if not '#' in row[0]:
                run = row[0].split(':')[0]
                block = row[1].split(':')[0]
                
                if not run in lumi_runs_and_blocks:
                    lumi_runs_and_blocks[run] ={}
                if not block in lumi_runs_and_blocks[run]:
                    lumi_runs_and_blocks[run][block] = float(row[6])
                    count += 1
    return lumi_runs_and_blocks

#Check if the pair run_and_block=(<string run #>, <string block #>) is in lumi_runs_and_blocks
def search_lumi(run_and_block, lumi_runs_and_blocks):
    if not run_and_block[0] in lumi_runs_and_blocks:
        return False
    if not run_and_block[1] in lumi_runs_and_blocks[run_and_block[0]]:
        return False
    return True
