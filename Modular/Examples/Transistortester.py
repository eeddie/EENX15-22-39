#
# Transistortester.py
# Gör de jämförelser mellan switcharna som används i rapporten
# Denna är sjukt rörig och kräver modifiering av skriptet för att få ut varje plot, borde kanske göra så att man kan köra skriptet en gång och få ut alla plots
# 

import matplotlib.pyplot as plt
import sys
import numpy as np
import gc
import multiprocessing as mp

sys.path.append('./Modular/')
from Functions import *


# MOSFETS for the simple, built-in mosfet component
# SPA11N60C3    Vds=650 Id = 11 A  Har en parameter subthresh som ngspice inte förstår sig på
# STP8NM60      Vds=650 Id = 8 A
# STW11NM80     Vds=800 Id = 11 A

# Infineon MOSFET, i.e. subscircuit mosfet model
# IPWS65R022CFD7A

# Infineon IGBT, i.e. subcircuit IGBT model
# IKW50N60H5


def runBasicSim(
    switchString,               # The lines of spice netlist code which defines the switch. Connects to the nets PWM, Drain and 0 (Ground)
    Gain = 1000,               # The tanh gain, i.e. sharpness of the PWM signal
    R_Drain = 10,               # Drain resistance, i.e. the resistance limiting Ids (the drain-source-current)
    filename = "bss"            # The simulation outputs a {filename}.raw file
):
    """ Runs a simulation of the general circuit with no transistor specified """

    netlist = f""".title Basic Test
BSin      Ph    0 V= sin(2*Pi*100*time)
BE_PWM    PWM   0 V= 15*tanh({Gain}*(V(Ph)-0.03-V(Triangle)))
BTri Triangle 0 V= (2/Pi)*asin(sin(2*Pi*10000*Time))
V1 in 0 400
Rd in Drain {R_Drain}
{switchString}

.options abstol=10n reltol=1m itl4=30

.save V(PWM), I(V1), V(Gate)

.tran 0.1ns 10ms
.end """

    batchNetlist(netlist, filename)


def runSwitchSim(
    filename = "bss_switch",
    Gain = 1000,
    R_on = "20m",
    V_t = "0",                    # Threshhold voltage where the switch turns on or off
):
    runBasicSim(filename = filename, Gain = Gain,
        switchString = f"""S1 Drain 0 PWM 0 swmod ON
.model swmod sw vt={V_t} ron={R_on}""")


def runVaristorSim(
    filename = "bss_varistor",
    Gain = 1000,
    R_off = 130*10**3,  # Avresistans plockad från IGBT:ns läckström i egenskapstabellen
    R_on = 20*10**-3,   # Påresistans plockad ur grafen för IGBT:ns Vce/Ic vid Vge=10
    V_off = 5,
    V_on = 7
):
    runBasicSim(filename=filename, Gain = Gain,
        switchString = f"""R1 Drain 0  r='V(PWM) > {V_on} ? {R_on} : (V(PWM) < {V_off} ? {R_off} : {(R_off-R_on)/(V_on-V_off)}*({V_off}-V(PWM)))'"""
        )

def runMOSFETSim(
    filename = "bss_mosfet",
    Gain = 1000,
    MOSType = "STP8NM60",
    R_Gate = 1.0,
):
    runBasicSim(filename=filename, Gain = Gain,
        switchString = f"""Rg PWM Gate {R_Gate}
M1 Drain Gate 0 0 {MOSType}
.lib /Modular/libs/MOSFET/MOS.lib""")

def runIGBTSim(
    filename = "bss_igbt",
    Gain = 1000,
    IGBTType = "rgw00ts65chr",
    R_Gate = 1,
    R_Drain = 10,
):
    runBasicSim(filename=filename, Gain = Gain, R_Drain=R_Drain,
        switchString = f"""Rg PWM Gate {R_Gate}
X1 Drain Gate 0 {IGBTType}
.lib /Modular/libs/IGBT/{IGBTType}.lib""")

def runInfineonMOSFETSim(
    filename = "bss_mosfet_infineon",
    Gain = 1000,
    MOSType = "IPWS65R022CFD7A",
    R_Gate = 1.0,
):
    runBasicSim(filename=filename + "_L0", Gain = Gain,
        switchString = f"""Rg PWM Gate {R_Gate}
X1 Drain Gate 0 {MOSType}_L0
.lib /Modular/libs/MOSFET/IFX_CFD7A_650V.lib""")


def runParallelIGBTSim(R_Drain):
        runIGBTSim(filename = f"bss_igbt_{R_Drain}", R_Drain = R_Drain)


def runSwitchSimWithGain(filename, gain): runSwitchSim(filename = filename, Gain = gain)
def runVaristorSimWithGain(filename, gain): runVaristorSim(filename = filename, Gain = gain)
def runMOSFETSimWithGain(filename, gain): runMOSFETSim(filename = filename, Gain = gain)
def runInfineonMOSFETSimWithGain(filename, gain): runInfineonMOSFETSim(filename = filename, Gain = gain)
def runIGBTSimWithGain(filename, gain): runIGBTSim(filename = filename, Gain = gain)
def runParallelGainComparisonSims(*gains):
    """ Run every simulation with every gain in parallell """
    processes = []
    for gain in gains:
        processes.append(mp.Process(target = runSwitchSimWithGain, args = (f"bss_switch_{gain}", gain)))
        processes.append(mp.Process(target = runVaristorSimWithGain, args = (f"bss_varistor_{gain}", gain)))
        processes.append(mp.Process(target = runMOSFETSimWithGain, args = (f"bss_mosfet_{gain}", gain)))
        processes.append(mp.Process(target = runInfineonMOSFETSimWithGain, args = (f"bss_mosfet_infineon_{gain}", gain)))
        processes.append(mp.Process(target = runIGBTSimWithGain, args = (f"bss_igbt_{gain}", gain)))
    for process in processes:
        process.start()
    for process in processes:
        process.join()
    



    
    





def plotSideBySideStepOf(names: list, filenames: list):
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 16})
    
    xlims = [[4.7466*10**-3, 4.7474*10**-3],
             [4.8021*10**-3, 4.8029*10**-3]]
    
    titles = ["Stigande flank", "Fallande flank"]
    for f in [0,1]:
        fig, axs = plt.subplots(1,len(filenames))
        fig.suptitle(titles[f])

        for i in range(len(axs)):
            ax = axs[i]
            ax2 = ax.twinx()
            fn = filenames[i]
            name = names[i]

            (time, (pwm, ids)) = readVariables(fn, "V(PWM)", "I(V1)")
            (time, (pwm, ids)) = window(time, pwm, ids, xMin=xlims[f][0], xMax=xlims[f][1])
            ids = -ids

            ax.title.set_text(name)
            ax.plot(time-xlims[f][0], pwm, color="black", label="$V_{pwm}$", linewidth=1, alpha=0.4)
            # set x-axis label
            ax.set_xlabel("Tid [s]")
            # move the label down a little
            ax.xaxis.labelpad = 20
            
            # set y-axis label
            if i == 0 : ax.set_ylabel("$V_{pwm}$ [V]",color="black")
            # # make a plot with different y-axis using second axis object
            ax2.plot(time-xlims[f][0], ids,color="blue", label="$I_{ds}$", linewidth=2)
            if i == len(axs)-1: ax2.set_ylabel("$I_{ds}$ [A]",color="blue")

            plt.xlim(0, xlims[f][1]-xlims[f][0])
            ax.set_xticks(np.linspace(0, xlims[f][1]-xlims[f][0],5))

    plt.show()


def plotOnTopStepOf(names: list, filenames: list):
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')
    plt.rcParams.update({'font.size': 16})
    
    xlims = [[4.7466*10**-3, 4.7474*10**-3],
             [4.8021*10**-3, 4.8029*10**-3]]
    
    titles = ["Stigande flank", "Fallande flank"]
    for f in [0,1]:
        fig, ax = plt.subplots(1,1)
        fig.suptitle(titles[f])

        ax2 = ax.twinx()

        for i in range(len(filenames)):
            fn = filenames[i]
            name = names[i]

            time = []
            ids = []

            
            if i == 0:
                time, (pwm, ids) = readVariables(fn, "V(PWM)", "I(V1)")
                time, (pwm, ids) = window(time, pwm, ids, xMin=xlims[f][0], xMax=xlims[f][1])
                ax.plot(time-xlims[f][0], pwm, color="black", label=name, linewidth=1, alpha=0.4)
                ax.set_xlabel("Tid [s]")
                # move the label down a little
                ax.xaxis.labelpad = 20
                ax.set_ylabel("$V_{pwm}$ [V]",color="black")
                ax2.set_ylabel("$I_{ds}$ [A]",color="black")
                del pwm
            else:
                time, (ids,) = readVariables(fn, "I(V1)")
                time, (ids,) = window(time, ids, xMin=xlims[f][0], xMax=xlims[f][1])
            
            
            ids = -ids

            ax2.plot(time-xlims[f][0], ids, label=name, linewidth=2)
            
            plt.xlim(0, xlims[f][1]-xlims[f][0])
            ax.set_xticks(np.linspace(0, xlims[f][1]-xlims[f][0],5))

    plt.show()


def plotSideBySideFFTOf(names: list, filenames: list):
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    for i in range(len(filenames)):

        fn = filenames[i]
        name = names[i]

        plt.subplot(1,5,i+1)
        plt.title(name)

        # Set the figure to be as wide as the screen
        fig = plt.gcf()
        fig.set_size_inches(18, 5)
        

        time, (pwm, ids) = readVariables(fn, "V(PWM)", "I(V1)")
        ids = -ids

        time, (pwm, ids) = uniformResample(time, pwm, ids, timeStep=10**-9) 

        N = len(time)
        xf = fftfreq(N, time[1]-time[0])[:N//2]

        fft_pwm = fft(pwm)
        fft_ids = fft(ids)

        plt.loglog(xf, 2.0/N * np.abs(fft_pwm[0:N//2]), color="black", label="$V_{pwm}$", linewidth=1, alpha=0.4)
        plt.loglog(xf, 2.0/N * np.abs(fft_ids[0:N//2]), color="blue", label="$I_{ds}$", linewidth=2)

        plt.ylim(10**-12, 10**4)
        plt.xticks([10**x for x in range(0,9)])
        plt.grid(True)
        plt.legend(loc = "lower left")

    plt.show()


def plotOnTopFFTOf(names: list, filenames: list):
    plt.rcParams.update({'font.size': 16})

    for i in range(len(filenames)):

        fn = filenames[i]
        name = names[i]

        # Set the figure to be as wide as the screen
        fig = plt.gcf()
        fig.set_size_inches(18, 5)
        

        (time, (pwm, ids)) = readVariables(fn, "V(PWM)", "I(V1)")
        ids = -ids

        _, pwm = uniformResample(time, pwm, 10**-9)
        time, ids = uniformResample(time, ids, 10**-9)

        N = len(time)
        xf = fftfreq(N, time[1]-time[0])[:N//2]

        fft_ids = fft(ids)

        if name == "IGBT":
            plt.loglog(xf, 2.0/N * np.abs(fft_ids[0:N//2]), label=name, color="black", alpha=0.5)
        else:
            plt.loglog(xf, 2.0/N * np.abs(fft_ids[0:N//2]), label=name, alpha=0.5)

    plt.ylim(10**-12, 10**4)
    plt.xticks([10**x for x in range(0,9)])
    plt.grid(True)
    plt.legend(loc = "lower left")

    plt.show()
 


if __name__ == "__main__":
    plt.rcParams.update({'font.size': 16})
    # Denna funktion ska följa dokumentets disposition
    # Kommentera in varje steg du vill köra

    #runParallelGainComparisonSims(10e2, 10e3, 10e4, 10e5)

    ## Första steget är att köra alla simuleringar, och skriva ned åtgången tid
    # for f in [runSwitchSim, runVaristorSim, runMOSFETSim, runInfineonMOSFETSim, runIGBTSim]
    #     f()
    # Eller kör alla parallellt för att få fram raw-filer
    # for f in [runSwitchSim, runVaristorSim, runMOSFETSim, runInfineonMOSFETSim]:  # runIGBTSim
    #     p = mp.Process(target=f)
    #     p.start()

    # run runIGBTSim() in parallel with 10 different R_Drain from 1 to 10
    # for R_Drain in [1, 5, 10]:
    #     p = multiprocessing.Process(target=runParallelIGBTSim, args=(R_Drain,))
    #     p.start()

    # Plotta stegsvaret för alla transistorer
    # plotSideBySideStepOf(
    #     names =     ["Strömbrytare",    "Varistor",         "Inb. MOSFET",          "Sub. MOSFET",                      "IGBT"],
    #     filenames = ["bss_switch_1000.0.raw",  "bss_varistor_1000.0.raw", "bss_mosfet_1000.0.raw",   "bss_mosfet_infineon_1000.0_L0.raw",   "bss_igbt_1000.0.raw"])

    # plt.title(r"Fouriertransform av $I_{ds}$")
    # plt.xlabel("Frekvens (Hz)")
    # plt.ylabel("Amplitud")
    # plotOnTopFFTOf(
    #     names =     ["IGBT",            "Inb.MOSFET",          "Sub. MOSFET"],
    #     filenames = ["bss_igbt_1000.0.raw", "bss_mosfet_1000.0.raw",   "bss_mosfet_infineon_1000.0_L0.raw"])
    # plt.show()

    # plt.title(r"Fouriertransform av $I_{ds}$")
    # plt.xlabel("Frekvens (Hz)")
    # plt.ylabel("Amplitud")
    # plotOnTopFFTOf(
    #     names =     ["IGBT", "Strömbrytare", "Varistor"],
    #     filenames=  ["bss_igbt_1000.0.raw", "bss_switch_1000.0.raw", "bss_varistor_1000.0.raw"])
    # plt.show()

    
    # Rita upp styrsignalen med referenssignal
    # #Create a time vector from 0 mss to 10 ms
    # time = np.linspace(0, 10e-3, num=1000)
    # # Create a sine wave with period 10 ms and amplitude 15 V
    # signal = 15*np.sin(time*2*np.pi/(10e-3))
    # # Plot the signal
    # plt.plot(time, signal, label="Referenssignal")
    # plotVars("bss_igbt_1000.0.raw", "V(PWM)", label="Styrsignal")
    # plt.ylabel("Spänning (V)")
    # plt.xlabel("Tid (s)")
    # plt.legend(loc="lower left")
    # plt.show()

    plotSideBySideFFTOf(
         names =     ["Strömbrytare",    "Varistor",         "Inb. MOSFET",          "Sub. MOSFET",                      "IGBT"],
         filenames = ["bss_switch_1000.0.raw",  "bss_varistor_1000.0.raw", "bss_mosfet_1000.0.raw",   "bss_mosfet_infineon_1000.0_L0.raw",   "bss_igbt_1000.0.raw"])

    # plotSideBySideStepOf(
    #     [f"$R_d={i}$" for i in [1,5,10]],
    #     [f"bss_igbt_{i}.raw" for i in [1,5,10]]
    #     )
    quit()


