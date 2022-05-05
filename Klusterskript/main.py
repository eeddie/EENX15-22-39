# 
# main.py
# 
# Ingångspunkten för klusterskriptet som mkörs på beräkningsnoder.
#

from subprocess import Popen
import glob
import os
import numpy as np

simTime = 24 #Hours

maxConcurrentSims = 64
numberOfSimulations = 128
maxConcurrentFFT = 8

if __name__ == "__main__":
    
    doneSimulations = 0
    while doneSimulations < numberOfSimulations:
        sims = []
        simulationsLeft = min(numberOfSimulations - doneSimulations, maxConcurrentSims)

        # Run simulations --> create .raw files and save a .npy file with the modules and simParams used.
        for i in range(simulationsLeft):
            sims.append(Popen(["python", "SimulateSingle.py", str(doneSimulations + i)], shell=False))
            print("Simulation " + str(doneSimulations + i) + " started")

        # Wait for simulations to finish
        for sim in sims:
            sim.wait()



        # Use the .raw files to create new .npy files that retrieves modules and simParams from the previous .npy file
        # and create a new .npy file that includes the results of the simulation as well as the parameters.
        doneFFT = 0
        while doneFFT < simulationsLeft:
            fftSims = []
            for j in range(min(simulationsLeft - doneFFT, maxConcurrentFFT)):
                fftSims.append(
                    Popen(["python", "FFTRaw.py", str(doneSimulations + doneFFT)], shell=False))
                doneFFT += 1
            for fftSim in fftSims: fftSim.wait()
        doneSimulations += simulationsLeft

    # Create a .npy file by combining the results of the simulations.
    # Put all npy files in simResults in a list
    files = glob.glob(os.path.join(os.path.dirname(__file__), "simResults", "*.npy"))
    
    # Open results.npy and read data if it exists
    if os.path.isfile(os.path.join(os.path.dirname(__file__), "results.npy")):
        data = np.load(os.path.join(os.path.dirname(__file__), "results.npy"), allow_pickle=True)
    else:
        data = None
    
    # Add the results of the simulations to the npy data
    for file in files:
        if data  is None: 
            data = np.array([np.load(file, allow_pickle=True).item])
        else:
            data = np.append(data, np.array([np.load(file, allow_pickle=True).item()]), axis=0)
        # Remove the file
        os.remove(file)

    # Write the combined npy data to results.npy
    np.save(os.path.join(os.path.dirname(__file__), "results.npy"), data)
        
