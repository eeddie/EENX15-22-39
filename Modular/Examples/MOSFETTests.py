#
# Skapar en krets med bara en mosfet som är till för att undersöka in- och utsignaler för MOSFET:en
# Plottar sedan en jämförande fourieranalys mellan gatespänning och drain-source-ström
#

import matplotlib.pyplot as plt
from os import remove
import sys
import scipy
import numpy as np

sys.path.append('./Modular/')
from Functions import *

# MOSFETS som åtminstone har tillräckligt hög Vds, men inte tillräcklig Ids
# SPA11N60C3    Vds=650 Id = 11 A
# STP8NM60      Vds=650 Id = 8 A
# STW11NM80     Vds=800 Id = 11 A

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

.tran 0.5ns 1ms 0ms 0.5ns
.end """

    batchNetlist(netlist, "tmp")


def compareGateDrainSource():
    """ Plottar frekvens- och tidsdomän för gate-spänning och drain-source-ström för en krets """

    runMOSFETSim()

    plt.figure(0)
    plt.title("Mosfet Test")
    plotFourierFromFile("tmp.raw", "v(gate)", "$V_{gs}$")
    plotFourierFromFile("tmp.raw", "i(V1)", "$I_{ds}$")
    plt.legend()
    plt.rcParams['text.usetex'] = True
    
    plt.figure(1)
    plt.title("Mosfet Test")
    plotVars("tmp.raw", "v(gate)", label="$V_{gs}$")
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

def compareAgainst100k():
    runMOSFETSim(Gain=10**5)
    [time0,data0] = readVariables("tmp.raw","v(gate)")
    [time1,data1] = readVariables("tmp.raw","i(v1)")
    [uniTime0,uniData0] = uniformResample(time0,data0,timeStep=10**(-9))
    [_,uniData1] = uniformResample(time0,data1,timeStep=10**(-9))
    N = len(uniTime0)
    ugf100k = fft(uniData0)
    #ugf100kplt = 2.0/N * np.abs(ugf100k[0,0:N//2])
    idsf100k = fft(uniData1)
    #idsf100kplt = 2.0/N * np.abs(idsf100k[0,0:N//2])
    tf = fftfreq(N, uniTime0[1]-uniTime0[0])[0:N//2]

    """plt.figure(0)
    plt.title("V_{gs}")
    plt.figure(1)
    plt.title("I_{ds}")

    plt.figure(0)
    plt.plot(tf, ugf100kplt, "-", linewidth=1, alpha=0.5, label="ug, gain=100k")
    plt.loglog()
    plt.grid()

    plt.figure(1)
    plt.plot(tf, idsf100kplt, "-", linewidth=1, alpha=0.5, label="ids, gain=100k")
    plt.loglog()
    plt.grid()
    plt.show()"""

    plt.figure(0)
    plt.plot(tf, 2.0/N * np.abs(ugf100k[0,0:N//2]), "-", linewidth=1, alpha=0.5, label=f"ug, gain=10^(5)")

    plt.figure(1)
    plt.plot(tf, 2.0/N * np.abs(idsf100k[0,0:N//2]), "-", linewidth=1, alpha=0.5, label=f"ids, gain=10^(5)")

    plt.figure(0)
    plt.loglog()
    plt.grid()

    plt.figure(1)
    plt.loglog()
    plt.grid()

    plt.figure(2)
    plt.loglog()
    plt.grid()

    plt.figure(3)
    plt.loglog()
    plt.grid()

    for i in [0,1,2]:
        runMOSFETSim(Gain=10**(4-i))
        [time0,data0] = readVariables("tmp.raw","v(gate)")
        [time1,data1] = readVariables("tmp.raw","i(v1)")
        [uniTime0,uniData0] = uniformResample(time0,data0,timeStep=10**(-9))
        [_,uniData1] = uniformResample(time0,data1,timeStep=10**(-9))
        N = len(uniTime0)
        ugf = fft(uniData0)
        idsf = fft(uniData1)

        diffug = ugf - ugf100k
        diffids = idsf - idsf100k

        plt.figure(0)
        plt.plot(tf, 2.0/N * np.abs(ugf[0,0:N//2]), "-", linewidth=1, alpha=0.5, label=f"ug, gain=10^({4-i})")

        plt.figure(1)
        plt.plot(tf, 2.0/N * np.abs(idsf[0,0:N//2]), "-", linewidth=1, alpha=0.5, label=f"ids, gain=10^({4-i})")

        plt.figure(2)
        plt.plot(tf, 2.0/N * np.abs(diffug[0,0:N//2]), "-", linewidth=1, alpha=0.5, label=f"diff ug, gain=10^({4-i})")

        plt.figure(3)
        plt.plot(tf, 2.0/N * np.abs(diffids[0,0:N//2]), "-", linewidth=1, alpha=0.5, label=f"diff ids, gain=10^({4-i})")
    
    plt.figure(0)
    plt.legend()
    plt.figure(1)
    plt.legend()
    plt.figure(2)
    plt.legend()
    plt.figure(3)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # compareGateResistance()
    # compareGateDrainSource()
    # compareGain()
    compareAgainst100k()
    
    #compareMOSFETModels(
    #    "IPI200N25N3",
    #    "RJK0451DPB",
    #    "TN2404K",
    #    "IRF2805S"
    #    )