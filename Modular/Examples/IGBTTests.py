#
# Skapar en krets med bara en IGBT som är till för att undersöka in- och utsignaler för IGBT:n
# Plottar sedan en jämförande fourieranalys mellan gatespänning och drain-source-ström
#

import matplotlib.pyplot as plt
from os import remove
import sys

sys.path.append('./Modular/')
from Functions import *


def runIGBTSim(
    R_Gate = 1.0,
    Gain = 1000,
    Fs = 10000,
    Freq = 100,
    OverlapProtection = 0.03,
    IGBTType = "rgw00ts65chr",
):
    """ Kör en simulering av en grundläggande krets med bara en IGBT. outputtar i tmp.raw """

    netlist = f""".title IGBT-Test
.lib /Modular/libs/IGBT/{IGBTType}.lib
BSin      Ph    0 V= sin(2*Pi*{Freq}*time)
BE_PWM    PWM   0 V= 15*tanh({Gain}*(V(Ph)-{OverlapProtection}-V(Triangle)))
BTri Triangle 0 V= (2/Pi)*asin(sin(2*Pi*{Fs}*Time))
V1 in 0 {str(2*15*1.0175)}  ; Denna spänning ser till att gate-spänningen och drain-source-strömmen har samma amplitud för att kunna jämföra fourier
R1 PWM Gate {R_Gate}
R2 in Drain 1
X1 Drain Gate 0 {IGBTType}

                       ; Recommendations for Infineons IGBT:s
.options reltol=1e-3   ; > 1ms  "Never larger than 0.003!"
.options abstol=10e-9  ; > 10ns
.options itl4=30       ; > 30
.options gmin=1e-10    ;        "Minimum conductance"
.options cshunt=1e-15  ;        "Capacitance added from each node to ground"

.tran 1ns 1ms 0ms 1ns
.end """

    batchNetlist(netlist, "tmp")


def compareGateDrainSource():
    """ Plottar frekvens- och tidsdomän för gate-spänning och drain-source-ström för en krets """

    runIGBTSim()

    plt.figure(0)
    plt.title("IGBT Test")
    plotFourierFromFile("tmp.raw", "v(PWM)", r"$V_{ge}$")
    plotFourierFromFile("tmp.raw", "i(V1)", r"$I_{ce}$")
    plt.legend()
    plt.rcParams['text.usetex'] = True
    
    plt.figure(1)
    plt.title("IGBT Test")
    plotVars("tmp.raw", "v(PWM)", label=r"$V_{ge}$")
    plotVars("tmp.raw", "i(V1)", label=r"$I_{ce}$")
    plt.show()

    remove("tmp.raw")


def compareGain():
    """ Plottar frekvenssvaret av fyra IGBT-kretsar med gain=10²-10⁴ """

    plt.figure(0)
    plt.title(r"V_{ge}")
    plt.figure(1)
    plt.title(r"I_{ce}")
    plt.figure(2)
    plt.title(r"V_{ce}")
    plt.rcParams['text.usetex'] = True

    for gain in [10**5, 10**4, 10**3, 10**2]:     # Vi plottar i omvänd ordning eftersom vi då kan se de högsta frekvenserna av varje fourier 
        runIGBTSim(Gain=gain)

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
    """ Plottar frekvenssvaret av fyra IGBT-kretsar med olika gate-resistanser, 0.25, 0.5, 0.75, 1 """

    plt.figure(0)
    plt.title(r"V_{ge}")
    plt.figure(1)
    plt.title(r"I_{ce}")
    plt.rcParams['text.usetex'] = True

    for R_Gate in [100, 10, 1, 0.1]:     # Vi plottar i omvänd ordning eftersom vi då kan se de högsta frekvenserna av varje fourier 
        runIGBTSim(R_Gate=R_Gate)

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
    plt.title(r"$V_{ge}$")
    plt.figure(1)
    plt.title(r"$I_{ce}$")
    
    for [IGBTType] in models:
        runIGBTSim(IGBTType=IGBTType, )

        plt.figure(0)
        plotFourierFromFile("tmp.raw", "v(PWM)", f"IGBT={IGBTType}", formatString="k", alpha=0.5)
        
        plt.figure(1)
        plotFourierFromFile("tmp.raw", "i(V1)", f"MOSFET={IGBTType}", formatString="k", alpha=0.5)

        remove("tmp.raw")

    plt.figure(0)
    plt.legend()
    plt.figure(1)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # compareGateResistance()
    # compareGateDrainSource()
    compareGain()
    
    # compareIGBTModels(
    #     "FGW75XS65",
    #     "FGW50XS65",
    #     )