'''
    match_jets: Tries to establish a 1:1 correspondance between a set of FastJet clusters (FJCs) and a set of AK5s by their momentum four-vector
    (note the convention p = (px,py,pz,e).) The return value is true if such a correspondance can be established.
'''

import numpy as np

def match_jets(pAK5, pFJ, comments=False):
    
    pAK5_nomatch = []
    
    #Perform initial sort by energy to speed up checks
    pAK5  = sorted(pAK5,  key=lambda i: i[3])
    pFJ = sorted(pFJ, key=lambda i: i[3])
    
    #values in MeV
    for pi in pAK5:
        #find all "close" jets (within 1 MeV)
        jclose = []
        j = 0
        
        for pj in pFJ:
            if np.abs(pi[0] - pj[0]) <= 1. and np.abs(pi[1] - pj[1]) <= 1. and np.abs(pi[2] - pj[2]) <= 1. and np.abs(pi[3] - pj[3]) <= 1.:
                jclose.append(j)
            j += 1
        
        #Case 1: more than one match
        if len(jclose) > 1:
            pclose = [pFJ[jj] for jj in jclose]
            
            #compare jets by mass squared
            mi     =  pi[3]**2 - pi[2]**2 - pi[1]**2 - pi[0]**2
            mclose = [pj[3]**2 - pj[2]**2 - pj[1]**2 - pj[0]**2 for pj in pclose]
            
            #find the AK5 closest in mass squared
            mcount = 0
            jclosest = 0
            least_dm = 10000000
            for jj in jclose:
                dm = np.abs(mclose[mcount] - mi)
                if dm < least_dm:
                    least_dm = dm
                    jclosest = jj
                mcount += 1
            
            #Reduce the list of closest entries to the one which is closest in mass (and move on to Case 2)
            jclose = [jclosest]
                
        #Case 2: 1:1 matched
        if len(jclose) == 1:
            if comments:
                print('Successfully matched ' + str(pi) + ' with ' + str(pFJ[jclose[0]]) + ".")
            pFJ.pop(jclose[0])
        
        #Case 3: no match
        if len(jclose) == 0:
            pAK5_nomatch.append(pi)
    
    #Return whether match process was successful
    if len(pFJ_nomatch) > 0:
        if comments:
            print('Warning: the following FJCs could not be matched:')
            for pj in pFJ:
                print(pj)
    
    if len(pAK5_nomatch) > 0:
        if comments:
            print('Warning: the following AK5s could not be matched:')
            for pi in pAK5_nomatch:
                print(pi)
        return False
    
    if comments:
        print('All FJCs and AK5s successfully matched.')
    return True


#Simplified function for only checking hardest 2 jets
def match_jets2(pAK5,pFJ):
    """ Function to check fastjet generated 2 hardest jets, match the AK5 two hardest jets in (rap,phi) multiplicity and 4-vector to within 1MeV
    Input both jet lists
    Output True or False if there is a match"""
    #Find trigger (hardest pT) jet, and second hardest jet, and their respective indices in the input lists
    #Initialise max values and respective indices
    AK5_maxpT_squared = 0.
    AK5_maxpT_index = 0
    AK5_secmaxpT_squared = 0.
    AK5_secmaxpT_index = 0
    #loop through AK5 jets
    for index in range(len(pAK5)):
        #Find the pT of the current jet
        current_pT_squared = (pAK5[index][0]**2+pAK5[index][1]**2)
        #Compare pT to current max, if larger update first and second values/indices
        if current_pT_squared > AK5_maxpT_squared:
            AK5_secmaxpT_squared = AK5_maxpT_squared
            AK5_secmax_index = AK5_maxpT_index
            AK5_maxpT_squared = current_pT_squared
            AK5_maxpT_index = index
        #Otherwise just compare to second, if larger update this
        elif current_pT_squared > AK5_secmaxpT_squared:
            AK5_secmaxpT_squared = current_pT_squared
            AK5_secmax_index = index
            
    #Define these 2 hardest jet rapidity and phi
    AK5_hardest_rap = np.arctanh(pAK5[AK5_maxpT_index][2]/pAK5[AK5_maxpT_index][3])
    AK5_hardest_phi = np.arctan2(pAK5[AK5_maxpT_index][1],pAK5[AK5_maxpT_index][0])
    AK5_sechardest_rap = np.arctanh(pAK5[AK5_secmax_index][2]/pAK5[AK5_secmax_index][3])
    AK5_sechardest_phi = np.arctan2(pAK5[AK5_secmax_index][1],pAK5[AK5_secmax_index][0])

 
    #Initialise with arbitrary high values
    min_delta_R_sq1 = 1000000.
    min_delta_R_sq2 = 1000000.
    min_delta_R_sq1_save2 = 1000000.
    fj_hardest_index = 0

    #Loop through all fj jets
    for fj_index in range(len(pFJ)):
        #Calculate the minimum azimuth difference between the current fj jet and AK5 hardest 2 jets
        phi1 = pFJ[fj_index][5]-AK5_hardest_phi
        phi2 = pFJ[fj_index][5]-AK5_sechardest_phi
        delta_phi1 = min([phi1,phi1+2*np.pi,phi1-2*np.pi],key=abs)
        delta_phi2 = min([phi2,phi2+2*np.pi,phi2-2*np.pi],key=abs)
        #Calculate the delR squared values to the hardest 2 AK5 jets
        current_delta_R_sq1 = (pFJ[fj_index][4]-AK5_hardest_rap)**2+delta_phi1**2
        current_delta_R_sq2 = (pFJ[fj_index][4]-AK5_sechardest_rap)**2+delta_phi2**2
        #Check if new delR1 is less than minimum, if so save it
        if current_delta_R_sq1 < min_delta_R_sq1:
            #If delR1 min is being updated, check to see if its old value could update the delR2 value, if so update it also with the old value
            if min_delta_R_sq1_save2 < min_delta_R_sq2:
                min_delta_R_sq2 = min_delta_R_sq2
                fj_sechardest_index = fj_hardest_index
            min_delta_R_sq1 = current_delta_R_sq1
            min_delta_R_sq1_save2 = current_delta_R_sq2
            fj_hardest_index = fj_index
        #Otherwise directly compare to delR2 value and update
        elif current_delta_R_sq2 < min_delta_R_sq2:
            min_delta_R_sq2 = current_delta_R_sq2
            fj_sechardest_index = fj_index
    
    #Check if good event: constituents, 4-momenta... if good return True and the indices of hardest 2 fastjet jets
    if np.abs(pFJ[fj_hardest_index][6]-pAK5[AK5_maxpT_index][4]) > 0.1 and np.abs(pFJ[fj_hardest_index][0]-pAK5[AK5_maxpT_index][0]) > 0.001 and np.abs(pFJ[fj_hardest_index][1]-pAK5[AK5_maxpT_index][1]) > 0.001 and np.abs(pFJ[fj_hardest_index][2]-pAK5[AK5_maxpT_index][2]) > 0.001 and np.abs(pFJ[fj_hardest_index][3]-pAK5[AK5_maxpT_index][3]) > 0.001 and np.abs(pFJ[fj_sechardest_index][6]-pAK5[AK5_secmaxpT_index][4]) > 0.1 and np.abs(pFJ[fj_sechardest_index][0]-pAK5[AK5_secmaxpT_index][0]) > 0.001 and np.abs(pFJ[fj_sechardest_index][1]-pAK5[AK5_secmaxpT_index][1]) > 0.001 and np.abs(pFJ[fj_sechardest_index][2]-pAK5[AK5_secmaxpT_index][2]) > 0.001 and np.abs(pFJ[fj_sechardest_index][3]-pAK5[AK5_secmaxpT_index][3]) > 0.001:
        return [False,0,0]
    else:
        return [True,fj_hardest_index,fj_sechardest_index]




'''
#Checks for match_jets
#2/2 matches
print('\n------2/2 matches------')
print(match_jets([[331.,221.,111.4,1000.], [431.,221.,211.4,2000.]],[[431.,221.,211.6,2000.8], [331.3,221.9,110.6,1000.99]], True))

#Different lengths
print('\n------Different lengths------')
print(match_jets([[331.,221.,111.4,1000.]],[[431.,221.,211.6,2000.8], [331.3,221.9,110.6,1000.99]], True))

#1/2 matches
print('\n------1/2 matches------')
print(match_jets([[331.,221.,111.4,1000.], [431.,251.,211.4,2000.]],[[431.,221.,211.6,2000.8], [331.3,221.9,110.6,1000.99]], True))

#Very close jets (note differences in pz,E)
print('\n------Very close------')
print(match_jets([[331.,221.,111.4,1000.], [331.,221.,111.4,1000.9]],[[331.,221.,111.5,1000.9], [331.,221.,111.3,1000.]], True))
'''