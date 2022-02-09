#####################################################################
import os

import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import numpy as np

import PySpice.Logging.Logging as Logging

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

from components import *

logger = Logging.setup_logging()
#####################################################################
#
#   Kretsschema
#   (nät) [komponent]
#    
#   (Vin)┌─[sw]─(a)─┬───←[D1]←──┬──(out)─┐
#       +│   │     [R1]         │        │
#        O (pwm)   (b)         [C1]   [Rload]
#       -│         [L1]         │        │
#        └──────────┴───────────┴────────┘
#         (circuit.gnd)

# VARIABLER

# Simuleringarnas tidssteg
step_time = 10 @u_us
# Simuleringarnas sluttid
final_time = 10 @u_ms

# Fyrkantsvågens parametrar
pwmFreq = 10**4
pwmDutyCycle = 0.9
pwmAmplitude = 7

# Likspänningen Vin = batteryVoltage * tanh(batteryGain * time)
# Enheter (ex. @ u_V) fungerar inte när man insertar i ett expression
batteryVoltage = 12

indR = 220 @ u_Ohm
inL = 1 @ u_uH
outC = 22 @u_uF
loadR = 1000 @u_Ohm





if __name__ == '__main__':
    circuit = Circuit('Buck-boost converter')
    spice_library = SpiceLibrary("./libs/")

    # Spänningskälla
    contStepSource(circuit, "in", 'Vin', circuit.gnd, batteryVoltage)

    # Switch PWM
    contPWMSource(circuit, 'pwm', 'pwm', circuit.gnd, pwmFreq, amplitude=pwmAmplitude, dutyCycle=pwmDutyCycle, offset=-pwmAmplitude/2)
    
    #circuit.subcircuit(SwitchSubCircuit('sub_switch'))
    #circuit.X('sw', 'sub_switch', 'Vin', 'a', 'pwm', circuit.gnd)

    # Denna ger upphov till "Timestep too small"
    circuit.include(spice_library["IKW40N65H5A_L2"])
    circuit.X('sw', 'IKW40N65H5A_L2', 'Vin', 'pwm', 'a')

    circuit.R(1, 'a', 'b', indR)
    circuit.L(1, 'b', circuit.gnd, inL)
    
    circuit.C(1, 'out', circuit.gnd, outC)
    circuit.R('load', 'out', circuit.gnd, loadR)
    
    circuit.include(spice_library["DI_1N4002G"])
    circuit.Diode('D', 'a', 'out', model="DI_1N4002G")

    # SIMULERING
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    simulator.initial_condition(a=0 @ u_V)

    analysis = simulator.transient(step_time=step_time, end_time=final_time)

    # PLOTTING
    #
    #   (Vin)┌─[sw]─(a)─┬───←[D1]←──┬──(out)─┐
    #       +│   │     [R1]         │        │
    #        O (pwm)   (b)         [C1]   [Rload]
    #       -│         [L1]         │        │
    #        └──────────┴───────────┴────────┘
    #         (circuit.gnd)
    #   Ex.
    #   plot(analysis['a'])
    #       för att plotta spänningen i nät (a)
    #
    #   plot((analysis['abc'] - analysis['aa']) / resistance)
    #       för att plotta strömmen genom R mellan (aa) och (abc)
    #

    # Plot över utspänning
    plt.figure(1)
    plt.title('Output voltage')
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')
    plt.grid()
    plot(analysis['out'], label="$\mathregular{V_{out}}$")
    plot(analysis['Vin'], label="$\mathregular{V_{in}}$")
    #plot(analysis['pwm'], label="$\mathregular{V_{pwm}}$")
    plt.legend()
    plt.show()

    # Fourieranalys av strömmen genom fas a
    #from scipy.fft import fft, fftfreq

    # Välj datan att analysera
    #y = np.array((analysis['abc'] - analysis['aa']) / phaseResistance)

    ## Kod som behövs för fourier analysen
    # Number of sample points
    #N = len(y)
    # sample spacing
    #T = float(step_time)
    #x = np.linspace(0.0, N * T, N, endpoint=False)
    #yf = fft(y)
    #xf = fftfreq(N, T)[:N // 2]
    ##

    # plotta fourier transformen i fig 1
    #plt.figure(1)
    #plt.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
    # avgränsa x-axeln
    #plt.xlim(0, 5000)
    #plt.grid()
    #plt.show()
