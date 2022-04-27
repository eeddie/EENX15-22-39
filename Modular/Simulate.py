#
#   Simulate.py
#
#   Innehåller en main-funktion för simulering av drivlinan
#

import os
from Modules import *
from Functions import *
import random as r
from multiprocessing import Process, cpu_count


def createNetlist(modules, simParams):
    return f""".title drivlina
{os.linesep.join(module.getNetlist() for module in modules)}
    
Xbattery BatPos BatNeg BatCase BatteryModule
    
VDC_P BatFiltPos BatPos 0 
VDC_N BatFiltNeg BatNeg 0

Xbatfilt BatPos BatNeg InvPos InvNeg DCFilterModule
    
Xinverter InvPos InvNeg InvA InvB InvC InvCase InverterModule
    
Xloadfilter InvA InvB InvC FiltA FiltB FiltC ACFilterModule

VAC_A PhA FiltA 0
VAC_B PhB FiltB 0
VAC_C PhC FiltC 0
    
Xload PhA PhB PhC LoadCase LoadModule
    
XbatGnd BatCase 0 BatteryGroundModule
XinvGnd InvCase 0 InverterGroundModule
XloadGnd LoadCase 0 LoadGroundModule
    
    
.ic v(InvA)=0 v(InvB)=0 v(InvC)=0
.option method={simParams["method"]}


.options reltol=1e-3   ; > 1ms  "Never larger than 0.003!"
.options abstol=10e-9  ; > 10ns
.options itl4=30       ; > 30
.options gmin=1e-10    ;        "Minimum conductance"
.options cshunt=1e-15  ;        "Capacitance added from each node to ground"
    
.options savecurrents
    
.save i(l.xload.l1)
    
.save i(l.xbatgnd.c1)
.save i(l.xinvgnd.c1)
.save i(l.xloadgnd.c1)
    
.tran {simParams["tstep"]} {simParams["tstop"]} {simParams["tstart"]}
.end"""


def rand(start: float, slut: float):
    return start + r.random() * (slut - start)


def batch(netlist, s, log):
    # Simulera netlisten och outputta till en .raw fil
    batchNetlist(netlist, s, log=log)


def cluster_code():
    numberOfSimulations = 1
    CouplingValues = [rand(0.5, 1) for _ in range(numberOfSimulations)]
    L_chokeValues = [rand(20, 80) * (10 ** -3) for _ in range(numberOfSimulations)]
    print(CouplingValues)
    print(L_chokeValues)

    # Mata in parametrarna till modulerna här i modulens constructor
    # Varje modul har sitt netlist-namn från vilken plats den har i den hela drivlinan. ex. XCapModule och DCCommonModeChokeModule har båda namnet DCFilterModule i netlisten.
    # Vill man byta ut ex. XCapModule med DCCommonModeChokeModule byter man ut dem i denna listan.
    # Vill man seriekoppla XCap och CMC får man sätta in unika namn för de två modulerna i denna listan, ha dem båda i listan nedan och ändra netlistan för drivlinan med de två nya namnen.
    for i in range(numberOfSimulations):
        modules = [
            InverterControlModule(),
            MosfetModule(),
            InverterModule(),
            InverterGroundModule(),
            StaticLoadModule(),
            LoadGroundModule(),
            XCapModule(),
            ACCommonModeChokeModule(L_choke=L_chokeValues[i], Coupling=CouplingValues[i]),
            BatteryGroundModule(),
            SimpleBatteryModule()
        ]

        # Simuleringsparametrar
        simParams = {
            "tstep": "1ns",
            "tstart": "0us",
            "tstop": "1us",
            "method": "trap"
        }

        netlist = createNetlist(modules, simParams)

        batchNetlist(netlist, "sim" + str(i) + ".raw", removeNetlist=False)

        # Spara datan från den genomförda simuleringen
        saveSim("params.json",
                modules=modules,
                simParams=simParams,
                results={}  # Beräknar inget resultat för tillfället.
                )


import sys


def one_cluster_code():
    modules = [
        InverterControlModule(),
        MosfetModule(),
        InverterModule(),
        InverterGroundModule(),
        StaticLoadModule(),
        LoadGroundModule(),
        XCapModule(),
        ACCommonModeChokeModule(Coupling=float(sys.argv[2]), L_choke=float(sys.argv[3])),
        BatteryGroundModule(),
        SimpleBatteryModule()
    ]

    # Simuleringsparametrar
    simParams = {
        "tstep": "1ns",
        "tstart": "0us",
        "tstop": "1us",
        "method": "trap"
    }

    netlist = createNetlist(modules, simParams)

    batchNetlist(netlist, "sim" + str(sys.argv[1]), removeNetlist=True)

    # Spara datan från den genomförda simuleringen
    saveSim("simResults\\params" + str(sys.argv[1]) + ".json",
            modules=modules,
            simParams=simParams,
            results={"energies": saveAllBands("sim" + str(sys.argv[1]) + ".raw")}
            # Beräknar inget resultat för tillfället.
            )

    os.remove("sim" + str(sys.argv[1]) + ".raw")

import subprocess
import multiprocessing


def np_encoder(object):
    if isinstance(object, np.generic):
        return object.item()


def saveBandEnergies(filename: str, energies: list):
    """ Sparar ned simuleringens parametrar till en JSON-fil, lägger till simuleringen om filen redan existerar """

    with open(filename, "w+") as file:  # Öppna/Skapa json fil
        try:
            file_data = json.load(file)  # Ladda in JSON-data som python object (list "[]" eller dict "{}")
        except json.JSONDecodeError:
            file_data = []  #  Om filen är tom, skapa en tom lista, i denna hamnar alla utförda simuleringar

        for i in range(len(energies)):
            file_data.append(energies[i])  # Lägg till en ny dict, som innehåller datan från simuleringen, i listan
        file.seek(0)  # Börja om filen från början så vi skriver över filen med den nya datan

        return json.dumps(file_data, default=np_encoder)


def saveAllBands(filename: str):
    [time0, data0] = readVariables(filename, "i(l.xload.l1)")
    [uniTime0, uniData0] = uniformResample(time0, data0, timeStep=10 ** (-9))
    N = len(uniTime0)
    fftcurrent = 2.0 / N * np.abs(fft(uniData0)[0, 0:N // 2])
    tf = fftfreq(N, uniTime0[1] - uniTime0[0])[0:N // 2]

    energy = energyInAllBands(tf, fftcurrent)

    return saveBandEnergies("C:\\EENX15\\Modular\\bandEnergies.json", energy)


if __name__ == "__main__":
    # cluster_code()

    one_cluster_code()

    # plt.figure(4)
    # freq = [row[0] for row in energy]
    # value = [row[2]/row[3] for row in energy]
    # plt.plot(tf, fftcurrent, "-", linewidth=1, alpha=0.5, label=f"i(L1)")
    # plt.plot(freq,value, '-', linewidth=1,alpha=0.5, label="i(L1) avg:d")
    # plt.legend()
    # plt.loglog()
    # plt.grid()
    # plt.show()

#    energyInAllBands("tmp_10000.raw")

# .options savecurrents

# .save i(l.xload.l1)
# .save i(l.xload.l2)
# .save i(l.xload.l3)
# .save v(pha)
# .save v(phb)
# .save v(phc)
# .save i(l.xbatgnd.c1)
# .save i(l.xinvgnd.c1)
# .save i(l.xloadgnd.c1)

# .save i(l.xbatgnd.c1)
# .save i(l.xinvgnd.c1)
# .save i(l.xloadgnd.c1)

# .save i(@c.xinverter.c1[i])
# .save i(@c.xinverter.c2[i])
# .save i(@c.xinverter.c3[i])
# .save i(@c.xinverter.c4[i])
# .save i(@c.xinverter.c5[i])

# .save i(l.xload.l1)
# .save i(l.xload.l2)
# .save i(l.xload.l3)
