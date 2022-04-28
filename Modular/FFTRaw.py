from typing import Any
from Functions import *
from Bfalt import getBfaltAmplitude

import sys


def np_encoder(obj):
    if isinstance(obj, np.generic):
        return obj.item()


def energyAndBfaltFromFile(filename: str, dcI: list[str], *variables: str):
    [time, data] = readVariables(filename, *variables)
    uniVariables = {}
    uniTime: Any
    for index, var in enumerate(variables):
        [uniTime, uniData] = uniformResample(time, data[index], 10 ** (-9))
        uniVariables[var] = uniData

    N = len(uniTime)
    tf = fftfreq(N, uniTime[1] - uniTime[0])[0:N // 2]
    yfs = [2.0 / N * np.abs(fft(uniVariables[var])[0:N // 2]) for var in variables]
    Bfalt = BfaltFromFile(filename, dcI[0], dcI[1])

    energy = energyInAllBands(tf,*yfs, *Bfalt)

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


def saveModifiedSim(filename: str, modules: list, simParams: dict, variables:list, results: dict):
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
                "variables":variables,
                "results": results  # Results är en dict med resultat. Ex. {"commonModeCurrent": 50}
            })
        file.seek(0)  # Börja om filen från början så vi skriver över filen med den nya datan
        json.dump(file_data, file, indent=4)  # Dumpa Python-objektet till JSON-filen igen


if __name__ == "__main__":
    parameterFile = "simResults/params" + str(sys.argv[1]) + ".json"
    simFile = "sim" + str(sys.argv[1]) + ".raw"
    logFile = "sim" + str(sys.argv[1]) + ".log"

    with open(parameterFile) as f:
        data = json.load(f)

    variables = ["i(l.xload.l1)", "i(VDC_P)", "i(VDC_N)"]
    failed = False
    result: Any
    try:
        result = energyAndBfaltFromFile(simFile, ["i(VDC_P)", "i(VDC_N)"], *variables)
    except Exception as e:
        failed = True
        print(e)
        result = open(logFile, "r").readlines()

    saveModifiedSim("simResults\\sim" + str(sys.argv[1]) + ".json",
                    modules=data[0]["modules"],
                    simParams=data[0]["simParams"],
                    variables = variables,
                    results={"energies": result} if not failed else {"log": result}
                    )

    os.remove(logFile)
    os.remove(parameterFile)
    os.remove(simFile)