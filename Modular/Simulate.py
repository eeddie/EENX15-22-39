#
#   Simulate.py
#
#   Innehåller en main-funktion för simulering av drivlinan
#

import os
import sys
from Modules import *
from Functions import *
import random as r



def createNetlist(modules, simParams):
    return f""".title drivlina
{os.linesep.join(module.getNetlist() for module in modules)}
    
Xbattery BatPos BatNeg BatCase BatteryModule
    
* Strömmättning batteri i(Vbatpos)  i(Vbatneg)
VDC_P BatPos CMCPos 0 
VDC_N BatNeg CMCNeg  0

Xdccmc CMCPos CMCNeg InvPos InvNeg DCCommonModeChokeModule

Xxcap InvPos InvNeg XCapModule

Xbatfilt BatPos BatNeg InvPos InvNeg DCFilterModule
    
Xinverter InvPos InvNeg InvA InvB InvC InvCase InverterModule
    
Xaccmc InvA InvB InvC CMCA CMCB CMCC ACCommonModeChokeModule

* Strömmätning för faser i(VPhA) i(VPhB) i(VPhC)
VAC_A CMCA PhA 0
VAC_B CMCB PhB 0
VAC_C CMCC PhC 0
    
Xload PhA PhB PhC LoadCase LoadModule
    
XbatGnd   BatCase 0 BatteryGroundModule
XinvGnd   InvCase 0 InverterGroundModule
XloadGnd LoadCase 0 LoadGroundModule
    
.ic v(InvA)=0 v(InvB)=0 v(InvC)=0
.option method={simParams["method"]}


.options reltol=1e-3   ; > 1ms  "Never larger than 0.003!"
.options abstol=10e-9  ; > 10ns
.options itl4=30       ; > 30

.save i(VAC_A)
.save i(VAC_B)
.save i(VAC_C)
.save i(VDC_P)
.save i(VDC_N)

.save i(l.xinvgnd.l1)
.save i(l.xbatgnd.l1)
.save i(l.xloadgnd.l1)

.save v(batCase)
.save v(invCase)
.save v(loadCase)

.save v(CMCPos)
.save v(CMCNeg)
    
.tran {simParams["tstep"]} {simParams["tstop"]} {simParams["tstart"]}
.end"""

def saveBandEnergies(filename: str, energies: list):
    """ Sparar ned simuleringens parametrar till en JSON-fil, lägger till simuleringen om filen redan existerar """

    with open(filename, "w+") as file:  # Öppna/Skapa json fil
        try:
            file_data = json.load(file)  # Ladda in JSON-data som python object (list "[]" eller dict "{}")
        except json.JSONDecodeError:
            file_data = []  #  Om filen är tom, skapa en tom lista, i denna hamnar alla utförda simuleringar

        for i in range(len(energies)):
            file_data.append(energies[i])  # Lägg till en ny dict, som innehåller datan från simuleringen, i listan
        file.seek(0)  # Börja om filen från början så vi skriver över filen med den nya datan


        return json.dumps(file_data, default=np_encoder)


def saveAllBands(filename: str):
    [time0, data0] = readVariables(filename, "i(l.xload.l1)")
    [uniTime0, uniData0] = uniformResample(time0, data0, timeStep=10 ** (-9))
    N = len(uniTime0)
    fftcurrent = 2.0 / N * np.abs(fft(uniData0)[0, 0:N // 2])
    tf = fftfreq(N, uniTime0[1] - uniTime0[0])[0:N // 2]

    energy = energyInAllBands(tf, fftcurrent)

    return saveBandEnergies("C:\\EENX15\\Modular\\bandEnergies.json", energy)