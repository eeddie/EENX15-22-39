#
# Visar en plot på hur interpoleringen av ström/spännings-datan fungerar
#

import matplotlib.pyplot as plt
import numpy as np
import sys
sys.path.append('./Modular/')
from Functions import uniformResample

if __name__=="__main__":
    

    time = np.cumsum((1*np.random.rand(20)+0))              # Skapa tidsvektor med slumpmässigt tidssteg [0,1) 
    time[0] = 0                                             # Flytta första punkten bakåt till 0
    val = np.cumsum((0.1*(np.random.rand(20)-0.5)))+0.5     # Skapa y-data som startar vi 0.5 och där varje punkt varierar ±5% från föregående punkt

    [uniTime, uniVal] = uniformResample(time, val, 1)

    plt.figure(0)
    plt.plot(time, val, 'o-', markersize=7, linewidth=4, label="Non-uniform time")
    plt.plot(uniTime, uniVal, 'o-', markersize=7, linewidth=3, label="Uniform time")
    plt.ylim(0, 1)
    plt.legend()
    plt.xticks(np.arange(time[time.size-1]))
    plt.grid(axis='x')
    plt.show()