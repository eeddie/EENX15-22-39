

import matplotlib.pyplot as plt
import sys

sys.path.append('./Modular/')
from Functions import *

def plotSteadyState():
    plotVars("singleSim_long.raw", "i(VAC_A)", label="$I_A$", timeStep=10e-6, step=100, linewidth=2)
    plotVars("singleSim_long.raw", "i(VAC_B)", label="$I_B$", timeStep=10e-6, step=100, linewidth=2)
    plotVars("singleSim_long.raw", "i(VAC_C)", label="$I_C$", timeStep=10e-6, step=100, linewidth=2)
    plt.title("Steady state-analys")
    plt.xlabel("Tid")
    plt.ylabel("Ström [A]")
    plt.grid()
    plt.legend()
    # Make the x display milliseconds
    plt.gca().xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: '{:.0f} ms'.format(x*1e3)))
    plt.show()

def plotCommonModeCurrent():
    
    time, (vaca, vacb, vacc) = readVariables("./Modular/Examples/singleSim.raw",  "i(VAC_A)", "i(VAC_B)", "i(VAC_C)")
    time, (vaca, vacb, vacc) = uniformResample(time, vaca, vacb, vacc)
    cmc = vaca + vacb + vacc

    # Make one plot in the time domain and a second in the frequency domain side by side
    fig, ax = plt.subplots(1, 2)

    # Set the title to "Fasströmmar"
    fig.suptitle("Common mode-ström")
    # Set the xlabel to "Tid [s]"
    ax[0].set_xlabel("Tid [s]")
    # Set the ylabel to "Ström [A]"
    ax[0].set_ylabel("Ström [A]")

    # Plot vaca with label "Fas A"
    ax[0].plot(time, cmc)

    # Make a fourier of vaca, vacb, and vacc with respect to time and plot them in the second graph

    ax[1].plot(fftfreq(len(time), time[1]-time[0])[:len(time)//2], abs(fft(cmc))[:len(time)//2])
    # Set the plot xscale and yscale to logarithmic
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    # Set the xlabel to "Frequenss [Hz]"
    ax[1].set_xlabel("Frekvens [Hz]")
    # Set the legend to the bottom left
    ax[1].legend(loc="lower left")
    # Show the plot
    plt.show()

def plotPhaseCurrents():
    #time, (vaca, vacb, vacc) = readVariables("./Modular/Examples/singleSim.raw",  "i(VAC_A)", "i(VAC_B)", "i(VAC_C)")
    time, vaca = readVariables("./Modular/Examples/singleSim.raw", "i(VAC_A)")
    _, vacb = readVariables("./Modular/Examples/singleSim.raw", "i(VAC_B)")
    _, vacc = readVariables("./Modular/Examples/singleSim.raw", "i(VAC_C)")

    uniTime, vaca = uniformResample(time, vaca)
    _, vacb = uniformResample(time, vacb)
    _, vacc = uniformResample(time, vacc)
    #time, (vaca, vacb, vacc) = uniformResample(time, vaca, vacb, vacc)

    # Make one plot in the time domain and a second in the frequency domain side by side
    fig, ax = plt.subplots(1, 2)

    # Set the title to "Fasströmmar"
    fig.suptitle("Fasströmmar")
    # Set the xlabel to "Tid [s]"
    ax[0].set_xlabel("Tid [s]")
    # Set the ylabel to "Ström [A]"
    ax[0].set_ylabel("Ström [A]")

    
    ax[0].plot(time, vaca, label="Fas A")
    ax[0].plot(time, vacb, label="Fas B")
    ax[0].plot(time, vacc, label="Fas C")
    ax[0].legend(loc="lower left")


    ax[1].plot(fftfreq(len(time), time[1]-time[0])[:len(time)//2], abs(fft(vaca))[:len(time)//2], label="Fas A")
    ax[1].plot(fftfreq(len(time), time[1]-time[0])[:len(time)//2], abs(fft(vacb))[:len(time)//2], label="Fas B")
    ax[1].plot(fftfreq(len(time), time[1]-time[0])[:len(time)//2], abs(fft(vacc))[:len(time)//2], label="Fas C")
    # Set the plot xscale and yscale to logarithmic
    ax[1].set_xscale("log")
    ax[1].set_yscale("log")
    # Set the xlabel to "Frequenss [Hz]"
    ax[1].set_xlabel("Frekvens [Hz]")
    # Set the legend to the bottom left
    ax[1].legend(loc="lower left")
    # Show the plot
    plt.show()


if __name__ == "__main__":
    # Increase the plot font size
    plt.rcParams.update({'font.size': 16})

    #plotPhaseCurrents()
    #plotCommonModeCurrent()
    plotSteadyState()

    quit()
