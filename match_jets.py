import numpy as np

#Function to match hardest 2 jets with fastjet jets
def match_jets(ak5_hardest, ak5_second, fastjets):
    """ Function to check fastjet generated 2 hardest jets, match the AK5 two hardest jets in (rap,phi) multiplicity and 4-vector to within 1MeV
    Input 2 hardest AK5s, and list of Pseudojet clusters from fastjet
    Output True or False if there is a match, and the indices of the hardest fj jets if True"""
            
    #Define these 2 hardest jet eta and phi
    ak5_hardest.calc_eta_phi()
    ak5_second.calc_eta_phi()
 
    #Initialise with arbitrary high values
    min_delta_R_sq1 = 1000000.
    min_delta_R_sq2 = 1000000.
    min_delta_R_sq1_save2 = 1000000.
    fj_hardest_index = 0
    fj_second_index = 0

    #Loop through all fj jets
    for fj_index in range(len(fastjets)):
        
        #Calculate the minimum azimuth difference between the current fj jet and AK5 hardest 2 jets
        phi1 = fastjets[fj_index][5]-ak5_hardest.phi()
        phi2 = fastjets[fj_index][5]-ak5_second.phi()
        
        delta_phi1 = min([phi1,phi1+2*np.pi,phi1-2*np.pi],key=abs)
        delta_phi2 = min([phi2,phi2+2*np.pi,phi2-2*np.pi],key=abs)
        
        #Calculate the delR squared values to the hardest 2 AK5 jets
        current_delta_R_sq1 = (fastjets[fj_index][4]-ak5_hardest.eta())**2+delta_phi1**2
        current_delta_R_sq2 = (fastjets[fj_index][4]-ak5_second.eta())**2+delta_phi2**2
        
        #Check if new delR1 is less than minimum, if so save it
        if current_delta_R_sq1 < min_delta_R_sq1:
            
            #If delR1 min is being updated, check to see if its old value could update the delR2 value, if so update it also with the old value
            if min_delta_R_sq1_save2 < min_delta_R_sq2:
                min_delta_R_sq2 = min_delta_R_sq2
                fj_second_index = fj_hardest_index
            min_delta_R_sq1 = current_delta_R_sq1
            min_delta_R_sq1_save2 = current_delta_R_sq2
            fj_hardest_index = fj_index
            
        #Otherwise directly compare to delR2 value and update
        elif current_delta_R_sq2 < min_delta_R_sq2:
            min_delta_R_sq2 = current_delta_R_sq2
            fj_second_index = fj_index
    
    #Check if good event: constituents, 4-momenta... if good return True and the indices of hardest 2 fastjet jets
    if (np.abs(fastjets[fj_hardest_index][6] - ak5_hardest.mul()) > 0.1   or
        np.abs(fastjets[fj_hardest_index][0] - ak5_hardest.px())  > 0.001 or
        np.abs(fastjets[fj_hardest_index][1] - ak5_hardest.py())  > 0.001 or
        np.abs(fastjets[fj_hardest_index][2] - ak5_hardest.pz())  > 0.001 or
        np.abs(fastjets[fj_hardest_index][3] - ak5_hardest.e())   > 0.001 or
        np.abs(fastjets[fj_second_index][6]  - ak5_second.mul())  > 0.1   or
        np.abs(fastjets[fj_second_index][0]  - ak5_second.px())   > 0.001 or
        np.abs(fastjets[fj_second_index][1]  - ak5_second.py())   > 0.001 or
        np.abs(fastjets[fj_second_index][2]  - ak5_second.pz())   > 0.001 or
        np.abs(fastjets[fj_second_index][3]  - ak5_second.e())    > 0.001):
        return [False,0,0]
    else:
        return [True,fj_hardest_index,fj_second_index]