import json
from typing import Any

from ltspice import FileSizeNotMatchException

from Simulate import *
import sys


def np_encoder(obj):
    if isinstance(obj, np.generic):
        return obj.item()

def energyFromFile(filename: str, dcI: list[str], *variables: str):
    [time, data] = readVariables(filename, *variables)
    uniVariables = {}
    uniTime: Any
    for index, var in enumerate(variables):
        [uniTime, uniData] = uniformResample(time, data[index], 10 ** (-9))
        uniVariables[var] = uniData

    N = len(uniTime)
    tf = fftfreq(N, uniTime[1] - uniTime[0])[0:N // 2]
    yfs = [2.0 / N * np.abs(fft(uniVariables[var])[0:N // 2]) for var in variables]

    energy = energyInAllBands(tf, *yfs)
    Bfalt = processedEnergyFromFile(filename, dcI[0], dcI[1])

    assert len(energy) == len(Bfalt)
    for i in range(len(energy)):
        energy[i].append(Bfalt[i])

    return json.dumps(energy, default=np_encoder)


def energyInDCBands(xf, *yf):
    limits = [0, 10000, 150000, 30000000, 400000000]
    bandwidths = [100 * 10 ** p for p in range(5)]
    frequencies = []
    for i in range(len(limits) - 1):
        for j in range(limits[i], limits[i + 1], bandwidths[i]):
            frequencies.append(j)
    frequencies.append(limits[-1])

    energy = []
    for index, startFreq in enumerate(frequencies):
        if startFreq == frequencies[-1]:
            break
        endFreq = frequencies[index + 1]

        lo = find_nearest_frequency(array=xf, value=startFreq)
        hi = find_nearest_frequency(array=xf, value=endFreq)

        bandEnergy = [sum_energy(yf=entry, lower=lo, upper=hi) for entry in yf]

        energy.append([*bandEnergy])
    return energy


from Bfalt import getBfaltAmplitude


def processedEnergyFromFile(filename: str, *variables: str):
    [time, data] = readVariables(filename, *variables)
    uniVariables = {}
    uniTime: Any
    for index, var in enumerate(variables):
        [uniTime, uniData] = uniformResample(time, data[index], 10 ** (-9))
        uniVariables[var] = uniData

    N = len(uniTime)
    tf = fftfreq(N, uniTime[1] - uniTime[0])[0:N // 2]
    yfs = [2.0 / N * np.abs(fft(uniVariables[var])[0:N // 2]) for var in variables]

    return getBfaltAmplitude(energyInDCBands(tf, *yfs)).tolist()


def saveModifiedSim(filename: str, modules: list, simParams: dict, results: dict):
    """ Sparar ned simuleringens parametrar till en JSON-fil, lägger till simuleringen om filen redan existerar """

    with open(filename, "w+") as file:  # Öppna/Skapa json fil
        try:
            file_data = json.load(file)  # Ladda in JSON-data som python object (list "[]" eller dict "{}")
        except json.JSONDecodeError:
            file_data = []  # Om filen är tom, skapa en tom lista, i denna hamnar alla utförda simuleringar

        file_data.append(  # Lägg till en ny dict, som innehåller datan från simuleringen, i listan
            {
                "modules": modules,
                # "modules" är en dict med moduler där modulnamn är key och parameterdicten är value
                "simParams": simParams,  # "simParams" är en dict med simuleringsparametrar ex. tstep, tstart, tstop
                "results": results  # Results är en dict med resultat. Ex. {"commonModeCurrent": 50}
            })
        file.seek(0)  # Börja om filen från början så vi skriver över filen med den nya datan
        json.dump(file_data, file, indent=4)  # Dumpa Python-objektet till JSON-filen igen


if __name__ == "__main__":
    parameterFile = "simResults\\params" + str(sys.argv[1]) + ".json"
    simFile = "sim" + str(sys.argv[1]) + ".raw"

    with open(parameterFile) as f:
        data = json.load(f)

    result: Any
    try:
        result = energyFromFile(simFile,["i(VDC_P)", "i(VDC_N)"], "i(l.xload.l1)","i(VDC_P)", "i(VDC_N)")
    except Exception and UnicodeDecodeError:
        result = None
    saveModifiedSim("simResults\\sim" + str(sys.argv[1]) + ".json",
                    modules=data[0]["modules"],
                    simParams=data[0]["simParams"],
                    results={
                        "energies": result
                    }
                    )

    os.remove(parameterFile)
    os.remove(simFile)
