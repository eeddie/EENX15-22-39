#
#   SimulateSingle.py
#
#   Innehåller en main-funktion för simulering av en enstaka drivlina med slumpade parametrar
#
from Modules import *
from Functions import *
import inspect, sys, random as r

def createNetlist(modules: list, simParams: dict):
    return f""".title drivlina
{os.linesep.join(module.getNetlist() for module in modules)}

Xbattery BatPos BatNeg BatCase BatteryModule
    
* Strömmättning batteri i(Vbatpos)  i(Vbatneg)
VDC_P BatPos CMCPos 0 
VDC_N BatNeg CMCNeg  0

Xdccmc CMCPos CMCNeg InvPos InvNeg DCCommonModeChokeModule

Xxcap InvPos InvNeg XCapModule
    
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


if __name__ == "__main__":

    modules: list[Module] = [
        InverterControlModule(
            Fs=rand(5000,20000), 
            Rg=rand(0.5, 2.0)),

        SwitchModule(),

        InverterModule(
            Freq=100, 
            Mod=1, 
            ParCapA=rand(0.1*1e-12, 10*1e-12), 
            ParCapB=rand(0.1*1e-12, 10*1e-12), 
            ParCapC=rand(0.1*1e-12, 10*1e-12), 
            ParCapP=rand(0.1*1e-12, 10*1e-12), 
            ParCapN=rand(0.1*1e-12, 10*1e-12)),

        InverterGroundModule(
            R=rand(1*1e-3, 10*1e-3), 
            C=rand(1*1e-9, 10*1e-9), 
            L=rand(100*1e-9, 1000*1e-9)),

        StaticLoadModule(
            R_load =rand(1, 10),
            L_load =rand(10*1e-3,  100*1e-3),
            ParCapA=rand(10*1e-12, 100*1e-12),
            ParCapB=rand(10*1e-12, 100*1e-12),
            ParCapC=rand(10*1e-12, 100*1e-12),
            ParCapN=rand(10*1e-12, 100*1e-12)),

        LoadGroundModule(
            R=rand(1*1e-3,   10*1e-3),
            C=rand(1*1e-9,   10*1e-9),
            L=rand(100*1e-9, 1000*1e-9)),

        XCapModule(
            C_self=rand(100*1e-6, 1000*1e-6),
            R_self=rand(1*1e-3, 10*1e-3)),
        
        DCCommonModeChokeModule(
            R_ser=rand(1*1e-3, 100*1e-3),
            L_choke=rand(10*1e-3, 100*1e-3),
            Coupling=rand(0.8, 1.0)) if r.random() > 0.5 else NoDCCommonModeChokeModule(),
        
        ACCommonModeChokeModule(
            R_ser=rand(1*1e-3, 100*1e-3),
            L_choke=rand(10*1e-3, 100*1e-3),
            Coupling=rand(0.8, 1.0)) if r.random() > 0.5 else NoACCommonModeChokeModule(),

        BatteryGroundModule(
            R=rand(1*1e-3, 10*1e-3), 
            C=rand(1*1e-9, 10*1e-9),
            L=rand(100*1e-9, 1000*1e-9)),

        SimpleBatteryModule(
            Voltage=rand(400, 800),
            R_self=rand(0.01, 1),
            L_self=rand(100*1e-9, 1000*1e-9),
            ParCapP=rand(10*1e-12, 100*1e-12),
            ParCapN=rand(10*1e-12, 100*1e-12))
    ]

    # Simuleringsparametrar
    simParams = {
        "tstep": "1ns",
        "tstart": "0us",
        "tstop": "10ms",
        "method": "trap"
    }

    netlist = createNetlist(modules, simParams)

    # Create the folder tmp/ if it does not exist
    if not os.path.exists("tmp"): os.makedirs("tmp")
    batchNetlist(netlist, os.path.join("tmp", "sim" + str(sys.argv[1])), log=True)

    saveSim(filename=os.path.join("tmp", "params" + str(sys.argv[1]) + ".json"),
            modules=modules,
            simParams=simParams)
