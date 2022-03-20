
from cmath import pi
from random import uniform
import matplotlib.pyplot as plt

import numpy as np


from scipy import interpolate
from scipy.fftpack import fft, fftfreq

from ltspice import Ltspice



def uniformResample(time: list, values: list, timeStep: float):
    """ returns a [time,value] list with an evenly spaced timestep and linearly interpolated values for the new timesteps """
    f = interpolate.interp1d(time, values)                      # Creates a function which returns an interpolated number of values for a given time
    uniTime = np.arange(time[0],time[time.size-1], timeStep)    # Creates a time array of the same time span with evenly spaced time steps
    uniVal = f(uniTime)                                         # Fill the array uniVal with interpolated numbers for all the evenly spaced timesteps
    return [uniTime, uniVal]



def compareUniformResample(rawFileName: str, resampleTime=1*10**-9):
    """ Plots the deltatime, phase-current over time and fourier of both non-uniform time data and sub-sampled uniform time data for comparison """

    l = Ltspice(rawFileName)
    l._x_dtype = np.float64
    l._y_dtype = np.float64

    l.parse()

    timeVec = l.get_time()
    currentVec = l.get_data("i(l.xload.l1)")

    # Resample the values into new vectors with uniform timestep of 5 ns
    [uniTime, uniVal] = uniformResample(timeVec, currentVec, resampleTime)

    # Plot current over time
    plt.figure(0)
    plt.title("Phase current over time")
    plt.plot(timeVec, currentVec, label="Non-uniform time")
    plt.plot(uniTime, uniVal, label="Uniform time")
    plt.legend()


    # Plot timestep size, shows a constant line at the set timestep with dips when the simulator decreases the timestep
    # For the uniform time, there are no dips
    diffTime =    timeVec[1:timeVec.size-1] - timeVec[0:timeVec.size-2]
    uniDiffTime = uniTime[1:uniTime.size-1] - uniTime[0:uniTime.size-2]
    
    plt.figure(1)
    plt.title("Delta-time")
    plt.plot(timeVec[0:timeVec.size-2], diffTime,    label="Non-uniform time")
    plt.plot(uniTime[0:uniTime.size-2], uniDiffTime, label="Uniform time")
    plt.legend()


    # Plot fourier of current   NOTE:   Time vector is non-uniform, but fft can only be done on uniform data, thus this is slightly inaccurate
    #                                   PyNUFFT package is for non-uniform fft but I could not get it to work.
    plt.figure(2)
    plt.title("FFT of phase current over time")
    plt.yscale("log")
    plt.xscale("log")
    plt.grid()

    # Plot non-uniform time fourier
    # Number of sample points
    N = timeVec.size
    yf = fft(currentVec)
    xf = fftfreq(N, resampleTime)[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label="Non-uniform time")

    # Plot uniform time fourier
    # Number of sample points
    N = uniTime.size
    yf = fft(uniVal)
    xf = fftfreq(N, resampleTime)[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), label="Uniform time")
    
    plt.legend()
    plt.show()


def plotTimeDiff(filename: str):
    """ Plot the timestep size over time, i.e. a line at the max timestep size with dips where the simulator has decreases the timestep """

    raw = Ltspice(filename)
    raw._x_dtype = np.float64
    raw._y_dtype = np.float64
    raw.parse()

    time = raw.get_time()
    diffTime  =  time[1:time.size-1] -   time[0:time.size-2]
    
    plt.title("Delta-time")
    plt.plot(time[0:time.size-2], diffTime, linewidth=1)


def compareCMCCurrent(noCMCRawFileName: str, cmcRawFileName: str, label1: str, label2: str, alpha=0.5, resampleTime=1*10**-9):
    """ Jämför svar av en krets utan common-mode-choke med en innehållande CMC """

    ncRaw = Ltspice(noCMCRawFileName)
    ncRaw._x_dtype = np.float64
    ncRaw._y_dtype = np.float64

    ncRaw.parse()

    cmcRaw = Ltspice(cmcRawFileName)
    cmcRaw._x_dtype = np.float64
    cmcRaw._y_dtype = np.float64

    cmcRaw.parse()

    ncTime = ncRaw.get_time()
    ncCurrent = ncRaw.get_data("i(l.xload.l1)") + ncRaw.get_data("i(l.xload.l2)") + ncRaw.get_data("i(l.xload.l3)")

    cmcTime = cmcRaw.get_time()
    cmcCurrent = cmcRaw.get_data("i(l.xload.l1)") + cmcRaw.get_data("i(l.xload.l2)") + cmcRaw.get_data("i(l.xload.l3)")


    # Plot current over time
    plt.figure(0)
    plt.title("Common mode current")
    plt.plot(ncTime, ncCurrent, linewidth=1, alpha=alpha, label=label2)
    plt.plot(cmcTime, cmcCurrent, linewidth=1, alpha=alpha, label=label1)
    plt.legend()


    # Plot timestep size, shows a constant line at the set timestep with dips when the simulator decreases the timestep
    ncDiffTime  =     ncTime[1:ncTime.size-1] -   ncTime[0:ncTime.size-2]
    cmcDiffTime =    cmcTime[1:cmcTime.size-1] - cmcTime[0:cmcTime.size-2]


    # Plot fourier of current
    # Resample the values into new vectors with uniform timestep of 5 ns
    [ncUniTime, ncUniVal] = uniformResample(ncTime, ncCurrent, 5*10**-9)
    [cmcUniTime, cmcUniVal] = uniformResample(cmcTime, cmcCurrent, 5*10**-9)

    plt.figure(2)
    plt.title("FFT of common mode current")
    plt.yscale("log")
    plt.xscale("log")
    plt.grid()

    # Plot uniform time fourier with no CMC
    # Number of sample points
    N = ncUniTime.size
    yf = fft(ncUniVal)
    xf = fftfreq(N, resampleTime)[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), linewidth=1, alpha=alpha, label=label1)

    # Plot uniform time fourier with CMC
    # Number of sample points
    N = cmcUniTime.size
    yf = fft(cmcUniVal)
    xf = fftfreq(N, resampleTime)[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), linewidth=1, alpha=alpha, label=label2)
    
    plt.legend()
    plt.show()


def compareFourier(filenames: list, labels: list, variableName="i(l.xload.l1)", title="", alpha=0.5, resampleTime=1*10**-9):
    """ Jämför en variabel över ett antal raw-filer  """

    plt.title(title)
    plt.loglog()
    plt.grid()

    # Walk through every file and plot the fourier of its value vector to the graph
    for i in np.arange(len(filenames)):
        raw = Ltspice(filenames[i])
        raw._x_dtype = np.float64
        raw._y_dtype = np.float64

        raw.parse()

        time = raw.get_time()
        val = raw.get_data(variableName)

        # Resample the values into new vectors with uniform timestep
        [uniTime, uniVal] = uniformResample(time, val, resampleTime)

        
        N = len(uniTime)
        yf = fft(uniVal)
        xf = fftfreq(N, resampleTime)[:N//2]
        plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), linewidth=1, alpha=alpha, label=labels[i])
    
    plt.legend()

def plotVars(fileName: str, variables: list, labels: list, alpha=0.5, title=""):
    """ Plotta alla givna variabler från en datafil i en plot, med labels """

    raw = Ltspice(fileName)
    raw._x_dtype = np.float64
    raw._y_dtype = np.float64

    raw.parse()

    time = raw.get_time()
    values = []
    for i in np.arange(len(variables)):
        values.append(raw.get_data(variables[i]))


    # Plot
    plt.title(title)
    for i in np.arange(min(len(values), len(labels))):
        plt.plot(time, values[i], linewidth=1, alpha=alpha, label=labels[i])
    
    plt.legend()

def plotFourier(filename: str, variableNames: list, labels: list, title, alpha=0.5, resampleTime=1*10**-9):
    """ Plotta fourier för fera variabler från en och samma raw-fil  """
    
    raw = Ltspice(filename)
    raw._x_dtype = np.float64
    raw._y_dtype = np.float64

    raw.parse()

    time = raw.get_time()

    
    plt.title(title)
    plt.loglog()
    plt.grid()

    for i in np.arange(len(variableNames)):

        val = raw.get_data(variableNames[i])

        # Resample the values into new vectors with uniform timestep
        [uniTime, uniVal] = uniformResample(time, val, resampleTime)

        
        N = len(uniTime)
        yf = fft(uniVal)
        xf = fftfreq(N, resampleTime)[:N//2]
        plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), linewidth=1, alpha=alpha, label=labels[i])
    
    plt.legend()



def visInterpolation():
    """ Visar en plot på hur interpoleringen av ström/spännings-datan fungerar """

    time = np.cumsum((1*np.random.rand(20)+0))              # Skapa tidsvektor med slumpmässigt tidssteg [0,1) 
    time[0] = 0                                             # Flytta första punkten bakåt till 0
    val = np.cumsum((0.1*(np.random.rand(20)-0.5)))+0.5     # Skapa y-data som startar vi 0.5 och där varje punkt varierar ±5% från föregående punkt

    [uniTime, uniVal] = uniformResample(time, val, 1)

    plt.figure(0)
    plt.plot(time, val, 'o-', markersize=7, linewidth=4, label="Non-uniform time")
    plt.plot(uniTime, uniVal, 'o-', markersize=7, linewidth=3, label="Uniform time")
    plt.ylim(0, 1)
    plt.legend()
    plt.xticks(np.arange(time[time.size-1]))
    plt.grid(axis='x')
    plt.show()




if __name__ == "__main__":

    # Jämför simuleringsresultat mellan en krets utan common-mode-choke och en med
    # compareFourier(["tmp_cmc_all2.raw", "tmp_cmc_all.raw"], labels=["all2", "all"])

    # Jämför common mode strömmen mellan två kretsar (från försimulerad data)
    # compareCMCCurrent("tmp_bin.raw", "tmp_cmc.raw", "No CMC", "Lcmc = 51 mH")
    
    # Jämför FFT mellan icke-subsamplad fasström och subsamplad fasström, också lite andra plots
    # compareUniformResample("tmp_bin.raw")

    # Visualiserar hur interpoleringen av datan fungerar
    # visInterpolation()

    # Plotta ett antal variabler i samma graf med olika färger
    plt.figure(0)
    plotVars("tmp_cmc.raw", ["i(@c.xbatgnd.c1[i])", "i(@c.xinvgnd.c1[i])", "i(@c.xloadgnd.c1[i])"], ["Battery", "Inverter", "Load"], title="Current through parasitic capacitances")
    plt.figure(1)
    plotVars("tmp_cmc.raw", ["v(pha)", "v(phb)", "v(phc)"], ["A", "B", "C"], title="Phase Voltages")
    plt.figure(2)
    plotVars("tmp_cmc.raw", ["i(l.xload.l1)", "i(l.xload.l2)", "i(l.xload.l3)"], ["A", "B", "C"], title="Phase Currents")

    plt.figure(3)
    compareFourier(["tmp_cmc.raw"], labels=[""], variableName="i(l.xload.l1)", title="Phase current")

    plt.figure(4)
    plotFourier("tmp_cmc.raw", ["i(@c.xbatgnd.c1[i])", "i(@c.xinvgnd.c1[i])", "i(@c.xloadgnd.c1[i])"], ["Battery", "Inverter", "Load"], title="Current through parasitic capacitances")

    plt.show()
    
    
        
        