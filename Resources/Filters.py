# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 21:27:47 2022

@author: Ortiz Montufar Gerardo
"""
from numpy import log10, pi, exp, ceil, sqrt, cosh, arccosh, cos, arccos, arcsinh 
from numpy import sin, sinh, arange
from scipy.signal import get_window

# =============================================================================
#         Functions: Are use to calculate specific mathematic expresions

def polesButter(k, NB, wcB):
    '''
    Butterworth poles function, it gives the complex poles on the left of
    semiplane of Laplace. It depends of parameter k: [0,N/2] with NB pair. If NB
    odd k:[0:int(N/2)+1]. This function was traversed in k + N

    Parameters
    ----------
    k : float
        number of complex conjugate pole [0,N/2] with NB pair and [0, int(NB/2)+1] if NB odd
    NB : float
        Order of the filter Buterworth
    wcB : float
        cutoff frequency

    Returns
    -------
    pB : complex
        A conjugate complex pole of a Butterworth filter with NB order and 
        cutoff frequency wcB

    '''
    pB = wcB*exp(1j*(2*k + 1 + NB)*pi/(2*NB))
    return pB

def polesCheby(k, NT, wp, a, wcT = None):
    '''
    Chebyshev poles function, it gives the complex poles on the left of
    semiplane of Laplace. It depends of parameter k: [0,N/2] with NB pair. If NB
    odd k:[0:int(N/2)+1]. This function was traversed in k + N

    Parameters
    ----------
    k : float
        number of complex conjugate pole [0,N/2] with NB pair and [0, int(NB/2)+1] if NB odd
    NT : float
        Order of the filter Buterworth
    wp : float
        frecuency of the band pass
    a : float
        Parameter of the filter a = (1/NT)*arcsinh(1/e) where e = sqrt(10**(Ap/10)-1)
        Ap is the minimum atenuation on the pass band
    wcT : float, optional
        wcT is the cutoff frecuency of a Chebyshev filter. If gives an float number
        this function returns the complex poles of a high pass Chebyshev filter.
        The default is None.

    Returns
    -------
    pT : complex
        Returns the pole of position k of a Chebyshev filter of NB order and cutoff
        frecuency wcT. If wcT is a float number returns the poles of a high pass filter

    '''
    
    #LP poles
    pT = wp*(sin((2*k+2*NT+1)*pi/(2*NT))*sinh(a)+1j*cos((2*k+2*NT+1)*pi/(2*NT))*cosh(a))
    
    #HP poles
    if wcT:
        pT = (wcT**2)/pT
    
    return pT

def SOS(ComplexPole, HP):
    '''
    A procedure to obtain the Second Order Section (SOS) of a analog filter
    with complex conjugate poles

    Parameters
    ----------
    ComplexPole : complex
        The complex canjugate pole of a second order filter
    HP : boolean
        if HP true returns the SOS of a high pass filter

    Returns
    -------
    num : list
        The numerator of the filter
    den : list
        The denominator of the filter

    '''
    
    den = [1, -2*ComplexPole.real, abs(ComplexPole)**2]
    if not HP:
        num = [abs(ComplexPole)**2]
    elif HP:
        num = [1,0,0]
    
    return (num,den)

def FOS(ComplexPole, HP):
    '''
    A procedure to obtain the First Order Section of a analog filter

    Parameters
    ----------
    ComplexPole : float or complex
        The pole of a FOS
    HP : boolean
        If HP true returns the FOS of a high pass filter

    Returns
    -------
    num : list
        The numerator of the filter
    den : TYPE
        The denominator of the filter

    '''
    den = [1, abs(ComplexPole)]
    
    if not HP:
        num = [abs(ComplexPole)]
        
    elif HP:
        num = [1,0]
    
    return (num,den)

def Sync(wc, N):
    '''
    The normalized Sinc function Sync(x) = Sin(pi*x)/(pix) with x = wc(n-a)
    for signals, where a = (N-1)/2
    
    Parameters
    ----------
    wc : float 
        the cutoff frequency of a FIR filter
    N : float
        the number of points of a FIR filter

    Returns
    -------
    n : Array
        The n points to plot
    x : Array
        The sinc function

    '''
    # Index vector
    n = arange(0, N, 1).astype(int)
    # Alpha
    a = (N-1)/2
    # Numerator y denominator of Sync(x)
    num = sin(wc*(n-a))
    den = wc*(n-a)
    # Evita el error en n=a si N impar
    if N%2 == 1:
        num[int(a)] = 1
        den[int(a)] = 1
    # Sync(x)
    x = (wc/pi)*num/den
    return n, x

def GenSec(func, HP, *args):
    '''
    Generate the sections of a analog filter

    Parameters
    ----------
    func : function
        Receive a poles function of a filter
    HP : boolean
        If HP true return the SOS and FOS sections of a high pass filter
    *args : float
        The arguments that the function poles will recive (func parameter)

    Returns
    -------
    sec : list
        Returns a list of tuples with SOS and FOS sections of a filter

    '''
    
    N = args[0]
    sec = []
    
    if N != 1:
        
        n = int(N/2)
        for i in range(n):
            p = func(i, *args)
            sec.append( SOS(p, HP) )
                            
        if N % 2 != 0:
            i += 1
            p = func(i, *args)
            sec.append( FOS(p, HP) )
    else:
        p = func(0, *args)
        sec.append( FOS(p, HP) )
    
    return sec
#                              END FUNCTIONS
# =============================================================================



class Filter:
    
    @staticmethod
    def Butterworth(Ap, Ar, fp, fr, HP = False):
        '''
        Generate a Butterworth filter with relative specificaitions

        Parameters
        ----------
        Ap : int
            Ap must be a positive int, is the minimum attenuation in the pass band
            in decibels
        Ar : int
            Ar must be a positive int, is the attenuation in the reject band
            in decibels
        fp : int
            Is the frequency of the pass band in hz
        fr : int
            Is the frequency of the reject band in hz
        HP : boolen, optional
            If HP is true returns a high pass Butterworth filter of a low pass
            design with the same cutoff frequency. The default is False.

        Returns
        -------
        fcB  : int
            Cutoff frequency of the total filter in hz
        secB : list
            returns a list of tuples with the SOS and FOS of a Butterworth filter

        '''
        
        NB = ceil( log10( (10**(Ap/10)-1)/(10**(Ar/10)-1) ) / (2*log10(fp/fr)) ).astype('int')
        wcB = 2*pi*fp / ( 10**(Ap/10)-1 )**( 1/(2*NB) )
        secB = GenSec(polesButter, HP, NB, wcB)
        
        return wcB/(2*pi), secB
    
    @staticmethod
    def Chebyshev(Ap, Ar, fp, fr, HP = False):
        '''
        Generate a Chebyshev filter with relative specificaitions

        Parameters
        ----------
        Ap : int
            Ap must be a positive int, is the minimum attenuation in the pass band
            in decibels
        Ar : int
            Ar must be a positive int, is the attenuation in the reject band
            in decibels
        fp : int
            Is the frequency of the pass band in hz
        fr : int
            Is the frequency of the reject band in hz
        HP : boolen, optional
            If HP is true returns a high pass Chebyshev filter of a low pass
            design with the same cutoff frequency. The default is False.

        Returns
        -------
        fcT : int
            The cutoff frequency of all the filter
        secT : list
            Returns a list of tuples with the SOS and FOS of a Chebyshev filter

        '''
        
        e = sqrt(10**(Ap/10)-1)
        NT = ceil(arccosh(sqrt((10**(Ar/10)-1)/(10**(Ap/10)-1)))/arccosh(fr/fp)).astype('int')
        a = (1/NT)*arcsinh(1/e)
        
        if Ap <= 3:
            wcT = 2*pi*fp*cosh(arccosh(1/sqrt(10**(Ap/10)-1))/NT)
        else:
            wcT = 2*pi*fp*cos(arccos(1/sqrt(10**(Ap/10)-1))/NT)
        
        if not HP:
            secT = GenSec(polesCheby, HP, NT, 2*pi*fp, a)
            
        elif HP:
            secT = GenSec(polesCheby, HP, NT, 2*pi*fp, a, wcT)
        
        if len(secT[-1][1]) == 3:#Para mantener ganancia unitaria
            A = 10**(-Ap/20)
            secT[-1][0][0] *= A
        
        return wcT/(2*pi), secT
    
    @staticmethod
    def BilinearTF(fs, FilterBank):
        '''
        Construct the bilinear transformation of a FOS or SOS system

        Parameters
        ----------
        fs : int
            Sample rate in hz
        FilterBank : list
            A list of tuples of a analog filter design (only FOS and SOS)

        Returns
        -------
        IIR : list
            Returns a list of tuples of a IIR digital filter

        '''
        
        T = 1/fs
        IIR = []
        
        for i in range(len(FilterBank)):
            AF = FilterBank[i] #Analog Filter
            num = AF[0]
            den = AF[1]
            
            if len(den) == 2: #FOS
                a = den[-1]*T
                
                if len(num) == 1: #LP
                    num_iir = [a, a]
                else: #HP
                    num_iir = [2,-2]
                
                IIR.append( (num_iir,[a+2, a-2]) )
            
            elif len(den) == 3: #SOS
                a = den[-1]*(T**2)
                b0 = 4 + 2*den[1]*T + a
                b2 = 4 - 2*den[1]*T + a
                b1 = 2*a - 8
                
                if len(num) == 1: #LP
                    num_iir = [a,2*a,a]
                    
                else: #HP
                    num_iir = [4,-8,4]
                
                IIR.append( (num_iir,[b0,b1,b2]) )
                
            else:
                #levantar excepcion no se acepta de orden mayor a dos
                pass
        
        return IIR
    
    @staticmethod
    def FIR(Ap, As, fp, fs, sps = 1, HP = False):
        '''
        Generate a FIR filter with realtive specifications with the windows method

        Parameters
        ----------
        Ap : float
            Ap must be a positive float, is the minimum attenuation in the pass band
            in decibels (not implemented)
        As : float
            Ar must be a positive float, is the attenuation in the reject band
            in decibels
        fp : float
            Is the frequency of the pass band in hz
        fs : float
            Is the frequency of the reject band in hz
        sps: float, optional
            Is the sample rate 
        HP : boolen, optional
            If HP is true returns a high pass FIR filter. The default is False.

        Returns
        -------
        wc : float
            Aproximate cutoff frequency of the design
        h : Array
            Returns the FIR filter

        '''
        
        wp, ws = fp*2*pi/sps, fs*2*pi/sps #digital frequency
        
        windows = {21 : ('boxcar', 4*pi), 
                   25 : ('bartlett', 4*pi), 
                   44 : ('hamming', 8*pi),
                   53 : ('hanning', 8*pi),
                   74 : ('blackman', 12*pi)
                   }
        
        window, rad = None ,None
        for attenuation in windows:
            if attenuation >= As:
                window = windows[attenuation][0]
                rad = windows[attenuation][1]
                break
         #The order of the filter is the middle of the transition band
        if rad:
            N = ceil(rad/(abs(ws - wp))).astype('int')
        
        if not window:
            beta = 0.1102*(As-8.7)
            N = ceil( (As - 7.95) / (2.285*abs(ws-wp)) + 1 ).astype('int')
            window = ('kaiser', beta)
        
        # Type I
        if N % 2 == 0:
            N += 1
        
        wc = (ws+wp)/2
        n, h = Sync(wc, N)
        
        if HP:
            n, h1 = Sync(pi, N) #all pass
            h = (h1-h)
            
        if window:
            h = h*get_window(window, N)
        
        return wc, h
