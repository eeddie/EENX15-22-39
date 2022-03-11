from io import TextIOWrapper
import os
import regex
import time
import winsound
import matplotlib.pyplot as plt

import numpy as np


def VarNotFoundError(Exception):
    pass


def findVarIndex(file, varNames):
    """ Returns the net index of the net in a ngspice raw ascii output file, -1 if not found """
    varIndexes = []
    j = 0
    while j < len(varNames):
        line = file.readline()
        if varNames[j] in line:
            varIndexes.append(int(line.strip().split("	")[0]))
            if j != len(varNames) - 1:
                file.seek(0, 0)
            j += 1
        elif line.strip() == "Values:":
            varIndexes.append(-1)
            if j != len(varNames) - 1:
                file.seek(0, 0)
            j += 1

    return varIndexes


def getVarData(filePath: str, varNames: list[str]):
    """ Returns time and value vectors for a net variable from a ngspice raw ascii output file """
    with open(filePath, "r") as f:
        # Walk down the list of nets/variables and find the index of the one we want.
        varIndexes = findVarIndex(f, varNames)

        # Walk down until we reach "Values:" i.e. the end of the variable list and the start of values
        maxVarIndex = varIndexes[-1]
        line = f.readline().strip()
        while line != "Values:":
            maxVarIndex = int(line.split("	")[0])
            line = f.readline().strip()

        # Here we want to jump every [variable count, e.g. 82] lines and get every value for our variable e.g. 62 as well as time
        time = []
        values = []
        for k in range(len(varIndexes)):
            values.append([])

        # The first line after Values: is the line with the data point index and time data, e.g. 0 0.0000e^-12. Later, timeline will be set to 1 1.24000e^-12, 2 2.48000e^-12 and so on
        timeLine = f.readline()

        # When the time line is empty we have reached the end of the file. At that point we have appended all data and should stop reading it
        while timeLine != "":

            # As mentioned the time data line has been read into timeline already, append the time into the time vector, [0.000e^-12, 1.24000e^-12, ...]
            time.append(float(timeLine.strip().split("		")[1]))

            # Skip all lines between time data and the data of the first variable we want to extract.
            for i in range(varIndexes[0] - 1):
                next(f)
            # We have reached the line where out variable is stored, append the value into the value vector, [0.000e*-3, 1.200e^-3, 9.3000e^-3, ...]
            values[0].append(float(f.readline().strip()))

            # Repeat the process above for all other values
            for j in range(len(varIndexes) - 1):
                for i in range(varIndexes[j + 1] - varIndexes[j] - 1):
                    next(f)
                values[j + 1].append(float(f.readline().strip()))

            # Skip all remaining rows of variables until we reach the new time line.
            for i in range(maxVarIndex - varIndexes[-1]):
                next(f)

            # Read the new time and loop back as long as its not empty.
            timeLine = f.readline()

        # All data has now been collected in the time and value vectors
        f.close()

        return np.array(time), np.array(values)


if __name__ == "__main__":
    startTime = time.time()

    output = getVarData("tmp_noLoad.raw", ["i(l.xload.l3)", "i(l.xload.l2)", "i(l.xload.l1)"])

    print(f"Done!, Elapsed time: {time.time() - startTime}")
    winsound.Beep(440, 1000)

    plt.plot(output[0], output[1][0])
    plt.show()
