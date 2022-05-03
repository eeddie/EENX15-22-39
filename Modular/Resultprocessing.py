
import json
import sys
import numpy as np

def combineResultFiles(name: str, *files: str):
    """ Reads all json files in files and combines the contents into a new json file named "name" """
    data = []
    for file in files:
        with open(file, "r") as f:
            # Get all the simulations from the file
            simulations = json.load(f)
            # Add the simulations to the data
            data.extend(simulations)

    with open(name + ".json", "w") as f:
        json.dump(data, f, indent=4)




def checkFaulty(file: str):
    # Load file
    with open(file, "r") as f:
        data = json.load(f)

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

    import numpy as np

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
    import matplotlib.pyplot as plt


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
    #combineResultFiles("Results/results", "Results/results_Eddie0.json", "Results/results_Eddie1.json", "Results/results_simon.json")
    #checkFaulty(sys.argv[1])
    plotFourierSurface("Results/results.json", "ACCommonModeChokeModule", "L_choke", "i(VAC_A)+i(VAC_B)+i(VAC_C)")
