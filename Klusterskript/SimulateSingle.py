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


def randomInRange(start: float, end: float):
    return start + r.random() * (end - start)

def randomAroundCenter(center, factor = 0.03):
    return randomInRange((1-factor) * center, (1+factor) * center)


if __name__ == "__main__":

    modules: list = [
        InverterControlModule(
            Fs=randomAroundCenter(10**4)
        ),

        SwitchModule(),

        InverterModule(),

        InverterGroundModule(),

        StaticLoadModule(
            R_load =randomAroundCenter(1.09),
            L_load =randomAroundCenter(20e-3)),

        LoadGroundModule(),

        XCapModule(
            C_self=randomAroundCenter(500e-6)),
        
        DCCommonModeChokeModule(
            L_choke=randomAroundCenter(20e-3),
            Coupling=randomAroundCenter(51e-3)),
        
        ACCommonModeChokeModule(
            L_choke=randomAroundCenter(51e-3),
            Coupling=randomAroundCenter(0.95)),

        BatteryGroundModule(),

        SimpleBatteryModule(
            R_self=randomAroundCenter(0.1),
            L_self=randomAroundCenter(500e-9))
    ]

    # Simuleringsparametrar
    simParams = {
        "tstep": "1ns",
        "tstart": "100ms",
        "tstop": "110ms",
        "method": "trap"
    }

    netlist = createNetlist(modules, simParams)

    # Create the folder tmp/ if it does not exist
    if not os.path.exists("tmp"): os.makedirs("tmp")
    try:
        batchNetlist(netlist, os.path.join(os.path.dirname(__file__), "tmp", "sim" + str(sys.argv[1])), log=True)
    except ValueError:
        pass            
        # En simulering har misslyckats, raw-filen innehåller ingen data, detta skapar error i repairRaw, men då behöver vi inte reparera, utan fortsätter. Tomma raw-filer hanteras senare i ex. FFTRaw


    saveSim(filename=os.path.join(os.path.dirname(__file__), "tmp", "params" + str(sys.argv[1]) + ".npy"),
            modules=modules,
            simParams=simParams)
