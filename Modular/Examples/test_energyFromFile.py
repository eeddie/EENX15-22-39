import os
import sys
sys.path.append('./Modular/')
from Modules import *
from Functions import *
def test_energyFromFile():
    energies = energyFromFile("test.raw","i(vac_a)", "i(vac_b)", "i(vdc_p)")
    # [time, data] = readVariables("test.raw","i(vac_a)", "i(vac_b)", "i(vdc_p)")
    phaseEnergy = energies["i(vac_a)"]
    freq = [row[0] for row in phaseEnergy]
    value = [row[2]/row[3] for row in phaseEnergy]
    plt.plot(freq,value,'-', linewidth=1,alpha=0.5, label="i(phA) avg:d")

    phaseEnergy1 = energies["i(vdc_p)"]
    freq1 = [row[0] for row in phaseEnergy1]
    value1 = [row[2]/row[3] for row in phaseEnergy1]
    plt.plot(freq1,value1,'-', linewidth=1,alpha=0.5, label="i(dc_p) avg:d")
    plt.legend()
    plt.loglog()
    plt.grid()
    plt.show()

if __name__=="__main__":
    test_energyFromFile()