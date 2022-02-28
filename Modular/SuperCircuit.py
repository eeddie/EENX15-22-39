# 
# SuperCircuit.py
#
# Innehåller funktioner för att skapa en netlist för hela kretsen, som tar in de olika modulerna som subcircuits
#

import ModuleNetlists as netlist
import os



def exampleNetlist():
    batteryNetlist = netlist.getSimpleBatteryNetlist('battery', 400, 0.005)
    inverterControlNetlist = netlist.getInverterControlNetlist('inverterControl')
    inverterNetlist = netlist.getInverterNetlist('inverter', 1, 50, 'IPI200N25N3')
    loadNetlist = netlist.getStaticLoadNetlist('RLload')

    netlist_file = f'example.cir'
    log_file = f'example.log'
    raw_file = f'example.raw'

    f = open(netlist_file, 'w')
    f.write(f"""example_supercircuit
Xbat pos neg batcase battery
Xinv pos neg A B C invcase inverter
Xload A B C loadcase RLload
R1 batcase 0 50
R2 invcase 0 50
R3 loadcase 0 50

{batteryNetlist}

{inverterControlNetlist}

{inverterNetlist}

{loadNetlist}

.model NMOS NMOS
.model PMOS PMOS
.inc .\\PySpice\\libs\MOS.lib
.tran 1us 200m 0 1us
.control
write
.endc""")
    f.close()

    os.system(f'C:\\Spice64\\bin\\ngspice_con.exe -b -r {raw_file} -o {log_file} {netlist_file}')

if __name__ == '__main__':
    exampleNetlist()
