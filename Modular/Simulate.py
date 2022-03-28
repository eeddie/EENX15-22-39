#
#   Simulate.py
#
#   Innehåller en main-funktion för simulering av drivlinan
#

import os
from Modules import *
from Functions import *


if __name__ == "__main__":

    # Mata in parametrarna till modulerna här i modulens constructor
    # Varje modul har sitt netlist-namn från vilken plats den har i den hela drivlinan. ex. XCapModule och DCCommonModeChokeModule har båda namnet DCFilterModule i netlisten.
    # Vill man byta ut ex. XCapModule med DCCommonModeChokeModule byter man ut dem i denna listan.
    # Vill man seriekoppla XCap och CMC får man sätta in unika namn för de två modulerna i denna listan, ha dem båda i listan nedan och ändra netlistan för drivlinan med de två nya namnen.
    modules = [
        InverterControlModule(),
        MosfetModule(),
        InverterModule(),
        InverterGroundModule(),
        StaticLoadModule(),
        LoadGroundModule(),
        XCapModule(),
        ACCommonModeChokeModule(),
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

Xbatfilt BatPos BatNeg InvPos InvNeg DCFilterModule

Xinverter InvPos InvNeg InvA InvB InvC InvCase InverterModule

Xloadfilter InvA InvB InvC PhA PhB PhC ACFilterModule

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

    # Simulera netlisten och outputta till en .raw fil
    batchNetlist(netlist, f"out",  log=False)

    # Spara datan från den genomförda simuleringen 
    saveSim("params.json", 
        modules = modules, 
        simParams = simParams,
        results = {}            # Beräknar inget resultat för tillfället.
        )

    


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