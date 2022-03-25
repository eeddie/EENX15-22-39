# 
#   Modules.py
#
#   Innehåller funktioner för att hämta netlists på de olika krets-modulerna
#

def getInverterControlNetlist(
    name,
    Fs                  = 10000,  # Switchfrekvens                                        
    Rg                  = 1.5,   # Gateresistans                                          NOTE: Tagen från extern källa med AN-1001 IGBT:er
    Gain                = 1000,   # Switchningens skarphet                                gain på 1000 ger rise-/fall-time på 10 ns
    OverlapProtection   = 0.01,  # Switchmarginal mellan positiv och negativ transistor   TODO: Välj ett passande default-värde 
    ):
    return f"""
.subckt {name} Freq Mod E1 E2 E3 E4 E5 E6 G1 G2 G3 G4 G5 G6
BSin_A      Ph_A    0 V= V(M)*sin(2*Pi*V(Frq)*time)
BSin_B      Ph_B    0 V= V(M)*sin(2*Pi*V(Frq)*time-2*Pi/3)
BSin_C      Ph_C    0 V= V(M)*sin(2*Pi*V(Frq)*time+2*Pi/3)
BE_PWM_A    PWM_A   0 V= 15*tanh({Gain}*(V(Ph_A)-{OverlapProtection}-V(Triangle)))
BE_PWM_B    PWM_B   0 V= 15*tanh({Gain}*(V(Ph_B)-{OverlapProtection}-V(Triangle)))
BE_PWM_C    PWM_C   0 V= 15*tanh({Gain}*(V(Ph_C)-{OverlapProtection}-V(Triangle)))
BE_PWM_A_n  PWM_A_n 0 V= 15*tanh({Gain}*(V(Ph_A)+{OverlapProtection}-V(Triangle)))
BE_PWM_B_n  PWM_B_n 0 V= 15*tanh({Gain}*(V(Ph_B)+{OverlapProtection}-V(Triangle)))
BE_PWM_C_n  PWM_C_n 0 V= 15*tanh({Gain}*(V(Ph_C)+{OverlapProtection}-V(Triangle)))
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


def getMosfetNetlist(
    name,
    MOSType
    ):
    return f""".subckt {name} Drain Gate Source
M1 Drain Gate Source Source {MOSType}
.ends {name}"""


def getIGBTNetlist(
    name,
    IGBTType
    ):
    return f""".subckt {name} Collector Gate Emitter
X1 Collector Gate Emitter {IGBTType}
.ends {name}
.lib /Modular/libs/IGBT/{IGBTType}.lib"""


def getInverterNetlist(
    name,
    Mod, 
    Freq,                       
    TranSubCir,                      # Mosfet-typ
    ParCapA     = 1.4*(10**-12),  # Parasiterande kapacitans fas A till hölje. 
    ParCapB     = 2.0*(10**-12),  # Parasiterande kapacitans fas B till hölje. 
    ParCapC     = 0.7*(10**-12),  # Parasiterande kapacitans fas C till hölje. 
    ParCapP     = 1.1*(10**-12),  # Parasiterande kapacitans positiv till hölje. 
    ParCapN     = 2.0*(10**-12),  # Parasiterande kapacitans negativ till hölje. 
    ):
    return f""".subckt {name} Pos Neg A B C Case
V_mod N005 0 {Mod}
V_freq N003 0 {Freq}
X1 Pos G1 A {TranSubCir}
X2 A G2 Neg {TranSubCir}
X3 Pos G3 B {TranSubCir}
X4 B G4 Neg {TranSubCir}
X5 Pos G5 C {TranSubCir}
X6 C G6 Neg {TranSubCir}
XPWM1 N003 N005 A Neg B Neg C Neg G1 G2 G3 G4 G5 G6 inverterControl
C1 A Case {ParCapA}
C2 B Case {ParCapB}
C3 C Case {ParCapC}
C4 Pos Case {ParCapP}
C5 Neg Case {ParCapN}
.ends {name}"""

def getStaticLoadNetlist(
    name,                           
    R_load      = 1.09,             # Lastresistans                                 TODO: 1.09 Ω är resistansen vid DC, kolla Thomas "Circuit Parameters.docx" för frekvensberoende resistans.
    L_load      = 20*(10**-3),      # Lastinduktans
    ParCapA     = 12*(10**-12),     # Parasiterande kapacitans fas A till Hölje
    ParCapB     = 15*(10**-12),     # Parasiterande kapacitans fas B till Hölje
    ParCapC     = 18*(10**-12),     # Parasiterande kapacitans fas C till Hölje
    ParCapN     = 55*(10**-12),     # Parasiterande kapacitans neutral till Hölje
    ):
    return f""".subckt {name} A B C Case
R1 A N001 {R_load}
L1 N001 N {L_load}
R2 B N002 {R_load}
L2 N002 N {L_load}
R3 C N003 {R_load}
L3 N003 N {L_load}
C1 A Case {ParCapA}
C2 B Case {ParCapB}
C3 C Case {ParCapC}
C4 N Case {ParCapN}
.ends {name}"""

def getSimpleBatteryNetlist(
    name,
    Voltage     = 400,              # Batterispänning
    RampTime    = 0.001,            # Upprampningstid
    R_self      = 0.1,              # Serieresistans batteri                        NOTE: 0.1 Ω är resistansen vid DC, kolla Thomas "Circuit Parameters.docx" för frekvensberoende resistans.
    L_self      = 500*(10**-9),     # Serieinduktans batteri
    ParCapP     = 52*(10**-12),     # Parasiterande kapacitans positiv till hölje
    ParCapN     = 48*(10**-12),      # Parasiterande kapacitans negativ till hölje
    ):
    return f""".subckt {name} Pos Neg Case
*V1 N001 Neg PULSE(0V {Voltage} 0s {RampTime}) 
B1 N001 Neg v={Voltage} * tanh({1/RampTime} * time)
R1 N001 N002 {R_self}
L1 N002 Pos {L_self}
C1 Pos Case {ParCapP}
C2 Neg Case {ParCapN}
.ends {name}"""



# Inget filter mellan batteri och inverter. 0 V mellan de två
def getNoBatteryFilterNetlist(
    name
):
    return f""".subckt {name} BatPos BatNeg InvPos InvNeg
V0 BatPos InvPos 0V
V1 BatNeg InvNeg 0V
.ends {name}"""

# X-cap mellan node och inverter
def getXCapNetlist(
    name,
    C_self = 500*10**-6,
    R_self = 1.9*10**-3
):
    return f""".subckt {name} BatPos BatNeg InvPos InvNeg
V0 BatPos InvPos 0V
V1 BatNeg InvNeg 0V
C1 BatPos Node {C_self}
R1 Node BatNeg {R_self}
.ends {name}"""

# common mode choke på DC-sidan
def getDCCommonModeChokeNetlist(
    name,
    R_ser       = 20    *10**-3,
    L_choke     = 51    *10**-3,
    Coupling    = 0.95
):
    return f""".subckt {name} BatPos BatNeg InvPos InvNeg
R1 BatPos PosNode {R_ser}
L1 PosNode InvPos {L_choke}
R2 BatNeg NegNode {R_ser}
L2 NegNode InvNeg {L_choke}
K12 L1 L2 {Coupling}
.ends {name}"""

# Ingen common-mode choke eller annat filter, 0 V mellan inverter och last
def getNoLoadFilterNetlist(
    name
):
    return f""".subckt {name} InA InB InC OutA OutB OutC
V0 InA OutA 0V
V1 InB OutB 0V
V2 InC OutC 0V
.ends {name}"""

def getACCommonModeChokeNetlist(
    name,                           
    R_ser        = 0.02,           # Serieresistans
    L_choke      = 51*(10**-3),    # Chokens induktans
    Coupling     = 0.95,           # Kopplingsfaktor mellan induktanserna, 0 < Coupling <= 1
    ):
    return f""".subckt {name} A_inv B_inv C_inv A_load B_load C_load
R1 A_inv N001 {R_ser}
L1 N001 A_load {L_choke}
R2 B_inv N002 {R_ser}
L2 N002 B_load {L_choke}
R3 C_inv N003 {R_ser}
L3 N003 C_load {L_choke}
K12 L1 L2 {Coupling}
K23 L2 L3 {Coupling}
K31 L3 L1 {Coupling}
.ends {name}"""

def getGroundingNetlist(
    name,
    resistance,
    capacitance,
    inductance,
):
    return f""".subckt {name} case ground
C1 case ground {capacitance}
R1 case node {resistance}
L1 node ground {inductance}
.ends {name}"""

def getLoadGroundNetlist(name,      resistance  = 1.59 * (10 ** (-3)),  capacitance = 8.96 * (10 ** (-9)),  inductance  = 800.0 * (10 ** (-9))):
    return getGroundingNetlist(name, resistance, capacitance, inductance)

def getInverterGroundNetlist(name,  resistance  = 1.59 * (10 ** (-3)),  capacitance = 4.48 * (10 ** (-9)),  inductance  = 400.0 * (10 ** (-9))):
    return getGroundingNetlist(name, resistance, capacitance, inductance)

def getBatteryGroundNetlist(name,   resistance = 1.59 * (10 ** (-3)),   capacitance=3.36 * (10 ** (-9)),    inductance=300.0 * (10 ** (-9))):
    return getGroundingNetlist(name, resistance, capacitance, inductance)