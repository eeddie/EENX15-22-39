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


import sys


def percentDiff(percent: float):
    return rand(1 - percent, 1 + percent)


if __name__ == "__main__":
    inverterControlModuleGain = percentDiff(0.1) * 1000
    inverterControlModuleFs = percentDiff(0.1) * 1000

    inverterModuleMod = percentDiff(0.1) * 1
    inverterModuleFreq = percentDiff(0.1) * 100
    inverterModuleParCapA = percentDiff(0.10) * (1.4 * (10 ** -12))
    inverterModuleParCapB = percentDiff(0.10) * (2.0 * (10 ** -12))
    inverterModuleParCapC = percentDiff(0.10) * (0.7 * (10 ** -12))
    inverterModuleParCapP = percentDiff(0.10) * (1.1 * (10 ** -12))
    inverterModuleParCapN = percentDiff(0.10) * (2.0 * (10 ** -12))

    staticLoadModuleR_load = percentDiff(0.10) * 1.09
    staticLoadModuleL_load = percentDiff(0.10) * 20 * (10 ** -3)
    staticLoadModuleParCapA = percentDiff(0.10) * 12 * (10 ** -12)
    staticLoadModuleParCapB = percentDiff(0.10) * 15 * (10 ** -12)
    staticLoadModuleParCapC = percentDiff(0.10) * 18 * (10 ** -12)
    staticLoadModuleParCapN = percentDiff(0.10) * 55 * (10 ** -12)

    simpleBatteryModuleR_self = percentDiff(0.10) * 0.1
    simpleBatteryModuleL_self = percentDiff(0.10) * 500 * (10 ** -9)
    simpleBatteryModuleParCapP = percentDiff(0.10) * 52 * (10 ** -12)
    simpleBatteryModuleParCapN = percentDiff(0.10) * 48 * (10 ** -12)

    xCapModuleC_self = percentDiff(0.10) * 500 * 10 ** -6
    xCapModuleR_self = percentDiff(0.10) * 1.9 * 10 ** -3

    dCCommonModeChokeModuleR_ser = percentDiff(0.10) * 20 * 10 ** -3
    dCCommonModeChokeModuleL_choke = percentDiff(0.10) * 51 * 10 ** -3
    dCCommonModeChokeModuleCoupling = percentDiff(0.10) * 0.95

    aCCommonModeChokeModuleR_ser = percentDiff(0.10) * 0.02
    aCCommonModeChokeModuleL_choke = percentDiff(0.10) * 51 * (10 ** -3)
    aCCommonModeChokeModuleCoupling = percentDiff(0.10) * 0.95

    loadGroundModuleR = percentDiff(0.10) * 1.59 * (10 ** (-3))
    loadGroundModuleC = percentDiff(0.10) * 8.96 * (10 ** (-9))
    loadGroundModuleL = percentDiff(0.10) * 800.0 * (10 ** (-9))

    inverterGroundModuleR = percentDiff(0.10) * 1.59 * (10 ** (-3))
    inverterGroundModuleC = percentDiff(0.10) * 4.48 * (10 ** (-9))
    inverterGroundModuleL = percentDiff(0.10) * 400.0 * (10 ** (-9))

    batteryGroundModuleR = percentDiff(0.10) * 1.59 * (10 ** (-3))
    batteryGroundModuleC = percentDiff(0.10) * 3.36 * (10 ** (-9))
    batteryGroundModuleL = percentDiff(0.10) * 300.0 * (10 ** (-9))

    modules = [
        InverterControlModule(Gain=inverterControlModuleGain, Fs=inverterControlModuleFs),
        MosfetModule(),
        InverterModule(Mod=inverterModuleMod, Freq=inverterModuleFreq,
                       ParCapA=inverterModuleParCapA, ParCapB=inverterModuleParCapB,
                       ParCapC=inverterModuleParCapC, ParCapP=inverterModuleParCapP, ParCapN=inverterModuleParCapN),
        InverterGroundModule(R=inverterGroundModuleR, C=inverterGroundModuleC, L=inverterGroundModuleL),
        StaticLoadModule(L_load=staticLoadModuleL_load, R_load=staticLoadModuleR_load, ParCapA=staticLoadModuleParCapA,
                         ParCapB=staticLoadModuleParCapB, ParCapC=staticLoadModuleParCapC,
                         ParCapN=staticLoadModuleParCapN),
        LoadGroundModule(R=loadGroundModuleR, C=loadGroundModuleC, L=loadGroundModuleL),
        XCapModule(C_self=xCapModuleC_self, R_self=xCapModuleR_self),
        ACCommonModeChokeModule(Coupling=aCCommonModeChokeModuleCoupling, R_ser=aCCommonModeChokeModuleR_ser,
                                L_choke=aCCommonModeChokeModuleL_choke),
        BatteryGroundModule(R=batteryGroundModuleR, C=batteryGroundModuleC, L=batteryGroundModuleL),
        SimpleBatteryModule(ParCapP=simpleBatteryModuleParCapP, ParCapN=simpleBatteryModuleParCapN,
                            L_self=simpleBatteryModuleL_self, R_self=simpleBatteryModuleR_self)
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

    saveSim("simResults\\params" + str(sys.argv[1]) + ".json",
            modules=modules,
            simParams=simParams,
            results={}
            )
