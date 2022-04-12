from Simulate import *
import sys


def np_encoder(obj):
    if isinstance(obj, np.generic):
        return obj.item()


def saveAllBands(filename: str):
    [time0, data0] = readVariables(filename, "i(l.xload.l1)")
    [uniTime0, uniData0] = uniformResample(time0, data0, timeStep=10 ** (-9))
    N = len(uniTime0)
    fftcurrent = 2.0 / N * np.abs(fft(uniData0)[0, 0:N // 2])
    tf = fftfreq(N, uniTime0[1] - uniTime0[0])[0:N // 2]

    return json.dumps(energyInAllBands(tf, fftcurrent), default=np_encoder)


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
    file = "simResults\\params" + str(sys.argv[1]) + ".json"

    with open(file) as f:
        data = json.load(f)
    os.remove(file)

    saveModifiedSim("simResults\\sim" + str(sys.argv[1]) + ".json",
                    modules=data[0]["modules"],
                    simParams=data[0]["simParams"],
                    results={"energies": saveAllBands("sim" + str(sys.argv[1]) + ".raw")}
                    )

    os.remove("sim" + str(sys.argv[1]) + ".raw")
