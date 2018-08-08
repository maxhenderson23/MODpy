class Event:
    def __init__(self, jets, prescale, jec, jet_quality = -1, trigger_fired = 'nan'):
        self.__jets          = jets
        self.__prescale      = prescale
        self.__jec           = jec
        self.__jet_quality   = jet_quality
        self.__trigger_fired = trigger_fired

    def jets(self):
        return self.__jets
    
    def mul_pre_SD(self):
        return len(self.__jets[0].constituents())
    
    def hardest_pT(self):
        return self.__jets[0].pt()
    
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