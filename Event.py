#Define reclustering algorithm for track jets
import fastjet as fj
R = fj.JetDefinition.max_allowable_R #arbitrary large ~ ----> inf
jet_def_cambridge = fj.JetDefinition(fj.cambridge_algorithm,R)

#Event class
class Event:
    def __init__(self, jets, prescale, jec, jet_quality, trigger_fired):
        self.__jets          = jets
        self.__prescale      = prescale
        self.__jec           = jec
        self.__jet_quality   = jet_quality
        self.__trigger_fired = trigger_fired

        #print("########################Initialising event, \nhardest pt = " + str(self.__jets[0].pt()) + "\nsecond pt = " + str(self.__jets[1].pt()))


    def jets(self):
        return self.__jets
    
    def mul_pre_SD(self):
        return len(self.__jets[0].constituents())
    
    def mass_pre_SD(self):
        return self.__jets[0].m()
    
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
    
    def track_mass_pre_SD(self):
        #Filter the jets particles into just lists of the charged particles (as pseudojets)
        track_jets = [filter_charged(jet.constituents()) for jet in self.__jets]
        track_masses = []
        #Recalculate the clustering for only the charged particles in the jets
        for jet in track_jets:
            fastjet = jet_def_cambridge(jet)
            #Append the mass of the regenerated jet to a list for output
            if len(fastjet) != 0:   #Sometimes there are no charged particles in one of the jets => omit jet
                track_masses.append(fastjet[0].m())
        return track_masses[0]      #Just returns hardest jet for that event, need to edit dat so each entry is both jets of event
    
    def track_mul_pre_SD(self):
        #Filter the jets particles into just lists of the charged particles (as pseudojets)
        track_jets = [filter_charged(jet.constituents()) for jet in self.__jets]
        Track_muls = [len(track_jet) for track_jet in track_jets]
        return Track_muls[0]        #Just returns hardest jet for that event, need to edit dat so each entry is both jets of event

 
#Define function to select and return only track constituents in a Jet
def filter_charged(Jet):
    Track_IDs = [1,2,11,13,15,211,321,2212,3112,3222,3312,3334]
    filtered = []
    for particle in Jet:
        if abs(particle.user_index()) in Track_IDs:
           filtered.append(particle)
    return filtered
