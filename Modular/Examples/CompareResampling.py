# 
# Plottar tre fourierkurvor från fasströmmen
# En kurva utan resampling, en med linjär resampling, en med kubisk resampling
#

import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import *

import sys
sys.path.append('./Modular/')
from Functions import *

filename = "raws/gain=100.raw"
resampleTime = 1*10**-9     # The time step for the uniform fouriers
maxTimeStep  = 5*10**-9     # The time step for the non-uniform fourier

if __name__=="__main__": 

    [time, current] = readVariables(filename, "i(l.xload.l1)")

    [uniTime, currentLin] = uniformResample(time, current, timeStep=1*10**-9, interpKind="linear")
    [_      , currentCub] = uniformResample(time, current, timeStep=1*10**-9, interpKind="cubic")

    # Plot non-uniform time fourier
    N = time.size
    yf = fft(current)
    xf = fftfreq(N, maxTimeStep)[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label="Icke-uniform tid", alpha=0.5)

    # Plot linearly interpolated fourier
    N = uniTime.size
    yf = fft(currentLin)
    xf = fftfreq(N, resampleTime)[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label="Linjär interpolation", alpha=0.5)

    # Plot cubic interpolated fourier
    yf = fft(currentCub)
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label="Kubisk interpolation", alpha=0.5)

    plt.grid()
    plt.loglog()
    plt.legend()
    plt.show()