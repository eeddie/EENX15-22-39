# 
#   Modules.py
#
#   Innehåller klasser för varje modul
#


class Module:
    name: str
    params: dict

    def __init__(self, name):
        self.name = name

    def getNetlist(self): ""


class InverterControlModule(Module):

    def __init__(self,
                 name="InverterControlModule",
                 Fs=1000,  # Switchfrekvens
                 Rg=1.5,
                 # Gateresistans                                      NOTE: Tagen från extern källa med AN-1001 IGBT:er
                 Gain=1000,
                 # Switchningens skarphet                                gain på 1000 ger rise-/fall-time på 10 ns
                 OverlapProtection=0.01
                 # Switchmarginal mellan positiv och negativ transistor   TODO: Välj ett passande default-värde
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
EDr1 G1 E1 PWM_A 0 1
EDr3 G3 E3 PWM_B 0 1
EDr5 G5 E5 PWM_C 0 1
EDr2 G2 E2 0 PWM_A_n 1
EDr4 G4 E4 0 PWM_B_n 1
EDr6 G6 E6 0 PWM_C_n 1
E1 Frq 0 Freq 0 1
E2 M 0 Mod 0 1
.ends {self.name}"""




class InternalMosfetModule(Module):
    
    def __init__(self, 
        name = "TransistorModule",
        MOSType = "IPI200N25N3",
        Rg = 1.5,
        ):

        self.name = name
        self.params = {"MOSType": MOSType, "Rg": Rg}

    def getNetlist(self):
        return f""".subckt {self.name} Drain Gate Source
Rg Gate MGate {self.params["Rg"]}
M1 Drain MGate Source Source {self.params["MOSType"]}
.ends {self.name}
.lib /Modular/libs/MOSFET/MOS.lib"""


class SubcircuitMosfetModule(Module):
    
    def __init__(self, 
        name = "TransistorModule",
        MOSType = "IPWS65R022CFD7A_L0",
        MOSLib = "IFX_CFD7A_650V.lib",
        Rg = 1.5,
        ):

        self.name = name
        self.params = {"MOSType": MOSType, "MOSLib": MOSLib, "Rg": Rg}

    def getNetlist(self):
        return f""".subckt {self.name} Drain Gate Source
Rg Gate MGate {self.params["Rg"]}
X1 Drain MGate Source {self.params["MOSType"]}
.ends {self.name}
.lib /Modular/libs/MOSFET/{self.params["MOSLib"]}"""


class IGBTModule(Module):

    def __init__(self,
        name = "TransistorModule",
        IGBTType = "rgw00ts65chr"
        ):
        
        return NotImplementedError("IGBTModule gate resistance was previously implemented in InverterControlModule but is removed and should be implemented in IGBTModule before use.")
        self.name = name
        self.params = {"IGBTType": IGBTType}

    def getNetlist(self):
        return f""".subckt {self.name} Collector Gate Emitter
X1 Collector Gate Emitter {self.params["IGBTType"]}
.ends {self.name}
.lib /Modular/libs/IGBT/{self.params["IGBTType"]}.lib"""


class SwitchModule(Module):
        
        def __init__(self,
            name = "TransistorModule",
            v_t = "0",
            r_on = "20m",
            r_off= "130k"):

            self.name = name
            self.params = {"v_t": v_t, "r_on": r_on, "r_off": r_off}
    
        def getNetlist(self):
            return f""".subckt {self.name} Source Gate Drain
            S1 Drain Source Gate Drain swmod
            D1 Drain Source dmod
            .model dmod d
            .model swmod sw vt={self.params["v_t"]} ron={self.params["r_on"]} roff={self.params["r_off"]}
            .ends {self.name}"""

class InverterModule(Module):

    def __init__(self,
        name = "InverterModule",
        invConModName = "InverterControlModule",    # Inverter controller module name
        tranModName = "TransistorModule",               # Transistor subcircuit name
        Mod = 1,
        Freq = 100,
        ParCapA = 1.4*(10**-12),       # Parasiterande kapacitans fas A till hölje. 
        ParCapB = 2.0*(10**-12),       # Parasiterande kapacitans fas B till hölje. 
        ParCapC = 0.7*(10**-12),       # Parasiterande kapacitans fas C till hölje. 
        ParCapP = 1.1*(10**-12),       # Parasiterande kapacitans positiv till hölje. 
        ParCapN = 2.0*(10**-12),       # Parasiterande kapacitans negativ till hölje. 
        ):
        
        self.name = name
        self.params = {
            "Mod": Mod,
            "Freq": Freq,
            "InvConModName": invConModName,
            "TranModName": tranModName,
            "ParCapA": ParCapA,       
            "ParCapB": ParCapB,       
            "ParCapC": ParCapC,       
            "ParCapP": ParCapP,       
            "ParCapN": ParCapN,       
    }

    def getNetlist(self) -> str: return f""".subckt {self.name} Pos Neg A B C Case
V_mod N005 0 {self.params["Mod"]}
V_freq N003 0 {self.params["Freq"]}
X1 Pos G1 A {self.params["TranModName"]}
X2 A G2 Neg {self.params["TranModName"]}
X3 Pos G3 B {self.params["TranModName"]}
X4 B G4 Neg {self.params["TranModName"]}
X5 Pos G5 C {self.params["TranModName"]}
X6 C G6 Neg {self.params["TranModName"]}
XPWM1 N003 N005 A Neg B Neg C Neg G1 G2 G3 G4 G5 G6 {self.params["InvConModName"]}
C1 A Case {self.params["ParCapA"]}
C2 B Case {self.params["ParCapB"]}
C3 C Case {self.params["ParCapC"]}
C4 Pos Case {self.params["ParCapP"]}
C5 Neg Case {self.params["ParCapN"]}
.ends {self.name}"""


class StaticLoadModule(Module):

    def __init__(self,
                 name="LoadModule",
                 R_load=1.09,
                 # Lastresistans                                 TODO: 1.09 Ω är resistansen vid DC, kolla Thomas "Circuit Parameters.docx" för frekvensberoende resistans.
                 L_load=20 * (10 ** -3),  # Lastinduktans
                 ParCapA=12 * (10 ** -12),  # Parasiterande kapacitans fas A till Hölje
                 ParCapB=15 * (10 ** -12),  # Parasiterande kapacitans fas B till Hölje
                 ParCapC=18 * (10 ** -12),  # Parasiterande kapacitans fas C till Hölje
                 ParCapN=55 * (10 ** -12),  # Parasiterande kapacitans neutral till Hölje
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
                 name="BatteryModule",
                 Voltage=400,  # Batterispänning
                 RampTime=0.001,  # Upprampningstid
                 R_self=0.1,
                 # Serieresistans batteri                        NOTE: 0.1 Ω är resistansen vid DC, kolla Thomas "Circuit Parameters.docx" för frekvensberoende resistans.
                 L_self=500 * (10 ** -9),  # Serieinduktans batteri
                 ParCapP=52 * (10 ** -12),  # Parasiterande kapacitans positiv till hölje
                 ParCapN=48 * (10 ** -12),  # Parasiterande kapacitans negativ till hölje
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
B1 N001 Neg v={self.params["Voltage"]} * tanh({1 / self.params["RampTime"]} * time)
R1 N001 N002 {self.params["R_self"]}
L1 N002 Pos {self.params["L_self"]}
C1 Pos Case {self.params["ParCapP"]}
C2 Neg Case {self.params["ParCapN"]}
.ends {self.name}"""



# X-cap mellan node och inverter
class XCapModule(Module):
    
    def __init__(self,
        name = "XCapModule",
        C_self = 500*10**-6,
        R_self = 1.9*10**-3
        ):
        self.name = name
        self.params = {
            "C_self": C_self,
            "R_self": R_self
        }

    def getNetlist(self):
        return f""".subckt {self.name} Pos Neg
C1 Pos Node {self.params["C_self"]}
R1 Node Neg {self.params["R_self"]}
.ends {self.name}"""


class NoDCCommonModeChokeModule(Module):

    def __init__(self,
        name = "DCCommonModeChokeModule"
    ):
        self.params = {}

    def getNetlist(self):
        return f""".subckt {self.name} BatPos BatNeg InvPos InvNeg
        V0 BatPos InvPos 0V
        V1 BatNeg InvNeg 0V
        .ends {self.name}"""


# common mode choke på DC-sidan
class DCCommonModeChokeModule(Module):

    def __init__(self,
        name = "DCCommonModeChokeModule",
        R_ser       = 20    *10**-3,
        L_choke     = 51    *10**-3,
        Coupling    = 0.95
    ):
        self.name = name
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
class NoACCommonModeChokeModule(Module):

    def __init__(self,
        name = "ACCommonModeChokeModule"):
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
        name = "ACCommonModeChokeModule",                           
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

    def __init__(self, name="LoadGroundModule", R=1.59 * (10 ** (-3)), C=8.96 * (10 ** (-9)), L=800.0 * (10 ** (-9))):
        super().__init__(name, R, C, L)

    def getNetlist(self):
        return super().getNetlist()


class InverterGroundModule(GroundingModule):
    def __init__(self, name="InverterGroundModule", R=1.59 * (10 ** (-3)), C=4.48 * (10 ** (-9)),
                 L=400.0 * (10 ** (-9))):
        super().__init__(name, R, C, L)

    def getNetlist(self):
        return super().getNetlist()


class BatteryGroundModule(GroundingModule):
    def __init__(self, name="BatteryGroundModule", R=1.59 * (10 ** (-3)), C=3.36 * (10 ** (-9)),
                 L=300.0 * (10 ** (-9))):
        super().__init__(name, R, C, L)

    def getNetlist(self):
        return super().getNetlist()
