import numpy as np

class Jet:
    def __init__(self,p):
        self.__px   = p[0]
        self.__py   = p[1]
        self.__pz   = p[2]
        self.__e    = p[3]
        self.__pT   = (p[0]**2+p[1]**2)**.5
        self.__pmag = (self.__pT**2+p[2]**2)**.5
        self.__mass = (p[3]**2-self.__pmag**2)**.5
        self.__y    = np.artanh(p[2]/p[3])
        self.__eta  = np.artanh(p[2]/self.__pmag)
        self.__phi  = np.arccos(p[0]/self.__pmag)
    
    def px(self):
        return self.__px
    
    def py(self):
        return self.__py
    
    def pz(self):
        return self.__pz
    
    def e(self):
        return self.__e
    
    def p(self):
        return [self.__px,self.__py,self.__pz,self.__e]
    
    def pT(self):
        return self.__pT
    
    def pmag(self):
        return self.__pmag
    
    def mass(self):
        return self.__mass
    
    def y(self):
        return self.__y
    
    def eta(self):
        return self.__eta
    
    def phi(self):
        return self.__phi