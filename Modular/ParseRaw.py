
from cmath import pi
from random import uniform
import matplotlib.pyplot as plt

import numpy as np


from scipy import signal, interpolate
from scipy.fftpack import fft, fftfreq
from scipy.signal import TransferFunction

from ltspice import Ltspice

# Non uniform fourier transform, for transforms with uneven time steps
# NUDFT is supposedly the same but with double precision.
#from pynufft import NUFFT, NUDFT



def uniformResample(time: list, values: list, timeStep: float):
    """ returns a [time,value] list with an evenly spaced timestep and linearly interpolated values for the new timesteps """
    f = interpolate.interp1d(time, values)                      # Creates a function which returns an interpolated number of values for a given time
    uniTime = np.arange(time[0],time[time.size-1], timeStep)    # Creates a time array of the same time span with evenly spaced time steps
    uniVal = f(uniTime)                                         # Fill the array uniVal with interpolated numbers for all the evenly spaced timesteps
    return [uniTime, uniVal]



if __name__ == "__main__":

    l = Ltspice("tmp_bin.raw")
    l._x_dtype = np.float64
    l._y_dtype = np.float64

    l.parse()

    timeVec = l.get_time()
    currentVec = l.get_data("i(l.xload.l1)")

    # Plot current over time
    plt.figure(0)
    plt.title("Phase current over time")
    plt.plot(timeVec, currentVec)


    [uniTime, uniVal] = uniformResample(timeVec, currentVec, 5*10**-9)
    # plt.figure(1)
    # uniDiffTime = uniTime[1:uniTime.size-1] - uniTime[0:uniTime.size-2]
    # plt.plot(uniTime[0:uniTime.size-2], uniDiffTime)

    plt.plot(uniTime, uniVal)


    # Plot timestep size, shows a constant line at the set timestep with dips when the simulator decreases the timestep
    #diffTime = timeVec[1:timeVec.size-1] - timeVec[0:timeVec.size-2]
    #plt.figure(1)
    #plt.plot(timeVec[0:timeVec.size-2], diffTime)


    # Plot fourier of current   NOTE:   Time vector is non-uniform, but fft can only be done on uniform data, thus this is slightly inaccurate
    #                                   PyNUFFT package is for non-uniform fft but I could not get it to work.
    fourier = fft(currentVec)

    plt.figure(1)
    plt.title("FFT of phase current over time")
    # Number of sample points
    N = timeVec.size
    # sample spacing
    T = 5*(10**-9)
    yf = fft(currentVec)
    xf = fftfreq(N, T)[:N//2]

    plt.yscale("log")
    plt.xscale("log")
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label="non-uniform sampling")
    plt.grid()

    #plt.figure(4)
    N = uniTime.size
    # sample spacing
    T = 5*(10**-9)
    yf = fft(uniVal)
    xf = fftfreq(N, T)[:N//2]

    #plt.yscale("log")
    #plt.xscale("log")
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label="interpolated uniform subsampling")
    plt.legend()
    #plt.grid()
    plt.show()
