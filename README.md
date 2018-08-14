# MODpy
This repository has code to analyze MOD (MIT Open Data) files produced using [MODProducer]    
(https://github.com/rmastand/MODProducer "MODProducer" for latest version).    
It is an adaption of MODAnalyzer for implementation with python.    
(https://github.com/prekshan/MODAnalyzer/tree/master).  

<b>Process rough workflow:<b />   
Parse reads MOD_file(s) in the input folder.   
It calls the analyzeMOD function which removes 'bad' events due to: lumi blocks, trigger effects, Jet Quality Criteria, Fastjet comparison.   
It then creates a .dat file of the two hardest jet objects.  
Plot_dat then generates plots from this.   

Ensure that fastjet is installed and compiled.   
(http://www.fastjet.fr)   

This code runs using python3. 
...command to run the code from the MODpy folder is:  
python3 parse.py ~/path/to/folder/containing/MOD_files ~/output/folder/for/dat_files [optional] Number_of_events_limiter [optional]  
e.g. "python3 ~/Documents/MOD_files ~/Documents/MODpy_output 10000"   

######Comments about the plotting mechanism - for Joe to fill in#######   

<b>Cross-checking scripts are provided:<b/>   
Print_MOD_file will print selected events from an argument input MOD file to allow manual comparison.  
Dat_file_length_check will compare the number of events in two argument input dat files, and print the first event difference where one exists.   

###################################################################  
<b>TO DO:<b/>   
Modify dat file structure to contain all events (including bad, with reason why rejected)   
Implement: CHS, pileup   
Introduce: Sim/GEN data, Machine-learning methods    
