
import json
import sys

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





if __name__ == "__main__":
    #combineResultFiles("Results/results", "Results/results_Eddie0.json", "Results/results_Eddie1.json", "Results/results_simon.json")
    #checkFaulty(sys.argv[1])
    quit()
