#Define function which reads in MOD file and list of good events, then for each event
#regeneraqtes all the jets from the PFC 4-vectors, tests the compatibility to the AK5s,
#and saves the good event jets
import fastjet as fj
from match_jets import match_jets

#Define FastJet parameters, and the algorithm
R = 0.5
jet_def = fj.JetDefinition(fj.antikt_algorithm, R)

#Define fastjet jet generator function
def Jet_generator(MOD_file,line_no_list):
    """ Inputs: MOD_file and the list of all good events
        Outputs: the updated list of good events and the respective FJ jets' 4-vectors for those events
    """
    #Updated format of good events: [first line, second line, trigger, [list of jets]]
    Jet_corrected_line_no_list = [] 
    
    #Initialise csv reader at zeroth line with index i=-1
    i = -1
    row = []

    #Loop through all listed events in MOD_file
    for (idx, event) in enumerate(line_no_list):
    
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
        
        #Check to see if FJ jets correspond to AK5 jets, if they don't ignore/remove event, if they do save the event and FJ jet 4-vectors
        if match_jets(jets,AK5s) is True:
            Jet_corrected_line_no_list.append([event[0],event[1],event[2],jets])
    
    return Jet_corrected_line_no_list


#Define function to increment the current row in consideration in the input MOD file, and respective counter
def next_MOD_file(i, MOD_file):
    return (i+1, next(MOD_file))
