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
        os.system(f'ngspice_con.exe -b -r {name}.raw {"-o " + name + ".log" if log else ""} {name}.net')   # NOTE: Lägg till mappen med ngspice i systemvariablerna istället så slipper vi byta
        os.remove(f"{name}.net")


def uniformResample(time: list, values: list, timeStep: float, interpKind="cubic"):
    """ Samplar om tid- och värdes-vektorer med ett konstant tidssteg. Använder kubisk interpolering vilket krävs för FFT """
    f = interpolate.interp1d(time, values, kind=interpKind)                      # Creates a function which returns an interpolated number of values for a given time
    uniTime = np.arange(time[0],time[time.size-1], timeStep)    # Creates a time array of the same time span with evenly spaced time steps
    uniVal = f(uniTime)                                         # Fill the array uniVal with interpolated numbers for all the evenly spaced timesteps
    return [uniTime, uniVal]


def readVariables(filename: str, *variables):
    """ Hämtar tid och variabel-vektorer från en raw-fil i formatet [time, data] där data är 2-dimensionell """

    raw = Ltspice(filename)
    raw._x_dtype = np.float64
    raw._y_dtype = np.float64
    raw.parse()

    time = raw.get_time()
    data = []
    for variable in variables:
        data.append(raw.get_data(variable))
    
    return [time, data]


def plotTimeDiff(filename: str):
    """ Plotta storleken på tidsstegen över tid i den aktiva plotten """

    [time, _] = readVariables(filename)
    diffTime  =  time[1:time.size-1] -   time[0:time.size-2]
    
    plt.plot(time[0:time.size-2], diffTime, linewidth=1)


def plotVars(filename: str, *variables: str, label: str, alpha=0.5):
    """ Plotta en variabel från en datafil i den aktiva ploten """

    [time, data] = readVariables(filename, *variables)

    for d in data:
        plt.plot(time, d, linewidth=1, alpha=alpha, label=label)

def plotFourierFromVector(time: list, data: list, label="", formatString="-", alpha=0.5):
    """ Plotta fourier från data- och tid-vektorer i den aktiva ploten """

    N = len(time)
    yf = fft(data)
    xf = fftfreq(N, time[1]-time[0])[:N//2]
    plt.plot(xf, 2.0/N * np.abs(yf[0:N//2]), formatString, linewidth=1, alpha=alpha, label=label)

    plt.loglog()
    plt.grid()


def plotFourierFromFile(filename: str, variableName: str, label: str, formatString="-", alpha=0.5, resampleTime=1*10**-9):
    """ Plotta fourier för en variabel från en och samma raw-fil i den aktiva ploten  """
    
    raw = Ltspice(filename)
    raw._x_dtype = np.float64
    raw._y_dtype = np.float64
    raw.parse()

    time = raw.get_time()
    data = raw.get_data(variableName)
    [uniTime, uniData] = uniformResample(time, data, resampleTime)

    plotFourierFromVector(uniTime, uniData, label, formatString=formatString, alpha=alpha)

    



# Skriv gärna denna funktion (saveResults())
# Denna funktion ska lägga till invariabler och utvariabler från en utförd simulering till en fil där alla simuleringar sparas.
# Det enklaste sättet är att använda en JSON-fil, där man kan spara ned en dict för vilka parametrar kretsens komponenter hade (ex. R_batt = 1.2)
# och en annan dict för alla möjliga resultat (oönskvärda strömmar/effekt) (ex. den integrerade effekten av common-mode-strömmen)
# Funktionen behöver inte veta vilka dessa är, utan sparar bara ned två dicts som innehåller allt sånt.
# Filen kommer alltså se ut något såhär:
#
# "sims": [                                                                 // En array med simuleringar
#   {                                                                       // Första simuleringen
#   "inparams": {"R_batt": 1.2, "L_batt": 0.05, "gain": 1000},              // Värdena på kretskomponenterna
#   "results": {"batCapPower": 50, "commonModePower": 30}                   // Olika resultat, vi kan senare bestämm vilka dessa är och vilka vi vill ha bara genom att byta namn på dem
#   },                                                                       // Resultaten kan också innehålla vektorer
#   {
#   "inparams": {"R_batt": 1.0, ...},
#   "results": {"batCapPower":30, ...} 
#   }
# ]
#
# Använd JSON-biblioteket, inte text för att generera och ändra filen 
# Kolla här: https://www.geeksforgeeks.org/append-to-json-file-using-python/
# typ: ladda in den existerande json-filen i en dict, lägg till simuleringen, spara ned dicten i json-filen igen. Se andra exemplet i länken
# 
# //Axel

def saveResults(filename: str, inparams: dict, results: dict):
    """ Lägger till simuleringens inparams (kretskomponenters värden) och results (ex. effekten i olika komponenter inom olika frekvensband) i JSON-filen "filename". """
