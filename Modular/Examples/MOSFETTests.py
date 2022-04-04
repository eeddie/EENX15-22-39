#
# Skapar en krets med bara en mosfet som är till för att undersöka in- och utsignaler för MOSFET:en
# Plottar sedan en jämförande fourieranalys mellan gatespänning och drain-source-ström
#

import matplotlib.pyplot as plt
from os import remove
import sys

sys.path.append('./Modular/')
from Functions import *


def runMOSFETSim(
    R_Gate = 1.0,
    Gain = 1000,
    Fs = 10000,
    Freq = 100,
    OverlapProtection = 0.03,
    MOSType = "IPI200N25N3"
):
    """ Kör en simulering av en grundläggande krets med bara en mosfet. outputtar i tmp.raw """

    netlist = f""".title MOSFET-Test
.lib /Modular/libs/MOS.lib
BSin      Ph    0 V= sin(2*Pi*{Freq}*time)
BE_PWM    PWM   0 V= 15*tanh({Gain}*(V(Ph)-{OverlapProtection}-V(Triangle)))
BTri Triangle 0 V= (2/Pi)*asin(sin(2*Pi*{Fs}*Time))
V1 in 0 {str(2*15*1.0175)}  ; Denna spänning ser till att gate-spänningen och drain-source-strömmen har samma amplitud för att kunna jämföra fourier
R1 PWM Gate {R_Gate}
R2 in Drain 1
M1 Drain Gate 0 0 {MOSType}

.tran 1ns 1ms 0ms 1ns
.end """

    batchNetlist(netlist, "tmp")


def compareGateDrainSource():
    """ Plottar frekvens- och tidsdomän för gate-spänning och drain-source-ström för en krets """

    runMOSFETSim()

    plt.figure(0)
    plt.title("Mosfet Test")
    plotFourierFromFile("tmp.raw", "v(PWM)", "$V_{gs}$")
    plotFourierFromFile("tmp.raw", "i(V1)", "$I_{ds}$")
    plt.legend()
    plt.rcParams['text.usetex'] = True
    
    plt.figure(1)
    plt.title("Mosfet Test")
    plotVars("tmp.raw", "v(PWM)", label="$V_{gs}$")
    plotVars("tmp.raw", "i(V1)", label="$I_{ds}$")
    plt.show()

    remove("tmp.raw")


def compareGain():
    """ Plottar frekvenssvaret av fyra MOSFET-kretsar med gain, 10-10⁴ """

    plt.figure(0)
    plt.title(r"$V_{gs}$")
    plt.figure(1)
    plt.title(r"$I_{ds}$")
    plt.figure(2)
    plt.title(r"$V_{gs}$")

    for gain in [10**5, 10**4, 10**3, 10**2]:     # Vi plottar i omvänd ordning eftersom vi då kan se de högsta frekvenserna av varje fourier 
        runMOSFETSim(Gain=gain)

        plt.figure(0)
        plotFourierFromFile("tmp.raw", "v(PWM)", f"gain={gain}", alpha=1, resampleTime=10**-10)
        
        plt.figure(1)
        plotFourierFromFile("tmp.raw", "i(V1)", f"gain={gain}", alpha=1, resampleTime=10**-10)

        plt.figure(2)
        plotVars("tmp.raw", "V(PWM)", label=f"gain={gain}", alpha=1)

        remove("tmp.raw")

    plt.figure(0)
    plt.legend(loc="lower left")
    plt.figure(1)
    plt.legend(loc="lower left")
    plt.figure(2)
    plt.legend(loc="lower left")
    plt.show()

def compareGateResistance():
    """ Plottar frekvenssvaret av fyra MOSFET-kretsar med olika gate-resistanser, 0.25, 0.5, 0.75, 1 """

    plt.figure(0)
    plt.title(r"$V_{gs}$")
    plt.figure(1)
    plt.title(r"$I_{ds}$")
    plt.rcParams['text.usetex'] = True

    for R_Gate in [0.1, 1, 10, 100]:     # Vi plottar i omvänd ordning eftersom vi då kan se de högsta frekvenserna av varje fourier 
        runMOSFETSim(R_Gate=R_Gate)

        plt.figure(0)
        plotFourierFromFile("tmp.raw", "v(PWM)", f"$R_{{gate}}={R_Gate}$", alpha=1)
        
        plt.figure(1)
        plotFourierFromFile("tmp.raw", "i(V1)", f"$R_{{gate}}={R_Gate}$", alpha=1)

        remove("tmp.raw")

    plt.figure(0)
    plt.legend()
    plt.figure(1)
    plt.legend()
    plt.show()


def compareMOSFETModels(*models):
    """ Plottar frekvenssvaret av olka MOSFETs """

    plt.rcParams['text.usetex'] = True
    plt.figure(0)
    plt.title(r"$V_{pwm}$")
    plt.figure(1)
    plt.title(r"$I_{ds}$")

    for MOSType in models:
        runMOSFETSim(MOSType=MOSType, )

        plt.figure(0)
        plotFourierFromFile("tmp.raw", "v(PWM)", f"MOSFET={MOSType}", formatString="k", alpha=0.5)
        
        plt.figure(1)
        plotFourierFromFile("tmp.raw", "i(V1)", f"MOSFET={MOSType}", formatString="k", alpha=0.5)

        remove("tmp.raw")

    plt.figure(0)
    plt.legend()
    plt.figure(1)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # compareGateResistance()
    # compareGateDrainSource()
    # compareGain()
    
    compareMOSFETModels(
        "IPI200N25N3",
        "RJK0451DPB",
        "TN2404K",
        "IRF2805S"
        )