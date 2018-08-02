import numpy as np

class Jet:
    def __init__(self,px,py,pz,e):
        self.__px   = px
        self.__py   = py
        self.__pz   = pz
        self.__e    = e
        self.__pT   = (px**2+py**2)**.5
        self.__pmag = (self.__pT**2+pz**2)**.5
        self.__mass = (e**2-self.__pmag**2)**.5
        self.__y    = np.artanh(pz/e)
        self.__eta  = np.artanh(pz/self.__pmag)
        self.__phi  = np.arccos(px/self.__pmag)
    
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