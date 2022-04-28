#
#   Simulate.py
#
#   Innehåller en main-funktion för simulering av drivlinan
#

import os
import sys
from Modules import *
from Functions import *
import random as r
from multiprocessing import Process, cpu_count
import subprocess
import multiprocessing



def createNetlist(modules, simParams):
    return f""".title drivlina
{os.linesep.join(module.getNetlist() for module in modules)}
    
Xbattery BatPos BatNeg BatCase BatteryModule
    
* Strömmättning batteri i(Vbatpos)  i(Vbatneg)
VDC_P BatPos CMCPos 0 
VDC_N BatNeg CMCNeg  0

Xdccmc CMCPos CMCNeg InvPos InvNeg DCCommonModeChokeModule

Xxcap InvPos InvNeg XCapModule

Xbatfilt BatPos BatNeg InvPos InvNeg DCFilterModule
    
Xinverter InvPos InvNeg InvA InvB InvC InvCase InverterModule
    
Xaccmc InvA InvB InvC CMCA CMCB CMCC ACCommonModeChokeModule

* Strömmätning för faser i(VPhA) i(VPhB) i(VPhC)
VAC_A CMCA PhA 0
VAC_B CMCB PhB 0
VAC_C CMCC PhC 0
    
Xload PhA PhB PhC LoadCase LoadModule
    
XbatGnd   BatCase 0 BatteryGroundModule
XinvGnd   InvCase 0 InverterGroundModule
XloadGnd LoadCase 0 LoadGroundModule
    
.ic v(InvA)=0 v(InvB)=0 v(InvC)=0
.option method={simParams["method"]}


.options reltol=1e-3   ; > 1ms  "Never larger than 0.003!"
.options abstol=10e-9  ; > 10ns
.options itl4=30       ; > 30

.save i(VAC_A)
.save i(VAC_B)
.save i(VAC_C)
.save i(VDC_P)
.save i(VDC_N)

.save i(l.xinvgnd.l1)
.save i(l.xbatgnd.l1)
.save i(l.xloadgnd.l1)

.save v(batCase)
.save v(invCase)
.save v(loadCase)

.save v(CMCPos)
.save v(CMCNeg)
    
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


def one_cluster_code():
    modules = [
        InverterControlModule(),
        SwitchModule(),
        InverterModule(),
        InverterGroundModule(),
        StaticLoadModule(),
        LoadGroundModule(),
        XCapModule(),
        DCCommonModeChokeModule(),  # Or NoDCCommonModeChokeModule()
        ACCommonModeChokeModule(Coupling=float(sys.argv[2]), L_choke=float(sys.argv[3])),  # or NoACCommonModeChokeModule()
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

    batchNetlist(netlist, "sim" + str(sys.argv[1]))


    # Spara datan från den genomförda simuleringen
    saveSim("simResults\\params" + str(sys.argv[1]) + ".json",
            modules=modules,
            simParams=simParams,
            results={"energies": saveAllBands("sim" + str(sys.argv[1]) + ".raw")}
            # Beräknar inget resultat för tillfället.
            )

    os.remove("sim" + str(sys.argv[1]) + ".raw")



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
    one_cluster_code()