def getInverterControlNetlist(Fs, Rg, Gain, OverlapProtection, name):
    return f""".subckt {name} Freq Mod E1 E2 E3 E4 E5 E6 G1 G2 G3 G4 G5 G6
BSin_A Ph_A 0 V= V(M)*sin(2*Pi*V(Frq)*time)
BSin_B Ph_B 0 V= V(M)*sin(2*Pi*V(Frq)*time-2*Pi/3)
BSin_C Ph_C 0 V= V(M)*sin(2*Pi*V(Frq)*time+2*Pi/3)
BE_PWM_A PWM_A 0 V= 15*tanh({Gain}*(V(Ph_A)-{OverlapProtection}-V(Triangle)))
BE_PWM_B PWM_B 0 V= 15*tanh({Gain}*(V(Ph_B)-{OverlapProtection}-V(Triangle)))
BE_PWM_C PWM_C 0 V= 15*tanh({Gain}*(V(Ph_C)-{OverlapProtection}-V(Triangle)))
BE_PWM_A_n PWM_A_n 0 V= 15*tanh({Gain}*(V(Ph_A)+{OverlapProtection}-V(Triangle)))
BE_PWM_B_n PWM_B_n 0 V= 15*tanh({Gain}*(V(Ph_B)+{OverlapProtection}-V(Triangle)))
BE_PWM_C_n PWM_C_n 0 V= 15*tanh({Gain}*(V(Ph_C)+{OverlapProtection}-V(Triangle)))
BTri Triangle 0 V= (2/Pi)*asin(sin(2*Pi*{Fs}*Time))
EDr1 N001 E1 PWM_A 0 1
EDr3 N003 E3 PWM_B 0 1
EDr5 N005 E5 PWM_C 0 1
EDr2 N002 E2 0 PWM_A_n 1
EDr4 N004 E4 0 PWM_B_n 1
EDr6 N006 E6 0 PWM_C_n 1
Rg1 N001 G1 {Rg}
Rg2 N002 G2 {Rg}
Rg3 N003 G3 {Rg}
Rg4 N004 G4 {Rg}
Rg5 N005 G5 {Rg}
Rg6 N006 G6 {Rg}
E1 Frq 0 Freq 0 1
E2 M 0 Mod 0 1
.ends {name}"""

def getInverterNetlist(Mod, Freq, MOStype, ParCap, name):
    return f""".subckt {name} Pos Neg A B C Case
V_mod N005 0 {Mod}
V_freq N003 0 {Freq}
M1 Pos G1 A A {MOStype}
M2 A G2 Neg 0 {MOStype}
M3 Pos G3 B B {MOStype}
M4 B G4 Neg 0 {MOStype}
M5 Pos G5 C C {MOStype}
M6 C G6 Neg 0 {MOStype}
XPWM1 N003 N005 A Neg B Neg C Neg G1 G2 G3 G4 G5 G6 inverterControl
C1 A Case {ParCap}
C2 B Case {ParCap}
C3 C Case {ParCap}
.ends {name}"""

def getStaticLoadNetlist(R_load, L_load, ParCapPh, ParCapY, name):
    return f""".subckt {name} A B C Case
R1 A N001 {R_load}
L1 N001 N {L_load}
R2 B N002 {R_load}
L2 N002 N {L_load}
R3 C N003 {R_load}
L3 N003 N {L_load}
C1 A Case {ParCapPh}
C2 B Case {ParCapPh}
C3 C Case {ParCapPh}
C4 N Case {ParCapY}
.ends {name}"""

def getSimpleBatteryNetlist(Voltage, R_self, L_self, RampTime, ParCapP, ParCapN, name):
    return f""".subckt {name} Pos Neg Case
V1 N001 Neg PULSE(0V {Voltage} 0s {RampTime})
R1 N001 N002 {R_self}
L1 N002 Pos {L_self}
C1 Pos Case {ParCapP}
C2 Pos Case {ParCapN}
.ends {name}
"""