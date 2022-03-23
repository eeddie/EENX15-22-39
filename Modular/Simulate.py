#
#   Simulate.py
#
#   Innehåller en main-funktion för simulering av drivlinan
#

from Modules import *
from Functions import batchNetlist, simulateNetlist

if __name__ == "__main__":

    
    netlist = f""".title drivlina
{getInverterControlNetlist("inverterControl", Gain=100)}
{getMosfetNetlist("mosfet", "IPI200N25N3")}
{getIGBTNetlist("IGBT", "FGW40N120WE")}
{getInverterNetlist("inverter", Mod=1, Freq=100, TranSubCir="mosfet")}  ;MOSType="IPI200N25N3"
{getInverterGroundNetlist("invGnd")}
{getStaticLoadNetlist("load")}
{getLoadGroundNetlist("loadGnd")}
{getXCapNetlist("xCap")}
{getNoLoadFilterNetlist("noLFilter")}
{getACCommonModeChokeNetlist("acCMC")}
{getNoBatteryFilterNetlist("noBFilter")}
{getBatteryGroundNetlist("batGnd")}
{getSimpleBatteryNetlist("battery")}

Xbattery BatPos BatNeg BatCase {"battery"}
Xbatfilt BatPos BatNeg InvPos InvNeg {"xCap"}


Xinverter InvPos InvNeg InvA InvB InvC InvCase {"inverter"}

Xloadfilter InvA InvB InvC PhA PhB PhC {"acCMC"}
Xload PhA PhB PhC LoadCase {"load"}

XbatGnd BatCase 0 {"batGnd"}
XinvGnd InvCase 0 {"invGnd"}
XloadGnd LoadCase 0 {"loadGnd"}



.inc .\\PySpice\\libs\\MOS.lib

.ic v(InvA)=0 v(InvB)=0 v(InvC)=0
.option method=trap

.options reltol=3e-3   ; > 1ms  "Never larger than 0.003!"
.options abstol=11e-9  ; > 10ns
.options itl4=31       ; > 30
.options gmin=1e-10    ;        "Minimum conductance"
.options cshunt=1e-15  ;        "Capacitance added from each node to ground"


.save i(l.xload.l1)

.tran 5ns 110ms 100ms 5ns
.end"""


    batchNetlist(netlist, f"out",  log=False)


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