import os
from typing import Any
from Functions import *
from Bfalt import getBfaltAmplitude
import sys


def np_encoder(obj):
    if isinstance(obj, np.generic):
        return obj.item()


def energyAndBfaltFromFile(filename: str, dcI: list[str], voltages: list[str], variables: list[str],
                           ACcurrents: list[str]):
    vars = variables.copy()
    [time, data] = readVariables(filename, *variables, *ACcurrents, *voltages)

    v = []
    for i in range(len(voltages) // 2):
        voltage = data[-2] - data[-1]
        vars.append(voltages[2 * i] + '-' + voltages[2 * i + 1])
        data.pop()
        data.pop()
        v.append(voltage)

    ac = []
    for i in range(len(ACcurrents) // 3):
        vars.append(ACcurrents[3 * i] + '+' + ACcurrents[3 * i + 1] + '+' + ACcurrents[3 * i + 2])
        ACsum = data[-1] + data[-2] + data[-3]
        data.pop()
        data.pop()
        data.pop()
        ac.append(ACsum)

    data.extend(v)
    data.extend(ac)

    uniVariables = {}
    uniTime: Any
    for index, var in enumerate(vars):
        [uniTime, uniData] = uniformResample(time, data[index], 10 ** (-9))
        uniVariables[var] = uniData

    N = len(uniTime)
    tf = fftfreq(N, uniTime[1] - uniTime[0])[0:N // 2]
    yfs = [2.0 / N * np.abs(fft(uniVariables[var])[0:N // 2]) for var in vars]
    Bfalt = BfaltFromFile(filename, dcI[0], dcI[1])

    energy = energyInAllBands(tf, *yfs, *Bfalt)

    return json.dumps(energy, default=np_encoder)


def BfaltFromFile(filename: str, *variables: str):
    [time, data] = readVariables(filename, *variables)
    uniVariables = {}
    uniTime: Any
    for index, var in enumerate(variables):
        [uniTime, uniData] = uniformResample(time, data[index], 10 ** (-9))
        uniVariables[var] = uniData

    N = len(uniTime)
    tf = fftfreq(N, uniTime[1] - uniTime[0])[0:N // 2]
    yfs = [2.0 / N * fft(uniVariables[var])[0:N // 2] for var in variables]

    return getBfaltAmplitude(yfs[0], yfs[1])


def saveModifiedSim(filename: str, modules: list, simParams: dict, variables: list, voltages: list, ACcurrents: list,
                    results: dict):
    """ Sparar ned simuleringens parametrar till en JSON-fil, lägger till simuleringen om filen redan existerar """
    totalVariables = variables.copy()
    voltages.reverse()
    totalVariables.extend(voltages)
    ACcurrents.reverse()
    totalVariables.extend(ACcurrents)
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
                "variables": totalVariables,
                "results": results  # Results är en dict med resultat. Ex. {"commonModeCurrent": 50}
            })
        file.seek(0)  # Börja om filen från början så vi skriver över filen med den nya datan
        json.dump(file_data, file, indent=4)  # Dumpa Python-objektet till JSON-filen igen


if __name__ == "__main__":
    parameterFile = "tmp/params" + str(sys.argv[1]) + ".json"
    simFile = "tmp/sim" + str(sys.argv[1]) + ".raw"
    logFile = "tmp/sim" + str(sys.argv[1]) + ".log"

    with open(parameterFile) as f:
        data = json.load(f)

    variables = ["i(VDC_P)",
            "i(VDC_N)",
            "i(VAC_A)",
            "i(VAC_B)",
            "i(VAC_C)",
            "i(l.xinvgnd.l1)",
            "i(l.xbatgnd.l1)",
            "i(l.xloadgnd.l1)",
            "v(batCase)",
            "v(invCase)",
            "v(loadCase)"]
    voltages = ["v(CMCpos)", "v(CMCneg)"]
    ACcurr = ["i(VAC_A)", "i(VAC_B)", "i(VAC_C)"]
    failed = False
    result: Any
    result = None
    try:
        result = energyAndBfaltFromFile(simFile, ["i(VDC_P)", "i(VDC_N)"], voltages, variables, ACcurr)
    except Exception as e:
        failed = True

    saveModifiedSim("simResults\\sim" + str(sys.argv[1]) + ".json",
                    modules=data[0]["modules"],
                    simParams=data[0]["simParams"],
                    variables=variables,
                    voltages=[voltage1 + '-' + voltage2 for voltage1, voltage2 in zip(voltages[0::2], voltages[1::2])],
                    ACcurrents=[curr1 + '+' + curr2 + '+' + curr3 for curr1, curr2, curr3 in zip(ACcurr[0::3],
                                                                                                 ACcurr[1::3],
                                                                                                 ACcurr[2::3])],
                    results={"energies": result} if not failed else {"log": open(logFile, "r").readlines()}
                    )

    os.remove(logFile)
    os.remove(parameterFile)
    os.remove(simFile)
