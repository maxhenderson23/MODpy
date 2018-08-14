# MODpy
python MOD analyser

// test

Process rough workflow: 
Parse reads MOD_file, removes 'bad' events due to lumi blocks, trigger effects, JQC, Fastjet comparison, then creates a .dat file of the hardest jet objects
Plot_dat then generates plots from this 

Main script reads in a MOD_file

Uses lumi script to cross check with the 'good' lumi events and creates a list of all the good event start&end row numbers in the MOD file.

Uses trigger script to scan each good event, find the largest trigger that fired, and check whether the largest AK5 jet pT value corresponds to the fired triggers' respective pT range (after JEC scaling).
Events where no trigger fired, or there is not agreement with trigger ranges, or the hardest jet does not meet the loose JQC are removed from the list of 'good' events.

Uses FJ_jet_generator script to regenerate the jets for each event from the PFCs, then the match_jet function to cross check with the AK5s. 
Events where the cross_check is not shown to agree are removed from the list of good events, the remaining good events have the FJ generated jet information saved also.

Plotting..... read MOD/dat?... add observables to lists, run np.histogram, plot
"""

mkdir ../MODpy_output/