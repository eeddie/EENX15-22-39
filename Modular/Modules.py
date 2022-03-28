# 
#   Modules.py
#
#   Innehåller funktioner för att hämta netlists på de olika krets-modulerna
#


class Module:
    name: str
    params: dict
    
    def __init__(self, name):
        self.name = name

    def getNetlist(self): ""




class InverterControlModule(Module):
    
    def __init__(self,
        name = "InverterControlModule",
        Fs=1000,                # Switchfrekvens
        Rg=1.5,                 # Gateresistans                                          NOTE: Tagen från extern källa med AN-1001 IGBT:er
        Gain=1000,              # Switchningens skarphet                                gain på 1000 ger rise-/fall-time på 10 ns
        OverlapProtection=0.01  # Switchmarginal mellan positiv och negativ transistor   TODO: Välj ett passande default-värde 
        ):

        self.name = name
        self.params = {
            "Fs": Fs,                
            "Rg": Rg,                  
            "Gain": Gain,               
            "OverlapProtection": OverlapProtection,  
        }

    def getNetlist(self):
        return f"""
.subckt {self.name} Freq Mod E1 E2 E3 E4 E5 E6 G1 G2 G3 G4 G5 G6
BSin_A      Ph_A    0 V= V(M)*sin(2*Pi*V(Frq)*time)
BSin_B      Ph_B    0 V= V(M)*sin(2*Pi*V(Frq)*time-2*Pi/3)
BSin_C      Ph_C    0 V= V(M)*sin(2*Pi*V(Frq)*time+2*Pi/3)
BE_PWM_A    PWM_A   0 V= 15*tanh({self.params["Gain"]}*(V(Ph_A)-{self.params["OverlapProtection"]}-V(Triangle)))
BE_PWM_B    PWM_B   0 V= 15*tanh({self.params["Gain"]}*(V(Ph_B)-{self.params["OverlapProtection"]}-V(Triangle)))
BE_PWM_C    PWM_C   0 V= 15*tanh({self.params["Gain"]}*(V(Ph_C)-{self.params["OverlapProtection"]}-V(Triangle)))
BE_PWM_A_n  PWM_A_n 0 V= 15*tanh({self.params["Gain"]}*(V(Ph_A)+{self.params["OverlapProtection"]}-V(Triangle)))
BE_PWM_B_n  PWM_B_n 0 V= 15*tanh({self.params["Gain"]}*(V(Ph_B)+{self.params["OverlapProtection"]}-V(Triangle)))
BE_PWM_C_n  PWM_C_n 0 V= 15*tanh({self.params["Gain"]}*(V(Ph_C)+{self.params["OverlapProtection"]}-V(Triangle)))
BTri Triangle 0 V= (2/Pi)*asin(sin(2*Pi*{self.params["Fs"]}*Time))
EDr1 N001 E1 PWM_A 0 1
EDr3 N003 E3 PWM_B 0 1
EDr5 N005 E5 PWM_C 0 1
EDr2 N002 E2 0 PWM_A_n 1
EDr4 N004 E4 0 PWM_B_n 1
EDr6 N006 E6 0 PWM_C_n 1
Rg1 N001 G1 {self.params["Rg"]}
Rg2 N002 G2 {self.params["Rg"]}
Rg3 N003 G3 {self.params["Rg"]}
Rg4 N004 G4 {self.params["Rg"]}
Rg5 N005 G5 {self.params["Rg"]}
Rg6 N006 G6 {self.params["Rg"]}
E1 Frq 0 Freq 0 1
E2 M 0 Mod 0 1
.ends {self.name}"""



class MosfetModule(Module):
    
    def __init__(self, 
        name = "MOSFETModule",
        MOSType = "IPI200N25N3"
        ):
        self.name = name
        self.params = {"MOSType": MOSType}

    def getNetlist(self):
        return f""".subckt {self.name} Drain Gate Source
M1 Drain Gate Source Source {self.params["MOSType"]}
.ends {self.name}
.lib /Modular/libs/MOS.lib"""


class IGBTModule(Module):
    
    def __init__(self,
        name = "IGBTModule",
        IGBTType = "rgw00ts65chr"
        ):
        
        self.name = name
        self.params = {"IGBTType": IGBTType}


    def getNetlist(self):
        return f""".subckt {self.name} Collector Gate Emitter
X1 Collector Gate Emitter {self.params["IGBTType"]}
.ends {self.name}
.lib /Modular/libs/IGBT/{self.params["IGBTType"]}.lib"""


class InverterModule(Module):

    invConModName = "InverterControlModule"
    tranModName = "MOSFETModule"
    
    def __init__(self,
        name = "InverterModule",
        invConModName = "InverterControlModule",    # Inverter controller module name
        tranModName = "MOSFETModule",               # Transistor subcircuit name
        Mod = 1,
        Freq = 100,
        ParCapA = 1.4*(10**-12),       # Parasiterande kapacitans fas A till hölje. 
        ParCapB = 2.0*(10**-12),       # Parasiterande kapacitans fas B till hölje. 
        ParCapC = 0.7*(10**-12),       # Parasiterande kapacitans fas C till hölje. 
        ParCapP = 1.1*(10**-12),       # Parasiterande kapacitans positiv till hölje. 
        ParCapN = 2.0*(10**-12),       # Parasiterande kapacitans negativ till hölje. 
        ):
        
        self.name = name
        self.invConModName = invConModName
        self.tranModName = tranModName
        self.params = {
            "Mod": Mod, 
            "Freq": Freq,
            "ParCapA": ParCapA,       
            "ParCapB": ParCapB,       
            "ParCapC": ParCapC,       
            "ParCapP": ParCapP,       
            "ParCapN": ParCapN,       
    }

    def getNetlist(self) -> str: return f""".subckt {self.name} Pos Neg A B C Case
V_mod N005 0 {self.params["Mod"]}
V_freq N003 0 {self.params["Freq"]}
X1 Pos G1 A {self.tranModName}
X2 A G2 Neg {self.tranModName}
X3 Pos G3 B {self.tranModName}
X4 B G4 Neg {self.tranModName}
X5 Pos G5 C {self.tranModName}
X6 C G6 Neg {self.tranModName}
XPWM1 N003 N005 A Neg B Neg C Neg G1 G2 G3 G4 G5 G6 {self.invConModName}
C1 A Case {self.params["ParCapA"]}
C2 B Case {self.params["ParCapB"]}
C3 C Case {self.params["ParCapC"]}
C4 Pos Case {self.params["ParCapP"]}
C5 Neg Case {self.params["ParCapN"]}
.ends {self.name}"""

class StaticLoadModule(Module):
    
    def __init__(self,
        name = "LoadModule",
        R_load = 1.09,                 # Lastresistans                                 TODO: 1.09 Ω är resistansen vid DC, kolla Thomas "Circuit Parameters.docx" för frekvensberoende resistans.
        L_load = 20*(10**-3),          # Lastinduktans
        ParCapA = 12*(10**-12),        # Parasiterande kapacitans fas A till Hölje
        ParCapB = 15*(10**-12),        # Parasiterande kapacitans fas B till Hölje
        ParCapC = 18*(10**-12),        # Parasiterande kapacitans fas C till Hölje
        ParCapN = 55*(10**-12),        # Parasiterande kapacitans neutral till Hölje
    ):
        self.name = name
        self.params = {                           
            "R_load": R_load,      
            "L_load": L_load,          
            "ParCapA": ParCapA,        
            "ParCapB": ParCapB,        
            "ParCapC": ParCapC,        
            "ParCapN": ParCapN,        
        }


    def getNetlist(self): return f""".subckt {self.name} A B C Case
R1 A N001 {self.params["R_load"]}
L1 N001 N {self.params["L_load"]}
R2 B N002 {self.params["R_load"]}
L2 N002 N {self.params["L_load"]}
R3 C N003 {self.params["R_load"]}
L3 N003 N {self.params["L_load"]}
C1 A Case {self.params["ParCapA"]}
C2 B Case {self.params["ParCapB"]}
C3 C Case {self.params["ParCapC"]}
C4 N Case {self.params["ParCapN"]}
.ends {self.name}"""

class SimpleBatteryModule(Module):
    
    def __init__(self, 
        name = "BatteryModule",
        Voltage     = 400,              # Batterispänning
        RampTime    = 0.001,            # Upprampningstid
        R_self      = 0.1,              # Serieresistans batteri                        NOTE: 0.1 Ω är resistansen vid DC, kolla Thomas "Circuit Parameters.docx" för frekvensberoende resistans.
        L_self      = 500*(10**-9),     # Serieinduktans batteri
        ParCapP     = 52*(10**-12),     # Parasiterande kapacitans positiv till hölje
        ParCapN     = 48*(10**-12),      # Parasiterande kapacitans negativ till hölje
        ):
        
        self.name = name
        self.params = {
            "Voltage": Voltage,
            "RampTime": RampTime,
            "R_self": R_self,
            "L_self": L_self,
            "ParCapP": ParCapP,
            "ParCapN": ParCapN 
        }

    def getNetlist(self):
        return f""".subckt {self.name} Pos Neg Case
*V1 N001 Neg PULSE(0V {self.params["Voltage"]} 0s {self.params["RampTime"]}) 
B1 N001 Neg v={self.params["Voltage"]} * tanh({1/self.params["RampTime"]} * time)
R1 N001 N002 {self.params["R_self"]}
L1 N002 Pos {self.params["L_self"]}
C1 Pos Case {self.params["ParCapP"]}
C2 Neg Case {self.params["ParCapN"]}
.ends {self.name}"""



# Inget filter mellan batteri och inverter. 0 V mellan de två
class NoDCFilterModule(Module):
    
    def __init__(self,
        name = "DCFilterModule"
        ):
        self.name = name
        self.params = {}

    def getNetlist(self):
        return f""".subckt {self.name} BatPos BatNeg InvPos InvNeg
V0 BatPos InvPos 0V
V1 BatNeg InvNeg 0V
.ends {self.name}"""

# X-cap mellan node och inverter
class XCapModule(Module):
    
    def __init__(self,
        name = "DCFilterModule",
        C_self = 500*10**-6,
        R_self = 1.9*10**-3
        ):

        self.name = name
        self.params = {
            "C_self": C_self,
            "R_self": R_self
        }

    def getNetlist(self):
        return f""".subckt {self.name} BatPos BatNeg InvPos InvNeg
V0 BatPos InvPos 0V
V1 BatNeg InvNeg 0V
C1 BatPos Node {self.params["C_self"]}
R1 Node BatNeg {self.params["R_self"]}
.ends {self.name}"""

# common mode choke på DC-sidan
class DCCommonModeChokeModule(Module):

    def __init__(self,
        name = "DCFilterModule",
        R_ser       = 20    *10**-3,
        L_choke     = 51    *10**-3,
        Coupling    = 0.95
    ):
        self.name = name,
        self.params = {
            "R_ser": R_ser,
            "L_choke": L_choke,
            "Coupling": Coupling
        }
    
    def getNetlist(self):
        return f""".subckt {self.name} BatPos BatNeg InvPos InvNeg
R1 BatPos PosNode {self.params["R_ser"]}
L1 PosNode InvPos {self.params["L_choke"]}
R2 BatNeg NegNode {self.params["R_ser"]}
L2 NegNode InvNeg {self.params["L_choke"]}
K12 L1 L2 {self.params["Coupling"]}
.ends {self.name}"""

# Ingen common-mode choke eller annat filter, 0 V mellan inverter och last
class NoLoadFilterModule(Module):

    def __init__(self,
        name = "ACFilterModule"):
        self.name = name,
        self.params = {}
    
    def getNetlist(self):
        return f""".subckt {self.name} InA InB InC OutA OutB OutC
V0 InA OutA 0V
V1 InB OutB 0V
V2 InC OutC 0V
.ends {self.name}"""

class ACCommonModeChokeModule(Module):

    def __init__(self,
        name = "ACFilterModule",                           
        R_ser        = 0.02,           # Serieresistans
        L_choke      = 51*(10**-3),    # Chokens induktans
        Coupling     = 0.95,           # Kopplingsfaktor mellan induktanserna, 0 < Coupling <= 1
    ):
        self.name = name
        self.params = {
            "R_ser": R_ser,
            "L_choke": L_choke,
            "Coupling": Coupling
        }

    def getNetlist(self):
        return f""".subckt {self.name} A_inv B_inv C_inv A_load B_load C_load
R1 A_inv N001 {self.params["R_ser"]}
L1 N001 A_load {self.params["L_choke"]}
R2 B_inv N002 {self.params["R_ser"]}
L2 N002 B_load {self.params["L_choke"]}
R3 C_inv N003 {self.params["R_ser"]}
L3 N003 C_load {self.params["L_choke"]}
K12 L1 L2 {self.params["Coupling"]}
K23 L2 L3 {self.params["Coupling"]}
K31 L3 L1 {self.params["Coupling"]}
.ends {self.name}"""


class GroundingModule(Module):
    
    def __init__(self,
        name,
        R,
        C,
        L,
    ):
        self.name = name
        self.params = {
            "R": R,
            "C": C,
            "L": L
        }

    def getNetlist(self):
        return f""".subckt {self.name} case ground
C1 case ground {self.params["C"]}
R1 case node {self.params["R"]}
L1 node ground {self.params["L"]}
.ends {self.name}"""


class LoadGroundModule(GroundingModule):

    def __init__(self, name = "LoadGroundModule", R = 1.59 * (10 ** (-3)), C = 8.96 * (10 ** (-9)), L = 800.0 * (10 ** (-9))):
        super().__init__(name, R, C, L)

    def getNetlist(self):
        return super().getNetlist()

class InverterGroundModule(GroundingModule):
    def __init__(self, name = "InverterGroundModule", R =  1.59 * (10 ** (-3)), C = 4.48 * (10 ** (-9)), L = 400.0 * (10 ** (-9))):
        super().__init__(name, R, C, L)

    def getNetlist(self):
        return super().getNetlist()

class BatteryGroundModule(GroundingModule):
    def __init__(self, name = "BatteryGroundModule", R = 1.59 * (10 ** (-3)), C = 3.36 * (10 ** (-9)), L = 300.0 * (10 ** (-9))):
        super().__init__(name, R, C, L)

    def getNetlist(self):
        return super().getNetlist()