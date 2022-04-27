import os
from subprocess import Popen

if __name__ == "__main__":
    numberOfSimulations = 128

    maxSims = 32
    maxFFT = 8
    doneSimulations = 0
    while doneSimulations < numberOfSimulations:
        sims = []
        simulationsLeft = min(numberOfSimulations - doneSimulations, maxSims)

        # Run simulations --> create .raw files and save a .json file with the modules and simParams used.
        for i in range(simulationsLeft):
            sims.append(Popen(["python", "C:/EENX15/Modular/SimulateRaw.py", str(doneSimulations + i)], shell=True))
            print("Simulation " + str(doneSimulations + i) + " started")

        # Wait for simulations to finish
        for sim in sims:
            sim.wait()

        # Use the .raw files to create new .json files that retrieves modules and simParams from the previous .json file
        # and create a new .json file that includes the results of the simulation as well as the parameters.
        doneFFT = 0
        while doneFFT < simulationsLeft:
            fftSims = []
            for j in range(min(simulationsLeft - doneFFT, maxFFT)):
                fftSims.append(
                    Popen(["python", "C:/EENX15/Modular/FFTRaw.py", str(doneSimulations + doneFFT)], shell=True))
                doneFFT += 1
            [fftSim.wait() for fftSim in fftSims]
        doneSimulations += simulationsLeft

    import glob

    # Create a .json file by combining the results of the simulations.
    files = glob.glob("C:/EENX15/Modular/simResults/*.json")
    with open("C:/EENX15/Modular/results.json", "w") as f:
        f.write("[\n")
        for file in files:
            with open(file, "r") as f2:
                f.write(f2.read()[1:-1] + ",\n")
            os.remove(file)
        f.write("]")
