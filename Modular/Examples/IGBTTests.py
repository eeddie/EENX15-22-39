#
# Skapar en krets med bara en IGBT som är till för att undersöka in- och utsignaler för IGBT:n
# Plottar sedan en jämförande fourieranalys mellan gatespänning och drain-source-ström
#

from threading import Thread
import multiprocessing
import matplotlib.pyplot as plt
from os import remove
import sys

sys.path.append('./Modular/')
from Functions import *


def runIGBTSim(
    R_Gate = 1.0,
    R_Drain = 10.0,
    Gain = 10000,
    Fs = 10000,
    Freq = 100,
    OverlapProtection = 0.03,
    IGBTType = "rgw00ts65chr",
    filePath = "tmp"
):
    """ Kör en simulering av en grundläggande krets med bara en IGBT. outputtar i tmp.raw """

    netlist = f""".title IGBT-Test
.lib /Modular/libs/IGBT/{IGBTType}.lib
BSin      Ph    0 V= sin(2*Pi*{Freq}*time)
BE_PWM    PWM   0 V= 15*tanh({Gain}*(V(Ph)-{OverlapProtection}-V(Triangle)))
BTri Triangle 0 V= (2/Pi)*asin(sin(2*Pi*{Fs}*Time))
V1 in 0 {str(400)}
R1 PWM Gate {R_Gate}
R2 in Drain {R_Drain}
X1 Drain Gate 0 {IGBTType}

                       ; Recommendations for Infineons IGBT:s
*.options reltol=1e-3   ; > 1ms  "Never larger than 0.003!"
*.options abstol=10e-9  ; > 10ns
*.options itl4=30       ; > 30
*.options gmin=1e-10    ;        "Minimum conductance"
*.options cshunt=1e-15  ;        "Capacitance added from each node to ground"

.save v(Gate)
.save i(V1)

.tran 0.1ns 1ms 0ms
.end """

    batchNetlist(netlist, filePath)
    return filePath + ".raw"

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

    


def runIGBTSimGain(Gain, filePath): runIGBTSim(Gain=Gain, filePath=filePath)
def runCompareGainSimsParallell():
    for Gain in [100, 1000, 10000]:
        Thread(target=runIGBTSimGain,args=(Gain, os.path.join("raws","compareGain",f"gain{Gain}_0.1ns"))).start()

def compareGain():
    """ Plottar frekvenssvaret av fyra IGBT-kretsar med gain=10²-10⁴ """

    plt.rcParams['text.usetex'] = True
    fig = 0

    for Gain in [100, 1000, 10000]:
        plt.subplot(1,3,fig+1)
        plotFourierFromFile(os.path.join("raws","compareGain",f"gain{Gain}_0.1ns.raw"), "v(Gate)", "$V_{gs}$", alpha=0.5, linewidth=0.25)
        plotFourierFromFile(os.path.join("raws","compareGain",f"gain{Gain}_0.1ns.raw"), "i(V1)", "$I_{ds}$", alpha=0.5, linewidth=0.25)
        plt.legend(loc="lower left")
        plt.title(f"$Gain={Gain}$")
        plt.loglog()
        plt.grid()

        fig += 1
    
    plt.show()





def runIGBTSimGateDrainResistance(R_Drain, R_Gate, filePath): runIGBTSim(R_Drain=R_Drain, R_Gate=R_Gate, filePath=filePath)
def runCompareGateDrainResistanceSimsParallell():
    for R_Drain in [0.1, 1,10]:
        for R_Gate in [0.1, 1, 10]:
            Thread(target=runIGBTSimGateDrainResistance,args=(R_Drain, R_Gate, os.path.join("raws","compareGateDrainResistance",f"Rd{R_Drain}Rg{R_Gate}G10000_0.1ns"))).start()

def compareGateDrainResistance():
    """ Plottar frekvenssvaret av nio IGBT-kretsar med olika gate. och drain-resistanser, 0.1, 1, 10 """

    plt.rcParams['text.usetex'] = True
    fig = 0

    for R_Drain in [0.1, 1, 10]:
        for R_Gate in [0.1, 1, 10]:
            plt.subplot(3,3,fig+1)
            plotFourierFromFile(os.path.join("raws","compareGateDrainResistance",f"Rd{R_Drain}Rg{R_Gate}_0.1ns.raw"), "v(Gate)", "$V_{gs}$", alpha=0.5, linewidth=0.25)
            plotFourierFromFile(os.path.join("raws","compareGateDrainResistance",f"Rd{R_Drain}Rg{R_Gate}_0.1ns.raw"), "i(V1)", "$I_{ds}$", alpha=0.5, linewidth=0.25)
            plt.legend(loc="lower left")
            plt.title(f"$R_{{drain}}={R_Drain}$,$R_{{gate}}={R_Gate}$")
            plt.loglog()
            plt.grid()

            fig += 1
    
    plt.show()


def runCompareRRatioSimsParallell():
    for (R_Drain, R_Gate) in [[100,10], [10,1], [1,0.1]]:
        Thread(target=runIGBTSimGateDrainResistance, args=(R_Drain, R_Gate, os.path.join("raws","compareRRatio",f"Rd{R_Drain}Rg{R_Gate}_0.1ns"))).start()

def compareRRatio():
    """ Plottar frekvenssvaret av fyra IGBT-kretsar med samma förhållande mellan drain- och gate-resistanser """

    plt.rcParams['text.usetex'] = True
    fig = 0

    for (R_Drain, R_Gate) in [[100,10], [10,1], [1,0.1]]:
        plt.subplot(1,3,fig+1)
        plotFourierFromFile(os.path.join("raws","compareRRatio",f"Rd{R_Drain}Rg{R_Gate}_0.1ns.raw"), "v(Gate)", "$V_{gs}$", alpha=0.5, linewidth=0.25)
        plotFourierFromFile(os.path.join("raws","compareRRatio",f"Rd{R_Drain}Rg{R_Gate}_0.1ns.raw"), "i(V1)", "$I_{ds}$", alpha=0.5, linewidth=0.25)
        plt.legend(loc="lower left")
        plt.title(f"$R_{{d}}={R_Drain},R_{{g}}={R_Gate}$")
        plt.loglog()
        plt.grid()

        fig += 1
    
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
    
    # compareGateDrainSource()

    # runCompareGateResistanceSimsParallell()
    # compareGateResistance()

    # runCompareGainSimsParallell()
    # compareGain()

    # runCompareRRatioSimsParallell()
    compareRRatio()

    

    # runCompareGateDrainResistanceSimsParallell()
    # compareGateDrainResistance()

    # compareIGBTModels(
    #     "FGW75XS65",
    #     "FGW50XS65",
    #     )


# Undersökta IGBT:er
# rgw00ts65chr # 50 A Ids

# Ej undersökta IGBT:er
# rgw60ts65chr # 30 A Ids
# rgw80ts65chr # 40 A Ids
