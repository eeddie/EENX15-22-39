#
# VisSwitch.py
#
# Visualiserar fyra olika switchmodeller
#

import matplotlib.pyplot as plt
import numpy as np


def VisSwitch():
    # Create a time vector from 0 to 10 seconds with a step of 0.1 seconds
    t = np.arange(0, 10, 0.1)

    # Set plt to use latex
    plt.rc('text', usetex=True)
    # Set plt font size
    plt.rc('font', size=18)
    # set title y offset
    plt.rc('axes', titlepad=30)

    # Create a vector the size of t with values of 0 from start to halfway and infinity from halfway to end
    vinf = np.zeros(t.size)
    vinf[t > 5] = 10**12

    plt.subplot(1,4,1)
    plt.title('$R_{off}=\\infty, R_{on}=0$')
    plt.ylabel("$R$")
    plt.xlabel("$t$")
    plt.plot(t, vinf)
    # set the y limits of the plot from 0 to 10**10
    plt.ylim(-4.8*10**8, 10**10)

    # Create a vector the size of t with values of 10^-10 from start to halfway and 10^10 from halfway to end
    vlim = np.zeros(t.size)+10**-10
    vlim[t > 5] = 10**10

    plt.subplot(1,4,2)
    plt.title('$R_{off}=10^{10}, R_{on}=10^{-10}$')
    plt.ylabel("$R$")
    plt.xlabel("$t$")
    plt.plot(t, vlim)

    # Create a vector the size of t with values of 0 from start to one third, a linear inteprolation between 0 and 10^10 and infinity from two thirds to end
    vlin = np.zeros(t.size) + 10**-10
    # Interpolate betweem 10^-10 and 10^10 for the mmiddle third of vlin
    vlin[t > 2] = np.interp(t[t > 2], [2, 8], [10**-10, 10**10])
    vlin[t > 8] = 10**10
    
    plt.subplot(1,4,3)
    plt.title('Linjär Interpolation')
    plt.ylabel("$R$")
    plt.xlabel("$t$")
    plt.plot(t, vlin)

    # Create a vector the size of t which is a tanh function which is a which transisitons smoothly from 5*10^9 at 0 to 10^10 at 10 with an offset of 5 seconds
    vtanh = np.tanh(t - 5) * 5*10**9 + 5*10**9

    plt.subplot(1,4,4)
    plt.title('Tangens Hyperbolicus ($\\tanh$)')
    plt.ylabel("$R$")
    plt.xlabel("$t$")
    plt.plot(t, vtanh)


    plt.show()