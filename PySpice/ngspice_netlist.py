def build_buck_netlist(M1: str, L1: str, R1: str, C1: str, R2: str, Fsw: str, Duty: str, Rg: str, M2: str, Gain: str, filename: str):
    netlist = f"""Syncbuck
Vin N001 0 PULSE(0 12 0 20us)
M1 N001 G1 E1 {M1}
L1 E1 Out {L1}
R1 Out Cin {R1}
C1 Cin 0 {C1}
R2 Out 0 {R2}
BTri Triangle 0 V=0.5 + asin(sin(2*Pi*Fsw*Time))/Pi
BE_PWMa N003 0 V=15*tanh(Gain*(Duty-V(Triangle)))
BE_PWMb N004 0 V=15*tanh(Gain*(-(Duty+0.03)+V(Triangle)))
EDr1 N002 E1 N003 0 1
EDr2 N005 0 N004 0 1
Rg1 N002 G1 {Rg}
Rg2 N005 G2 {Rg}
M2 E1 G2 0 0 {M2}
.model NMOS NMOS
.model PMOS PMOS
.inc .\MOS.lib
.ic V(Out)=0
.param Duty = {Duty}
.param Gain = {Gain}
.param Fsw= {Fsw}
.tran 1ns 180us 0us 1ns uic
.control
write
.endc
.end"""
    f = open(filename, 'w')
    f.write(netlist)
    f.close()