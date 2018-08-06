#Define function which reads in MOD file and list of good events, then for each event
#regeneraqtes all the jets from the PFC 4-vectors, tests the compatibility to the AK5s,
#and saves the good event jets
import fastjet as fj
import plot
from match_jets import match_jets

#Define FastJet parameters, and the algorithm
R = 0.5
jet_def = fj.JetDefinition(fj.antikt_algorithm, R)

#Define fastjet jet generator function
def Jet_generator(MOD_file,line_no_list):
    """ Inputs: MOD_file and the list of all good events
        Outputs: the updated list of good events and the respective FJ jets' 4-vectors for those events
    """
    #Return format: [[first line, second line, trigger], [list of jets]]
    Jet_corrected_line_no_list = [] 
    all_jets = []
    
    #Initialise csv reader at zeroth line with index i=-1
    i = -1
    row = []
    
    
    list_counter = 0 ########
    #Loop through all listed events in MOD_file
    for (idx, event) in enumerate(line_no_list):
        list_counter += 1 #########
        
        #Iterate to the first line of current event
        while i < event[0]:
            (i, row) = next_MOD_file(i, MOD_file) #End of iteration
            
        Particles = []
        AK5s = []
        
        #Loop through the PFCs and add their 4-vectors as psuedojets
        while i < event[1]:
            
            if row[0] == "AK5":
                #Add the AK5 4-vectors to a list for comparison with FJ jets
                AK5s.append([float(row[1]),float(row[2]),float(row[3]),float(row[4])])
            
            if row[0] == "PFC":
                #Add the particle 4-vector (px,py,pz,E) as a pseudo-jet 
                Particles.append(fj.PseudoJet(float(row[1]),float(row[2]),float(row[3]),float(row[4]))) 
            
            #Increment row, and respective counter
            (i, row) = next_MOD_file(i, MOD_file) 
            
        #Create the jets via FastJet algorithm
        jets = jet_def(Particles)
        jets_list = [[x.px(),x.py(),x.pz(),x.e()] for x in jets]
        
        #pFJ = [[jet.px(), jet.py(), jet.pz(), jet.e()] for jet in jets]
        
        #Check to see if FJ jets correspond to AK5 jets, if they don't ignore/remove event, if they do save the event and FJ jet 4-vectors
        if True: #match_jets(AK5s,jets_list) == True:
            Jet_corrected_line_no_list.append([event[0],event[1],event[2]]) #,jets_list])  READD IN TO PLOT WITH FJ JETS!! ##############
    
        '''        
        if list_counter < 5: #################
            print(list_counter)
            #print(Particles)
            print()
            print('AK5s: ',AK5s)
            print()
            print('fj jets:' ,jets_list)
            print()
            print('corrected jet list: ',Jet_corrected_line_no_list)
            print('end of print')
            print()
    '''
    
    return [Jet_corrected_line_no_list, all_jets]

#Define function to increment the current row in consideration in the input MOD file, and respective counter
def next_MOD_file(i, MOD_file):
    return (i+1, next(MOD_file))
