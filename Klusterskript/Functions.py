#
#   Functions.py
#
#   Innehåller funktioner som vi använder
#

import numpy as np
import scipy as sp
import os
from scipy import interpolate
from scipy.fftpack import fft, fftfreq
from ltspice import Ltspice
import json
import math


def batchNetlist(netlist: str, name = 'tmp', log=False, removeNetlist=True):
        netlist_file = open(f'{name}.net', 'w')
        netlist_file.write(netlist)
        netlist_file.close()
        os.system(f'ngspice -b -r {name}.raw {"-o " + name + ".log" if log else ""} {name}.net')   # NOTE: Lägg till mappen med ngspice i systemvariablerna istället så slipper vi byta
        if removeNetlist: os.remove(f"{name}.net")
        repairRaw(f"{name}.raw")


def uniformResample(time: list, values: list, timeStep=10 ** -9, interpKind="cubic"):
    """ Samplar om tid- och värdes-vektorer med ett konstant tidssteg. Använder kubisk interpolering vilket krävs för FFT """
    f = interpolate.interp1d(time, values,
                             kind=interpKind)  # Creates a function which returns an interpolated number of values for a given time
    uniTime = np.arange(time[0], time[time.size - 1],
                        timeStep)  # Creates a time array of the same time span with evenly spaced time steps
    uniVal = f(uniTime)  # Fill the array uniVal with interpolated numbers for all the evenly spaced timesteps

    return [uniTime, uniVal]

# A function which returns the vectors in the specified window from xMin to xMax
def window(time: list, *values: list, xMin, xMax):
    """ Kortar ner de angivna vektorerna inom xMin och xMax """

    # Find the index in time which is closest to xMin
    xMinIndex = np.argmin(np.abs(time - xMin)) - 1
    # Find the index in time which is the closest to xMax plus one
    xMaxIndex = np.argmin(np.abs(time - xMax)) + 1

    return [time[xMinIndex:xMaxIndex], [value[xMinIndex:xMaxIndex] for value in values]]


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


def repairRaw(*filenames: str):
    """ Reparera en raw-fil """

    for filename in filenames:

        # Open the file as binary
        with open(filename, "rb") as f:
            # Split the data into ascii header and binary data 
            header, data = f.read().split(bytearray("Binary:", "utf-8"),1)
            # Convert the header to a string
            header = header.decode('utf-8') + "Binary:"
            
            # Check if the header contains a line "Variables:"
            if "\nVariables:" not in header:
                # Find the line in the header which ends with "Variables:" and add a newline before "Variables:"
                header = header.replace("Variables:", "\nVariables:").replace("\nVariables:", "Variables:", 1)

            # Write the header and data to the file
            with open(filename, "wb") as f:
                f.write(header.encode('utf-8'))
                f.write(data)



# Alternative method
def energyInFrequencyBand(data: list, lower: float, upper: float, fs=10 ** 9):
    """ Beräknar effekten i ett visst frekvensband. Indatan bör ha uniform sampling med samplingsfrekvens fs. """
    x = np.array(data)
    f, Pxx = sp.signal.periodogram(x, fs=fs)
    ind_min = sp.argmax(f > lower) - 1
    ind_max = sp.argmax(f > upper) - 1
    return sp.trapz(Pxx[ind_min: ind_max], f[ind_min: ind_max])


# Finds the frequency closest to a specified frequency, in a sorted np array of frequencies
def find_nearest_frequency(array, value):
    index = np.searchsorted(array, value, side="left")
    if index > 0 and (index == len(array) or math.fabs(value - array[index - 1]) < math.fabs(value - array[index])):
        return index - 1
    else:
        return index


# Sums the 'energy' in a frequency band. Needs indices of first and last frequency in a band, and vector containing the absolute values of an FFT
def sum_energy(yf, lower, upper):
    energy = 0
    for i in range(lower, upper + 1):
        energy += yf[i]
    return energy


# Returns a 2d array with every row in the format: [flo fhi sum numofpoints].
# Deecated
def energy_in_interesting_frequencies(xf, yf):
    startLowFreq = 100 * 10 ** 3
    startHighFreq = 30 * 10 ** 6
    endHighFreq = 100 * 10 ** 6

    LFbw = 9 * 10 ** 3
    HFbw = 120 * 10 ** 3

    lowFrequencies = []
    counter = startLowFreq
    while counter < startHighFreq:
        lowFrequencies.append(counter)
        counter += LFbw

    highFrequencies = []
    counter = startHighFreq
    while counter < endHighFreq:
        highFrequencies.append(counter)
        counter += HFbw

    energy = []
    for freq in lowFrequencies:
        lower = find_nearest_frequency(array=xf, value=freq)
        hfreq = startHighFreq
        if freq + LFbw < startHighFreq:
            hfreq = freq + LFbw
        upper = find_nearest_frequency(array=xf, value=hfreq)
        numOfPoints = upper - lower + 1
        bandEnergy = sum_energy(yf=yf, lower=lower, upper=upper)
        energy.append([freq, hfreq, bandEnergy, numOfPoints])

    for freq in highFrequencies:
        lower = find_nearest_frequency(array=xf, value=freq)
        hfreq = freq + HFbw
        upper = find_nearest_frequency(array=xf, value=hfreq)
        numOfPoints = upper - lower + 1
        bandEnergy = sum_energy(yf=yf, lower=lower, upper=upper)
        energy.append([freq, hfreq, bandEnergy, numOfPoints])

    return energy

# Returns a 2d array with every row in the format: [flo fhi numofpoints *sums] where sums is the sum for several variables
# From 100Hz to 400MHz
# xf is a vector with the frequencies for one or more FFTs
# *yf is a tuple of vectors containing the absolute values of an FFT
def energyInAllBands(xf, *yf):
    limits = [0, 10000, 150000, 30000000, 400000000]
    bandwidths = [100*10**p for p in range(5)]
    frequencies = []
    for i in range(len(limits)-1):
        for j in range(limits[i],limits[i+1],bandwidths[i]):
            frequencies.append(j)
    frequencies.append(limits[-1])

    energy = []
    for index, startFreq in enumerate(frequencies):
        if startFreq == frequencies[-1]:
            break
        endFreq = frequencies[index + 1]

        lo = find_nearest_frequency(array=xf, value=startFreq)
        hi = find_nearest_frequency(array=xf, value=endFreq) - 1
        numOfPoints = hi - lo + 1
        bandEnergy = [sum_energy(yf=entry, lower=lo, upper=hi) for entry in yf]

        energy.append([startFreq, endFreq, numOfPoints, *bandEnergy])

    return energy


# Returns a 2d array with every row in the format: [flo fhi sum numofpoints]. 
# From 100Hz to 400MHz
# Used on rawfile
def energyFromFile(filename: str, *variables:str):
    [time, data] = readVariables(filename, *variables)
    uniVariables = {}
    uniTime = None
    for index, var in enumerate(variables):
        [uniTime, uniData] = uniformResample(time,data[index],10**(-9))
        uniVariables[var] = uniData
    
    N = len(uniTime)
    tf = fftfreq(N, uniTime[1]-uniTime[0])[0:N//2]
    yfs = [2.0/N * np.abs(fft(uniVariables[var])[0:N//2]) for var in variables]

    return energyInAllBands(tf, *yfs)

def saveSim(filename: str, modules, simParams: dict, variables: list = None, results: dict = None, log: str = None):
    """ Sparar ned simuleringens parametrar till en JSON-fil, lägger till simuleringen om filen redan existerar """

    # Create the folders if they don't exist
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, "w+") as file:  # Öppna/Skapa json fil
        try:
            file_data = json.load(file)  # Ladda in JSON-data som python object (list "[]" eller dict "{}")
        except json.JSONDecodeError:
            file_data = []  # Om filen är tom, skapa en tom lista, i denna hamnar alla utförda simuleringar

        # Om modules är en modullista och inte en färdig dict, ta bort "virtuella" moduler (ex. NoDCCommonModeChoke) och gör om till dict

        if isinstance(modules, list):
            i = len(modules)-1
            while i > 0:
                if not hasattr(modules[i], "params"): modules.pop(i)
                i -= 1
            modules = {module.name: module.params for module in modules}

        simDict = {
            "modules": modules, # "modules" är en dict med moduler där modulnamn är key och parameterdicten är value
            "simParams": simParams,  # "simParams" är en dict med simuleringsparametrar ex. tstep, tstart, tstop   
        }
        if variables is not None: simDict["variables"] = variables
        if results is not None: simDict["results"] = results
        if log is not None: simDict["log"] = log

        file_data.append(simDict) # Lägg till den nya simuleringen i listan
        file.seek(0)  # Börja om filen från början så vi skriver över filen med den nya datan
        json.dump(file_data, file, indent=4)  # Dumpa Python-objektet till JSON-filen igen


def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()


def saveBandEnergies(filename: str, energies: list):
    """ Sparar ned simuleringens parametrar till en JSON-fil, lägger till simuleringen om filen redan existerar """

    with open(filename, "w+") as file:  # Öppna/Skapa json fil
        try:
            file_data = json.load(file)  # Ladda in JSON-data som python object (list "[]" eller dict "{}")
        except json.JSONDecodeError:
            file_data = []  # Om filen är tom, skapa en tom lista, i denna hamnar alla utförda simuleringar

        for i in range(len(energies)):
            file_data.append(energies[i])   # Lägg till en ny dict, som innehåller datan från simuleringen, i listan
        file.seek(0)  # Börja om filen från början så vi skriver över filen med den nya datan

        json.dump(file_data, file, default=np_encoder)


# Returns a list of mosfet models present in MOS.lib
def getMOSFETs(libFile="./Modular/libs/MOSFET/MOS.lib"):
    mosfetList = []
    with open(libFile, "r") as f:
        for line in f:
            if line.startswith(".model"):
                mosfetList.append(line.split()[1])
    return mosfetList
