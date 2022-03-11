
from cmath import pi
import matplotlib.pyplot as plt

import numpy as np

from scipy import signal
from scipy.fftpack import fft, fftfreq
from scipy.signal import TransferFunction

from ltspice import Ltspice

# Non uniform fourier transform, for transforms with uneven time steps
# NUDFT is supposedly the same but with double precision.
#from pynufft import NUFFT, NUDFT


if __name__ == "__main__":

    l = Ltspice("tmp_bin.raw")
    l._x_dtype = np.float64
    l._y_dtype = np.float64

    l.parse()

    timeVec = l.get_time()
    currentVec = l.get_data("i(l.xload.l1)")

    # Plot current over time
    plt.figure(0)
    plt.plot(timeVec, currentVec)

    # Plot timestep size, shows a constant line at the set timestep with dips when the simulator decreases the timestep
    #diffTime = timeVec[1:timeVec.size-1] - timeVec[0:timeVec.size-2]
    #plt.figure(1)
    #plt.plot(timeVec[0:timeVec.size-2], diffTime)


    # Plot fourier of current   NOTE:   Time vector is non-uniform, but fft can only be done on uniform data, thus this is slightly inaccurate
    #                                   PyNUFFT package is for non-uniform fft but I could not get it to work.
    fourier = fft(currentVec)

    plt.figure(1)
    # Number of sample points
    N = timeVec.size
    # sample spacing
    T = 5*(10**-9)
    yf = fft(currentVec)
    xf = fftfreq(N, T)[:N//2]

    plt.yscale("log")
    plt.xscale("log")
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]))
    plt.grid()
    plt.show()
