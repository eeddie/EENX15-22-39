# 
# main.py
# 
# Ingångspunkten för klusterskriptet som mkörs på beräkningsnoder.
#

from subprocess import Popen
import json
import glob
import os

simTime = 24 #Hours

maxConcurrentSims = 16
numberOfSimulations = int(maxConcurrentSims * simTime * 60 / 55) #55 min per sim
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

    # Create a .json file by combining the results of the simulations.
    # Put all json files in simResults in a list
    files = glob.glob("simResults/*.json")
    # Open results.json and read json data
    data = None
    try:
        with open("results.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    # Add the results of the simulations to the json data
    for file in files:
        with open(file, "r") as f:
            simData = json.load(f)[0]
            data.append(simData)
        # Remove the file
        os.remove(file)

    # Write the combined json data to results.json
    with open("results.json", "w") as f:
        json.dump(data, f, indent=4)
        
