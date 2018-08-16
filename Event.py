import fastjet as fj

class Event:
    def __init__(self, jets, prescale, jec, jet_quality, trigger_fired):
        self.__jets          = jets
        self.__prescale      = prescale
        self.__jec           = jec
        self.__jet_quality   = jet_quality
        self.__trigger_fired = trigger_fired

    def jets(self):
        return self.__jets
    
    def mul_pre_SD(self):
        return len(self.__jets[0].constituents())
    
    def mass_pre_SD(self):
        return self.__jets[0].m()
    
    def hardest_consts(self):
        #returns constituents 4-momenta in EnergyFlow format [E,px,py,pz]
        p_mus = [[const.e(), const.px(), const.py(), const.pz()]
                 for const in self.__jets[0].constituents()]
        
        return p_mus
    
    def hardest_pT(self):
        return self.__jets[0].pt()*self.__jec
    
    def hardest_eta(self):
        return self.__jets[0].eta()
    
    def hardest_phi(self):
        return self.__jets[0].phi()
    
    def hardest_area(self):
        if self.__jets[0].has_area():
            return self.__jets[0].area()
        else:
            return 'nan'
    
    def prescale(self):
        return self.__prescale
    
    def jec(self):
        return self.__jec
    
    def jet_quality(self):
        return self.__jet_quality
    
    def trigger_fired(self):
        return self.__trigger_fired
    
    def set_jet_quality(self, jet_quality):
        self.__jet_quality = jet_quality
    
    def set_trigger_fired(self, trigger_fired):
        self.__trigger_fired = trigger_fired
        
    '''  
    def track_mass_pre_SD(self):
        track_jets = [filter_charged(self.__jets[jet].constituents()) for jet in range(len(self.__jets))]
                
        
        
        #Need to redefine a jet clustering algorithm of infinite radius, then take jet.m() of that new object...
        ClusterSequence.cs_track1(track_constit_hardest, jet_def_cambridge) #Unsure if this is correct structure? see preksha's analyze.cc
        ClusterSequence.cs_track2(track_constit_second, jet_def_cambridge)
        track_jet_hardest = cs_track1.inclusive_jets()[0]
        track_jet_second = cs_track2.inclusive_jets()[0]  
        return 
    '''
    def track_mul_pre_SD(self):
        track_jets = [filter_charged(self.__jets[jet].constituents()) for jet in range(len(self.__jets))]
        Track_muls = [len(track_jet) for track_jet in track_jets]
        return Track_muls[0]        #Just returns hardest jet for that event, need to edit dat so each entry is both jets of event
    
#Define reclustering algorithm for track jets
R = float(1e32) #arbitrary large ~ ----> inf
jet_def_cambridge = fj.JetDefinition(fj.cambridge_algorithm,R)

 
#Define function to select and return only track constituents in a Jet
def filter_charged(Jet):
    Track_IDs = [1,2,11,13,15,211,321,2212,3112,3222,3312,3334]
    filtered = []
    for particle in Jet:
        if abs(particle.user_index()) in Track_IDs:
           filtered.append(particle)
    return filtered
