
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 22:48:40 2022

@author: Gerardo Ortíz Montufar
"""

from numpy import logspace,log10,pi,angle,ones, complex128
from scipy.signal import freqresp, freqz

class frecResponse:
    
    def Fltr(self, SYS,fc):
        wx = logspace(0,2,2000)*fc
        Ny = ones(len(wx),complex128)
        
        for i in range(len(SYS)):
            W, HB = freqresp(SYS[i], wx)
            Ny *= HB
        
        Hdb = 20*log10(abs(Ny))
        Hphi = angle(Ny)
        
        return W/(2*pi), Hdb, Hphi, Ny
    
    
    def IIR(self, SYS, fc, sps):
        W, HB = freqz(SYS[0][0], SYS[0][1], whole = False, fs = 2*pi*sps)
        Ny = HB
        for i in range(1,len(SYS)):
            W, HB = freqz(SYS[i][0], SYS[i][1], whole = False, fs = 2*pi*sps)
            Ny *= HB
        
        Hdb = 20*log10(abs(Ny))
        Hphi = angle(Ny)
        
        return W/(2*pi), Hdb, Hphi, Ny
    
    
    def FIR(self, h):
        w, H = freqz(h, [1])
        
        return w, 20*log10(abs(H)), angle(H), H
    
