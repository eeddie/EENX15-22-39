#
#   Functions.py
#
#   Innehåller funktioner som vi använder
#

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import os
from scipy import interpolate
from scipy.fftpack import fft, fftfreq
from ltspice import Ltspice
import json
import operator



def simulateNetlist(netlist: str, name='tmp', removeNetlist=True):
        netlist_file = open('tmp.net', 'w')
        netlist_file.write(netlist)
        netlist_file.close()
        os.system(f'ngspice.exe {name}.net"')                       # NOTE: Lägg till mappen med ngspice i systemvariablerna istället så slipper vi byta
        if removeNetlist: os.remove(f"{name}.net")

def batchNetlist(netlist: str, name = 'tmp', log=False, removeNetlist=True):
        netlist_file = open(f'{name}.net', 'w')
        netlist_file.write(netlist)
        netlist_file.close()
        os.system(f'ngspice_con.exe -b -r {name}.raw {"-o " + name + ".log" if log else ""} {name}.net')   # NOTE: Lägg till mappen med ngspice i systemvariablerna istället så slipper vi byta
        if removeNetlist: os.remove(f"{name}.net")


def uniformResample(time: list, values: list, timeStep=10**-9, interpKind="cubic"):
    """ Samplar om tid- och värdes-vektorer med ett konstant tidssteg. Använder kubisk interpolering vilket krävs för FFT """

    f = interpolate.interp1d(time, values, kind=interpKind)                      # Creates a function which returns an interpolated number of values for a given time
    uniTime = np.arange(time[0],time[time.size-1], timeStep)    # Creates a time array of the same time span with evenly spaced time steps
    uniVal = f(uniTime)                                         # Fill the array uniVal with interpolated numbers for all the evenly spaced timesteps

    return [uniTime, uniVal]


def readVariables(filename: str, *variables: str):
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

    [uniTime, uniData] = uniformResample(raw.get_time(), raw.get_data(variableName), resampleTime)

    plotFourierFromVector(uniTime, uniData, label, formatString=formatString, alpha=alpha)


def energyInFrequencyBand(data: list, lower: float, upper: float, fs=10**9):
    """ Beräknar effekten i ett visst frekvensband. Indatan bör ha uniform sampling med samplingsfrekvens fs. """
    x = np.array(data)
    f, Pxx = sp.signal.periodogram(x, fs=fs)
    ind_min = sp.argmax(f > lower) - 1
    ind_max = sp.argmax(f > upper) - 1
    return sp.trapz(Pxx[ind_min: ind_max], f[ind_min: ind_max])
    


def saveSim(filename: str, modules: list, simParams: dict, results: dict):
    """ Sparar ned simuleringens parametrar till en JSON-fil, lägger till simuleringen om filen redan existerar """

    with open(filename, "w+") as file:                                          # Öppna/Skapa json fil
        try: 
            file_data = json.load(file)                                         # Ladda in JSON-data som python object (list "[]" eller dict "{}")
        except json.JSONDecodeError:
            file_data = []                                                      # Om filen är tom, skapa en tom lista, i denna hamnar alla utförda simuleringar

        file_data.append(                                                       # Lägg till en ny dict, som innehåller datan från simuleringen, i listan 
            {
            "modules": {module.name:module.params for module in modules},       # "modules" är en dict med moduler där modulnamn är key och parameterdicten är value
            "simParams": simParams,                                             # "simParams" är en dict med simuleringsparametrar ex. tstep, tstart, tstop
            "results": results                                                  # Results är en dict med resultat. Ex. {"commonModeCurrent": 50}
            })      
        file.seek(0)                                                            # Börja om filen från början så vi skriver över filen med den nya datan
        json.dump(file_data, file, indent=4)                                    # Dumpa Python-objektet till JSON-filen igen



def plotFromJSON(filename: str, module: str, param: str, result: str, label="", formatString="-", alpha=1):
    """ Plottar datapunkter från ett flertal simuleringar med en kretsparameter som x-axel och en resultatvariabel som y-axel """

    with open(filename, "r+") as file:
        
        file_data = json.load(file)                                             # Om filen är tom kommer denna rad ge JSONDecodeError, vi vill att funktionen avbryter i så fall, därför lämnades denna
        
        # file_data kan sedan indexeras så här
        # file_data[simuleringens index]["modules","simParams" eller "results"][önskad modul, simuleringsparameter eller resultat][önskad parameter i modulen om modul valts]
        # ex.
        # file_data[0]["modules"]["InverterModule"]["R_gate"] ger ex. 1.2
        # file_data[13]["simParam"]["tstep"] ger ex. 10^-9
        # file_data[42]["results"]["commonModeCurrent"] ger ex. 12

        # Fyll x och y med 
        x = []
        y = []
        for sim in file_data:                                                   # Iterera genom alla simuleringar i file_data, d.v.s. JSON-filen
            try:
                x.append(float(sim["modules"][module][param]))                  # Lägg till den valda parameterns värde som en punkt i x-vektorn
                y.append(float(sim["results"][result]))                         # Lägg till det valda resultatet som en punkt i y-vektorn
            except KeyError:                                                    # Om modulen, parametern eller resultatet inte finns i en simulering, hoppa över simuleringen
                pass

        # Sortera x och y efter x
        x, y = zip(*sorted(zip(x,y), key=operator.itemgetter(0)))

        plt.plot(x, y, formatString, label=label, alpha=alpha)
        plt.show()
