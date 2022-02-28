import os
from ngspice_netlist import *
def main():
    for i in range(0,4):
        netlist_file = f'syncbuck{i}.cir'
        log_file = f'syncbuck{i}.log'
        raw_file = f'syncbuck{i}.raw'
        duty = 0.20 + i*0.10
        build_buck_netlist('BSB012N03LX3', '1u', '0.25', '33u', '0.5', '1.0Meg', str(duty), '0.25', 'BSB012N03LX3', '100', netlist_file)
        os.system(f'C:\\Spice64\\bin\\ngspice_con.exe -b -r {raw_file} -o {log_file} {netlist_file}')

def example():
    build_buck_netlist('BSB012N03LX3', '1u', '0.25', '33u', '0.5', '1.0Meg', '0.28', '0.25', 'BSB012N03LX3', '100', 'example.cir')


if __name__ == '__main__':
    main()
