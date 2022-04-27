#
#   Simulate.py
#
#   Innehåller en main-funktion för simulering av drivlinan
#
from Modules import *
from Functions import *
import inspect, sys, random as r

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

.save i(l.xload.l1)

.save i(VDC_P)
.save i(VDC_N)

.tran {simParams["tstep"]} {simParams["tstop"]} {simParams["tstart"]}
.end"""


def rand(start: float, slut: float):
    return start + r.random() * (slut - start)


def percentDiff(percent: float):
    return rand(1 - percent, 1 + percent)


def get_default_args(func):
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


if __name__ == "__main__":

    inverterControlModule = get_default_args(InverterControlModule)
    inverterModule = get_default_args(InverterModule)
    staticLoadModule = get_default_args(StaticLoadModule)
    simpleBatteryModule = get_default_args(SimpleBatteryModule)
    xCapModule = get_default_args(XCapModule)
    dCCommonModeChokeModule = get_default_args(DCCommonModeChokeModule)
    aCCommonModeChokeModule = get_default_args(ACCommonModeChokeModule)
    loadGroundModule = get_default_args(LoadGroundModule)
    inverterGroundModule = get_default_args(InverterGroundModule)
    batteryGroundModule = get_default_args(BatteryGroundModule)

    inverterControlModuleGain = percentDiff(0.1) * inverterControlModule["Gain"]
    inverterControlModuleFs = percentDiff(0.1) * inverterControlModule["Fs"]

    inverterModuleMod = percentDiff(0.1) * inverterModule["Mod"]
    inverterModuleFreq = percentDiff(0.1) * inverterModule["Freq"]
    inverterModuleParCapA = percentDiff(0.10) * inverterModule["ParCapA"]
    inverterModuleParCapB = percentDiff(0.10) * inverterModule["ParCapB"]
    inverterModuleParCapC = percentDiff(0.10) * inverterModule["ParCapC"]
    inverterModuleParCapP = percentDiff(0.10) * inverterModule["ParCapP"]
    inverterModuleParCapN = percentDiff(0.10) * inverterModule["ParCapN"]

    staticLoadModuleR_load = percentDiff(0.10) * staticLoadModule["R_load"]
    staticLoadModuleL_load = percentDiff(0.10) * staticLoadModule["L_load"]
    staticLoadModuleParCapA = percentDiff(0.10) * staticLoadModule["ParCapA"]
    staticLoadModuleParCapB = percentDiff(0.10) * staticLoadModule["ParCapB"]
    staticLoadModuleParCapC = percentDiff(0.10) * staticLoadModule["ParCapC"]
    staticLoadModuleParCapN = percentDiff(0.10) * staticLoadModule["ParCapN"]

    simpleBatteryModuleR_self = percentDiff(0.10) * simpleBatteryModule["R_self"]
    simpleBatteryModuleL_self = percentDiff(0.10) * simpleBatteryModule["L_self"]
    simpleBatteryModuleParCapP = percentDiff(0.10) * simpleBatteryModule["ParCapP"]
    simpleBatteryModuleParCapN = percentDiff(0.10) * simpleBatteryModule["ParCapN"]

    xCapModuleC_self = percentDiff(0.10) * xCapModule["C_self"]
    xCapModuleR_self = percentDiff(0.10) * xCapModule["R_self"]

    dCCommonModeChokeModuleR_ser = percentDiff(0.10) * dCCommonModeChokeModule["R_ser"]
    dCCommonModeChokeModuleL_choke = percentDiff(0.10) * dCCommonModeChokeModule["L_choke"]
    dCCommonModeChokeModuleCoupling = percentDiff(0.10) * dCCommonModeChokeModule["Coupling"]

    aCCommonModeChokeModuleR_ser = percentDiff(0.10) * aCCommonModeChokeModule["R_ser"]
    aCCommonModeChokeModuleL_choke = percentDiff(0.10) * aCCommonModeChokeModule["L_choke"]
    aCCommonModeChokeModuleCoupling = percentDiff(0.10) * aCCommonModeChokeModule["Coupling"]

    loadGroundModuleR = percentDiff(0.10) * loadGroundModule["R"]
    loadGroundModuleC = percentDiff(0.10) * loadGroundModule["C"]
    loadGroundModuleL = percentDiff(0.10) * loadGroundModule["L"]

    inverterGroundModuleR = percentDiff(0.10) * inverterGroundModule["R"]
    inverterGroundModuleC = percentDiff(0.10) * inverterGroundModule["C"]
    inverterGroundModuleL = percentDiff(0.10) * inverterGroundModule["L"]

    batteryGroundModuleR = percentDiff(0.10) * batteryGroundModule["R"]
    batteryGroundModuleC = percentDiff(0.10) * batteryGroundModule["C"]
    batteryGroundModuleL = percentDiff(0.10) * batteryGroundModule["L"]

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
