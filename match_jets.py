'''
    match_jets: Tries to establish a 1:1 correspondance between a set of FastJet clusters (FJCs) and a set of AK5s by their momentum four-vector
    (note the convention p = (px,py,pz,e).) The return value is true if such a correspondance can be established.
'''

import numpy as np

def match_jets(pFJ, pAK5, comments=False):
    
    if len(pAK5) != len(pFJ):
        if comments:
            print('Warning: pFJ and pAK5 are different lengths. Matching failed.')
        return False
    
    pFJ_nomatch = []
    
    #Perform initial sort by energy to speed up checks
    pFJ  = sorted(pFJ,  key=lambda i: i[3])
    pAK5 = sorted(pAK5, key=lambda i: i[3])
    
    #values in MeV
    for pi in pFJ:
        #find all "close" jets (within 1 MeV)
        jclose = []
        j = 0
        
        for pj in pAK5:
            if np.abs(pi[0] - pj[0]) <= 1. and np.abs(pi[1] - pj[1]) <= 1. and np.abs(pi[2] - pj[2]) <= 1. and np.abs(pi[3] - pj[3]) <= 1.:
                jclose.append(j)
            j += 1
        
        #Case 1: more than one match
        if len(jclose) > 1:
            pclose = [pAK5[jj] for jj in jclose]
            
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
                print('Successfully matched ' + str(pi) + ' with ' + str(pAK5[jclose[0]]) + ".")
            pAK5.pop(jclose[0])
        
        #Case 3: no match
        if len(jclose) == 0:
            pFJ_nomatch.append(pi)
    
    #Return whether match process was successful
    if len(pAK5) > 0:
        if comments:
            print('Warning: the following FJCs could not be matched:')
            for pi in pFJ_nomatch:
                print(pi)
            print('Warning: the following AK5s could not be matched:')
            for pj in pAK5:
                print(pj)
        return False
    
    if comments:
        print('All FJCs and AK5s successfully matched.')
    return True

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