#
#   Simulate.py
#
#   Innehåller en main-funktion för simulering av drivlinan
#

import os
from Modules import *
from Functions import *


def getSimulation()-> list[str, list[Module], dict]:

    modules = [
        InverterControlModule(),
        SwitchModule(),
        InverterModule(),
        InverterGroundModule(),
        StaticLoadModule(),
        LoadGroundModule(),
        XCapModule(),
        DCCommonModeChokeModule(),  # Or NoDCCommonModeChokeModule()
        ACCommonModeChokeModule(),  # or NoACCommonModeChokeModule()
        BatteryGroundModule(),
        SimpleBatteryModule()
    ]

    # Simuleringsparametrar
    simParams = {
        "tstep": "1ns",
        "tstart": "100ms",
        "tstop": "110ms",
        "method": "trap"
    }

    netlist = f""".title drivlina
{os.linesep.join(module.getNetlist() for module in modules)}

Xbattery BatPos BatNeg BatCase BatteryModule

* Strömmättning batteri i(Vbatpos)  i(Vbatneg)
VDC_P BatPos CMCPos 0 
VDC_N BatNeg CMCNeg  0

Xxcap CMCPos CMCNeg XCapModule

Xdccmc CMCPos CMCNeg InvPos InvNeg DCCommonModeChokeModule

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
*.options gmin=1e-10    ;        "Minimum conductance"
*.options cshunt=1e-15  ;        "Capacitance added from each node to ground"

.save i(VAC_A)
.save i(VAC_B)
.save i(VAC_C)
.save i(VDC_P)
.save i(VDC_N)

.save i(xinvgnd.l1)
.save i(xbatgnd.l1)
.save i(xloadgnd.l1)

.tran {simParams["tstep"]} {simParams["tstop"]} {simParams["tstart"]}
.end"""

    return netlist, modules, simParams



if __name__ == "__main__":
    netlist, modules, simParams = getSimulation()

    # Simulera netlisten och outputta till en .raw fil
    batchNetlist(netlist, f"out",  log=False)

    # Spara datan från den genomförda simuleringen 
    saveSim("params.json", 
        modules = modules, 
        simParams = simParams,
        results = {}            # Beräknar inget resultat för tillfället.
        )