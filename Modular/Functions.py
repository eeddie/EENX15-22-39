#
#   Functions.py
#
#   Innehåller funktioner som vi använder
#

import matplotlib.pyplot as plt

import numpy as np
import os

from scipy import interpolate
from scipy.fftpack import fft, fftfreq

from ltspice import Ltspice



def simulateNetlist(netlist: str, name='tmp'):
        netlist_file = open('tmp.net', 'w')
        netlist_file.write(netlist)
        netlist_file.close()
        os.system(f'ngspice.exe {name}.net"')                       # NOTE: Lägg till mappen med ngspice i systemvariablerna istället så slipper vi byta
        os.remove(f"{name}.net")

def batchNetlist(netlist: str, name = 'tmp', log=False):
        netlist_file = open(f'{name}.net', 'w')
        netlist_file.write(netlist)
        netlist_file.close()
        os.system(f'ngspice_con.exe -b -r {name}.raw {"-o " + name + ".raw" if log else ""} {name}.net')   # NOTE: Lägg till mappen med ngspice i systemvariablerna istället så slipper vi byta
        os.remove(f"{name}.net")


def uniformResample(time: list, values: list, timeStep: float, interpKind="cubic"):
    """ Samplar om tid- och värdes-vektorer med ett konstant tidssteg. Använder kubisk interpolering vilket krävs för FFT """
    f = interpolate.interp1d(time, values, kind=interpKind)                      # Creates a function which returns an interpolated number of values for a given time
    uniTime = np.arange(time[0],time[time.size-1], timeStep)    # Creates a time array of the same time span with evenly spaced time steps
    uniVal = f(uniTime)                                         # Fill the array uniVal with interpolated numbers for all the evenly spaced timesteps
    return [uniTime, uniVal]


def readVariables(fileName: str, *variables):
    """ Hämtar tid och variabel-vektorer från en raw-fil i formatet [time, data] där data är 2-dimensionell """

    raw = Ltspice(fileName)
    raw._x_dtype = np.float64
    raw._y_dtype = np.float64
    raw.parse()

    time = raw.get_time()
    data = []
    for variable in variables:
        data.append(raw.get_data(variable))
    
    return [time, data]

def plotTimeDiff(fileName: str):
    """ Plotta storleken på tidsstegen över tid i den aktiva plotten """

    [time, _] = readVariables(fileName)
    diffTime  =  time[1:time.size-1] -   time[0:time.size-2]
    
    plt.plot(time[0:time.size-2], diffTime, linewidth=1)


def plotVars(fileName: str, *variables: str, label: str, alpha=0.5):
    """ Plotta en variabel från en datafil i den aktiva ploten """

    [time, data] = readVariables(fileName, variables)

    for d in data:
        plt.plot(time, d, linewidth=1, alpha=alpha, label=label)

def plotFourierFromVector(time: list, data: list, label="", alpha=0.5):
    """ Plotta fourier från data- och tid-vektorer i den aktiva ploten """

    N = len(time)
    yf = fft(data)
    xf = fftfreq(N, time[1]-time[0])[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), linewidth=1, alpha=alpha, label=label)

    plt.loglog()
    plt.grid()


def plotFourierFromFile(filename: str, variableName: str, label: str, alpha=0.5, resampleTime=1*10**-9):
    """ Plotta fourier för en variabel från en och samma raw-fil i den aktiva ploten  """
    
    raw = Ltspice(filename)
    raw._x_dtype = np.float64
    raw._y_dtype = np.float64
    raw.parse()

    time = raw.get_time()
    data = raw.get_data(variableName)
    [uniTime, uniData] = uniformResample(time, data, resampleTime)

    plotFourierFromVector(uniTime, uniData, label, alpha)

    
