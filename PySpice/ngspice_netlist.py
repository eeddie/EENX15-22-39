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
.inc .\libs\MOS.lib
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

def build_inverter_netlist(Modulation: str, Frequency: str, Fsw: str, MOStype: str, L_m: str, R_m: str, BatV: str, Gain: str, Rg: str, filename: str):
    netlist = f"""trefas med subcircuit
V_mod N005 0 {{Mod}}
V_freq N003 0 {{Freq}}
Vdc N001 0 PULSE(0V {BatV} 0s 5ms)
M1 N001 G1 A A {MOStype}
M2 A G2 0 0 {MOStype}
M3 N001 G3 B B {MOStype}
M4 B G4 0 0 {MOStype}
M5 N001 G5 C C {MOStype}
M6 C G6 0 0 {MOStype}
R1 A N002 {{R_motor}}
L1 N002 N {{L_motor}}
R2 B N004 {{R_motor}}
L2 N004 N {{L_motor}}
R3 C N006 {{R_motor}}
L3 N006 N {{L_motor}}
XPWM1 N003 N005 A 0 B 0 C 0 G1 G2 G3 G4 G5 G6 trefas_exempel

* block symbol definitions
.subckt trefas_exempel Freq Mod E1 E2 E3 E4 E5 E6 G1 G2 G3 G4 G5 G6
BSin_A Ph_A 0 V= V(M)*sin(2*Pi*V(Frq)*time)
BSin_B Ph_B 0 V= V(M)*sin(2*Pi*V(Frq)*time-2*Pi/3)
BSin_C Ph_C 0 V= V(M)*sin(2*Pi*V(Frq)*time+2*Pi/3)
BE_PWM_A PWM_A 0 V= 15*tanh(Gain*(V(Ph_A)-V(Triangle)))
BE_PWM_B PWM_B 0 V= 15*tanh(Gain*(V(Ph_B)-V(Triangle)))
BE_PWM_C PWM_C 0 V= 15*tanh(Gain*(V(Ph_C)-V(Triangle)))
BTri Triangle 0 V= (2/Pi)*asin(sin(2*Pi*Fs*Time))
EDr1 N001 E1 PWM_A 0 1
EDr3 N003 E3 PWM_B 0 1
EDr5 N005 E5 PWM_C 0 1
EDr2 N002 E2 0 PWM_A 1
EDr4 N004 E4 0 PWM_B 1
EDr6 N006 E6 0 PWM_C 1
Rg1 N001 G1 {Rg}
Rg2 N002 G2 {Rg}
Rg3 N003 G3 {Rg}
Rg4 N004 G4 {Rg}
Rg5 N005 G5 {Rg}
Rg6 N006 G6 {Rg}
E1 Frq 0 Freq 0 1
E2 M 0 Mod 0 1
.ends trefas_exempel

.model NMOS NMOS
.model PMOS PMOS
.inc .\libs\MOS.lib
.tran 1us 200m 0 1us
.control
plot i(L1) i(L2) i(L3)
write
.endc
.PARAM L_Motor = {L_m}
.PARAM R_Motor = {R_m}
.param Mod= {Modulation}
.param Freq = {Frequency}
.param Fs = {Fsw}
.param Gain = {Gain}
.end"""
    f = open(filename, 'w')
    f.write(netlist)
    f.close()