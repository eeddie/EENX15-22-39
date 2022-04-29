# 
# main.py
# 
# Ingångspunkten för klusterskriptet som mkörs på beräkningsnoder.
#

import os
from subprocess import Popen

numberOfSimulations = 16
maxConcurrentSims = 16
maxConcurrentFFT = 4

if __name__ == "__main__":
    
    doneSimulations = 0
    while doneSimulations < numberOfSimulations:
        sims = []
        simulationsLeft = min(numberOfSimulations - doneSimulations, maxConcurrentSims)

        # Run simulations --> create .raw files and save a .json file with the modules and simParams used.
        for i in range(simulationsLeft):
            sims.append(Popen(["python", "SimulateSingle.py", str(doneSimulations + i)], shell=True))
            print("Simulation " + str(doneSimulations + i) + " started")

        # Wait for simulations to finish
        for sim in sims:
            sim.wait()

        # Use the .raw files to create new .json files that retrieves modules and simParams from the previous .json file
        # and create a new .json file that includes the results of the simulation as well as the parameters.
        doneFFT = 0
        while doneFFT < simulationsLeft:
            fftSims = []
            for j in range(min(simulationsLeft - doneFFT, maxConcurrentFFT)):
                fftSims.append(
                    Popen(["python", "FFTRaw.py", str(doneSimulations + doneFFT)], shell=True))
                doneFFT += 1
            for fftSim in fftSims: fftSim.wait()
        doneSimulations += simulationsLeft

    import glob

    # Create a .json file by combining the results of the simulations.
    files = glob.glob(os.path.join("simResults", "*.json"))
    with open("results.json", "w") as f:
        f.write("[\n")
        for index, file in enumerate(files):
            with open(file, "r") as f2:
                f.write(f2.read()[1:-1] + (",\n" if index + 1 < numberOfSimulations else ""))
            os.remove(file)
        f.write("]")