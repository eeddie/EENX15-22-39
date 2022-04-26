#
# Plot_TransistorTester_Drivlina.py
#
# Skapar fyra plots som används i rapporten för transistortesterna i drivlinan
# Kräver tre färdiga drivline-simuleringar: "Strömbrytare.raw", "Inbyggd MOSFET.raw", "Subcircuit MOSFET.raw"
# 


import sys
sys.path.append('./Modular/')
from Modules import *
from Functions import *
from scipy.fftpack import fft, fftfreq

linewidth = 3

def test_energyFromFile(*filenames: str):

    plt.figure(1)
    plt.title("Ström fas A")
    plt.figure(2)
    plt.title("Batteriström")

    for filename in filenames:
        energies = energyFromFile(filename,"i(vac_a)", "i(vac_b)", "i(vdc_p)")
        
        phaseEnergy = energies["i(vac_a)"]
        freq = [row[0] for row in phaseEnergy]
        value = [row[2]/row[3] for row in phaseEnergy]
        
        plt.figure(1)
        plt.plot(freq,value,'-', linewidth=linewidth,alpha=0.5, label=filename.removesuffix(".raw"))

        phaseEnergy1 = energies["i(vdc_p)"]
        freq1 = [row[0] for row in phaseEnergy1]
        value1 = [row[2]/row[3] for row in phaseEnergy1]

        plt.figure(2)
        plt.plot(freq1,value1,'-', linewidth=linewidth,alpha=0.5, label=filename.removesuffix(".raw"))
    
    plt.figure(1)
    plt.legend()
    plt.loglog()
    plt.grid()

    plt.figure(2)
    plt.legend()
    plt.loglog()
    plt.grid()

if __name__=="__main__":
    plt.rcParams.update({'font.size': 28})
    test_energyFromFile("Strömbrytare.raw", "Inb. MOSFET.raw", "Sub. MOSFET.raw")
    
    plt.figure(3)
    # Increase the font size

    # Read the variable 'i(dc_P)' from switch.raw
    time, (vac_a, vdc_p) = readVariables("Strömbrytare.raw", "i(vac_a)", "i(vdc_p)")

    energies = energyFromFile("Strömbrytare.raw", "i(vac_a)", "i(vdc_p)")
        
    phaseEnergy = energies["i(vac_a)"]
    freq = [row[0] for row in phaseEnergy]
    value = [row[2]/row[3] for row in phaseEnergy]
    
    plt.figure(3)

    # Number of sample points
    N = len(time)
    # sample spacing
    T = time[1] - time[0]
    xf = fftfreq(N, T)
    xf = xf[:int(N/2)]
    yf = fft(vac_a)
    yf = yf[:int(N/2)]
    plt.plot(xf, 2.0/N * np.abs(yf), '-', linewidth=linewidth,alpha=0.5, label="Obehandlad FFT")

    plt.plot(freq,value,'-', linewidth=linewidth,alpha=0.5, label="Frekvensbandsindelad FFT")
    plt.title("Frekvensanalys av ström genom fas A")
    plt.legend()
    plt.loglog()
    plt.grid()

    phaseEnergy = energies["i(vdc_p)"]
    freq1 = [row[0] for row in phaseEnergy]
    value1 = [row[2]/row[3] for row in phaseEnergy]

    plt.figure(4)

    # Number of sample points
    N = len(time)
    # sample spacing
    T = time[1] - time[0]
    xf = fftfreq(N, T)
    xf = xf[:int(N/2)]
    yf = fft(vdc_p)
    yf = yf[:int(N/2)]
    plt.plot(xf, 2.0/N * np.abs(yf), '-', linewidth=linewidth,alpha=0.5, label="Obehandlad FFT")


    plt.plot(freq1,value1,'-', linewidth=linewidth,alpha=0.5, label="Frekvensbandsindelad FFT")
    plt.title("Frekvensanalys av ström från batteri")
    plt.legend()
    plt.loglog()
    plt.grid()

    plt.show()



