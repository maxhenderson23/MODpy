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
        return len(self.__jets.hardest_jet_constituents())
    
    def hardest_pT(self):
        return self.__jets[0].pt()
    
    def hardest_eta(self):
        return self.__jets[0].eta()
    
    def hardest_phi(self):
        return self.__jets[0].phi()
    
    def hardest_area(self):
        return self.__jets[0].area()
    
    def prescale(self):
        return self.__prescale
    
    def jec(self):
        return self.__jec
    
    def jet_quality(self):
        return self.__jet_quality
    
    def trigger_fired(self):
        return self.__trigger_fired