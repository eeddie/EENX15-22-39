
import json
import numpy as np
import matplotlib.pyplot as plt
import os

import json
import numpy as np
import os
import matplotlib.pyplot as plt
from MakePredictions import makePrediction


def convertJSONtoNPY(result_file, directory):
    # Open all json files in directory and its subdirectories and add all simulations to a list
    simulations = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                print(os.path.join(root, file))
                # Replace all ccurences of "[[ with [[ and ]]" with ]] in the file
                with open(os.path.join(root, file), "r") as f:
                    data = f.read()
                    data = data.replace("\"[[", "[[")
                    data = data.replace("]]\"", "]]")
                    with open(os.path.join(root, file), "w") as f:
                        f.write(data)

                # Open the file and extend simulations with its contents
                with open(os.path.join(root, file)) as f:
                    simulations.extend(json.load(f))

    # Walk through simulations and remove all simulations which do not contain the key "DCCommonModeChoke" in "modules"
    i = len(simulations) - 1
    while i >= 0:
        sim = simulations[i]
        if "modules" not in sim:
            simulations.pop(i)
        elif "DCCommonModeChokeModule" not in sim["modules"]:
            simulations.pop(i)
        elif "ACCommonModeChokeModule" not in sim["modules"]:
            simulations.pop(i)
        elif sim["modules"]["BatteryModule"]["Voltage"] != 400:
            simulations.pop(i)
        elif sim["simParams"]["tstep"] != "1ns":
            simulations.pop(i)
        elif sim["simParams"]["tstart"] != "100ms":
            simulations.pop(i)
        elif sim["simParams"]["tstop"] != "110ms":
            simulations.pop(i)
        if sim["results"] is str:
            sim["log"] = sim["results"]
            sim.remove("results")
        if "energies" in sim["results"]:
            sim["results"] = sim["results"]["energies"]
        i -= 1

    # Save simulations to numpy file
    np.save(result_file, simulations, allow_pickle=True)

def combineAllNPY(result_file, directory, *exclude_files):
    # Open all npy files in directory and its subdirectories and add all simulations to a list
    simulations = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".npy") and file not in exclude_files:
                print(os.path.join(root, file))
                # Open the file and extend simulations with its contents
                data = np.load(os.path.join(root, file), allow_pickle=True)
                print(len(data))
                simulations.extend(data)

    # Walk through simulations and remove all simulations which should be filtered out
    print(f"{len(simulations)} before filtering")

    i = len(simulations) - 1
    while i >= 0:
        sim = simulations[i]
        
        # Check if the sim is a dictionary

        if not isinstance(sim, dict):
            print("Sim not dict but " + str(type(sim)))
            simulations.pop(i)
        elif "modules" not in sim:
            print("modules not in sim")
            simulations.pop(i)
        elif "DCCommonModeChokeModule" not in sim["modules"]:
            print("DCCommonModeChokeModule not in sim")
            simulations.pop(i)
        elif "ACCommonModeChokeModule" not in sim["modules"]:
            print("ACCommonModeChokeModule not in sim")
            simulations.pop(i)
        elif sim["modules"]["BatteryModule"]["Voltage"] != 400:
            print("BatteryModule Voltage != 400")
            simulations.pop(i)
        elif sim["simParams"]["tstep"] != "1ns":
            print("tstep != 1ns")
            simulations.pop(i)
        elif sim["simParams"]["tstart"] != "100ms":
            print("tstart != 100ms")
            simulations.pop(i)
        elif sim["simParams"]["tstop"] != "110ms":
            print("tstop != 110ms")
            simulations.pop(i)
        else:
            if sim["results"] is str:
                print("results is str, moving results to log and removing results")
                sim["log"] = sim["results"]
                sim.remove("results")
            if "energies" in sim["results"]:
                print("moving energies to results")
                sim["results"] = sim["results"]["energies"]
        i -= 1

    print(f"{len(simulations)} after filtering")
    # Save simulations to numpy file
    np.save(result_file, simulations, allow_pickle=True)


def plotAll(result_file, module = "ACCommonModeChokeModule", parameter = "L_choke", variable = "i(VAC_A)+i(VAC_B)+i(VAC_C)", color="black", alpha=0.01, linewidth=1, label=""):
    # Load simulations from numpy file
    simulations = np.load(result_file, allow_pickle=True)
    # Get a vector of common mode choke inductance values
    parameterValues = [sim["modules"][module][parameter] for sim in simulations]
    
    # Get the index of the variable
    index = simulations[0]["variables"].index(variable)

    fouriers = []
    middleFrequencies = [(simulations[0]["results"][i][0] + simulations[0]["results"][i][1])/2 for i in range(len(simulations[0]["results"]))]
    for sim in simulations:
        fouriers.append([sim["results"][i][3 + index]/sim["results"][i][2] for i in range(len(sim["results"]))])
        
    # Plot fouriers of all simulations
    plt.loglog(middleFrequencies, fouriers[0], color=color, alpha=alpha, linewidth=linewidth, label=label)
    for fourier in fouriers[1:]:
        plt.loglog(middleFrequencies, fourier, color=color, alpha=alpha, linewidth=linewidth)
    






def checkFaulty(file: str):
    # Load file
    data = np.load(file, allow_pickle=True)

    # Calculate how many sims in data contain a "results" field, and how many contian a "log" field, how many contain both and how many contain neither
    sims_with_results = 0
    sims_with_log = 0
    sims_with_both = 0
    sims_without_either = 0
    for sim in data:
        if "results" in sim:
            sims_with_results += 1
        if "log" in sim:
            sims_with_log += 1
        if "results" in sim and "log" in sim:
            sims_with_both += 1
        if "results" not in sim and "log" not in sim:
            sims_without_either += 1

    # Print results
    print("Sims with results:", sims_with_results)
    print("Sims with log:", sims_with_log)
    print("Sims with both:", sims_with_both)
    print("Sims without either:", sims_without_either)
    print("Total:", len(data))


def plotFourierSurface(file: str, module: str, parameter: str, variable: str):
    """ Plots the fourier surface of the variable in the parameter of the module in the file """
    with open(file, "r") as f:
        data = json.load(f)

        # Get all the simulations that contain the module and parameter
        parameterValues = []
        variableValues = []
        middleFrequencies = []
        for sim in data:
            if module in sim["modules"] and parameter in sim["modules"][module] and variable in sim["variables"]:

                if "ACCommonModeChokeModule" in sim["modules"] and "DCCommonModeChokeModule" in sim["modules"] and sim["modules"]["BatteryModule"]["Voltage"] == 400:
                    parameterValues.append([sim["modules"][module][parameter] for i in range(len(sim["results"]))])
                    
                    # Get the middle frequency from the result file and add it to the middleFrequencies list
                    middleFrequencies.append([(sim["results"][i][0] + sim["results"][i][1])/2 for i in range(len(sim["results"]))])
                    # get the variable index from the variable field
                    variableIndex = sim["variables"].index(variable)
                    variableValues.append([sim["results"][i][3 + variableIndex]/sim["results"][i][2] for i in range(len(sim["results"]))])

    # Plot a surface plot with parameterValues as x, middlefrequencies as y and the variablevalues as z


    fig = plt.figure(1, figsize=(6,6))
    ax = fig.add_subplot(111, projection='3d')

    # Sort parameterValues, middlefrequencies and variableValues by parameterValues
    parameterValues, middleFrequencies, variableValues = zip(*sorted(zip(parameterValues, middleFrequencies, variableValues)))

    parameterValues = np.array(parameterValues)
    middleFrequencies = np.log10(np.array(middleFrequencies))
    variableValues = np.log10(np.array(variableValues))

    parameterValues = np.transpose(parameterValues)
    middleFrequencies = np.transpose(middleFrequencies)
    variableValues = np.transpose(variableValues)

    # Plot a 3D surface with the parameterValues as x, middleFrequencies as y and the variableValues as z
    ax.plot_surface(parameterValues, middleFrequencies, variableValues)

    plt.figure(2)

    # Plot variablevalues transosed as a function of middleFrequencies with the color vector as color
    plt.plot(middleFrequencies, variableValues, color="black", alpha=0.1)

    #plt.plot(np.transpose(middleFrequencies), np.transpose(variableValues), color=color, alpha=0.1)

    plt.show()



if __name__ == "__main__":
    checkFaulty("./Modular/results_v4.npy")
    quit()
    
    #convertJSONtoNPY("results_v1.npy", ".")
    #combineAllNPY("results_v4.npy", ".", "results_v1.npy", "results_v4.npy")
    
    plt.rcParams.update({'font.size': 16})

    
    plt.figure(1)
    plotAll("./Modular/results_v1.npy", color="blue")
    plotAll("./Modular/results_v4.npy", color="red")
    plt.title("AC Common mode-ström för alla simuleringar")
    plt.xlabel("Frekvens [Hz]")
    plt.ylabel("Amplitud")
    plt.legend(loc="lower left")
    makePrediction("i(VAC_A)+i(VAC_B)+i(VAC_C)")


    plt.figure(2)
    plotAll("./Modular/results_v1.npy", variable="i(VAC_A)", color="blue")
    plotAll("./Modular/results_v4.npy", variable="i(VAC_A)", color="red")
    plt.title("Fasström för alla simuleringar")
    plt.xlabel("Frekvens [Hz]")
    plt.ylabel("Amplitud")
    makePrediction("i(VAC_A)")

    plt.show()


    #checkFaulty(sys.argv[1])
    #plotFourierSurface("Klusterskript/results.json", "ACCommonModeChokeModule", "L_choke", "i(VAC_A)+i(VAC_B)+i(VAC_C)")
    quit()
