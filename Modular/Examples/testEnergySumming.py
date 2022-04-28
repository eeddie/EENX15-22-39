import os
import sys
sys.path.append('./Modular/')
from Modules import *
from Functions import *
def test_energyInAllBands():
    [time0,data0] = readVariables("out.raw","i(l.xload.l1)")
    [uniTime0,uniData0] = uniformResample(time0,data0,timeStep=10**(-9))
    N = len(uniTime0)
    fftcurrent = 2.0/N * np.abs(fft(uniData0)[0,0:N//2])
    tf = fftfreq(N, uniTime0[1]-uniTime0[0])[0:N//2]

    energy = energyInAllBands(tf, fftcurrent)
    plt.figure(4)
    freq = [row[0] for row in energy]
    value = [row[2]/row[3] for row in energy]
    plt.plot(tf, fftcurrent, "-", linewidth=1, alpha=0.5, label=f"i(L1)")
    plt.plot(freq,value, '-', linewidth=1,alpha=0.5, label="i(L1) avg:d")
    plt.legend()
    plt.loglog()
    plt.grid()
    plt.show()

if __name__=="__main__":
    test_energyInAllBands()