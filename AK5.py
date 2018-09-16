import numpy as np
import math

class AK5:
    def __init__(self, row, entry_dic):
        try:
            self.__valid         = True
            self.__px            = float(row[entry_dic["px"]])
            self.__py            = float(row[entry_dic["py"]])
            self.__pz            = float(row[entry_dic["pz"]])
            self.__e             = float(row[entry_dic["energy"]])
            self.__jec           = float(row[entry_dic["jec"]])
            self.__area          = float(row[entry_dic["area"]])
            self.__no_of_const   = float(row[entry_dic["no_of_const"]])
            self.__chrg_multip   = float(row[entry_dic["chrg_multip"]])
            self.__neu_had_frac  = float(row[entry_dic["neu_had_frac"]])
            self.__neu_em_frac   = float(row[entry_dic["neu_em_frac"]])
            self.__chrg_had_frac = float(row[entry_dic["chrg_had_frac"]])
            self.__chrg_em_frac  = float(row[entry_dic["chrg_em_frac"]])
            #self.__pT2  = self.__jec**2*(self.__px**2+self.__py**2)
            self.__pT = self.__jec * math.sqrt(self.__px**2+self.__py**2)
        
        except: #initialise with an empty row
            self.__valid         = False
            #self.__pT2           = 0.
            self.__pT            = 0.
        
    def valid(self):
        return self.__valid
    
    def calc_eta_phi(self):
        pmag = math.sqrt(self.__px**2+self.__py**2+self.__pz**2)
        self.__eta  = np.arctanh(self.__pz/pmag)
        self.__phi  = np.arctan2(self.__py, self.__px)
            
    def calc_quality(self):
        #Loose quality check
        if (self.__no_of_const <= 1. or self.__chrg_multip <= 0. or self.__neu_had_frac >= 0.99 or
            self.__neu_em_frac >= 0.99 or self.__chrg_had_frac <= 0. or self.__chrg_em_frac >= 0.99):
            self.__quality = 0
        
        #Tight quality check
        elif (self.__no_of_const > 1. and self.__chrg_multip > 0. and self.__neu_had_frac < 0.90 and
             self.__neu_em_frac < 0.90 and self.__chrg_had_frac > 0. and self.__chrg_em_frac < 0.99):
            self.__quality = 3
        
        #Medium quality check
        elif (self.__no_of_const > 1. and self.__chrg_multip > 0. and self.__neu_had_frac < 0.95 and
             self.__neu_em_frac < 0.99 and self.__chrg_had_frac > 0. and self.__chrg_em_frac < 0.99):
            self.__quality = 2
        
        else:
            self.__quality = 1
            
        return self.__quality
    
    def px(self):
        return self.__px
    
    def py(self):
        return self.__py
    
    def pz(self):
        return self.__pz
    
    def e(self):
        return self.__e
    
    #def pT2(self):
    #return self.__pT2
    
    def pT(self):
        return self.__pT
    
    def eta(self):
        return self.__eta
    
    def phi(self):
        return self.__phi
    
    def jec(self):
        return self.__jec
    
    def no_of_const(self):
        return self.__no_of_const
    
    def mul(self):
        return self.__no_of_const
    
    def chrg_multip(self):
        return self.__chrg_multip
    
    def neu_had_frac(self):
        return self.__neu_had_frac
    
    def neu_em_frac(self):
        return self.__neu_em_frac
    
    def chrg_had_frac(self):
        return self.__chrg_had_frac
    
    def chrg_em_frac(self):
        return self.__chrg_em_frac
    
    def quality(self):
        return self.__quality
