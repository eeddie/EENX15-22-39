
import matplotlib.pyplot as plt

import numpy as np

from scipy import fft

from ltspice import Ltspice


if __name__ == "__main__":

    l = Ltspice("tmp_bin.raw")
    l._x_dtype = np.float64
    l._y_dtype = np.float64

    l.parse()

    timeVec = l.get_time()
    currentVec = l.get_data("i(l.xload.l1)")

    plt.figure(0)
    plt.plot(timeVec, currentVec)

    # Plot timestep size
    #diffTime = timeVec[1:timeVec.size-1] - timeVec[0:timeVec.size-2]
    #plt.figure(1)
    #plt.plot(timeVec[0:timeVec.size-2], diffTime)

    plt.show()
