import os
from ngspice_netlist import *
def main():
    netlist_file = 'syncbuck1.cir'
    log_file = 'syncbuck1.log'
    raw_file = 'syncbuck1.raw'
    build_buck_netlist('BSB012N03LX3', '1u', '0.25', '33u', '0.5', '1.0Meg', '0.28', '0.25', 'BSB012N03LX3', '100', netlist_file)
    os.system(f'C:\\Spice64\\bin\\ngspice_con.exe -b -r {raw_file} -o {log_file} {netlist_file}')


if __name__ == '__main__':
    main()
