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
#
#    (Vbat)
#   ┌──────┬───────┬───────┐
#   │   [sw_a+] [sw_b+] [sw_c+]
#  +│      ├(a)──────────────────L─(aa)─R─┐
#   O      │       ├(b)──────────L─(bb)─R─┤(abc)
#  -│      │       │       ├(c)──L─(cc)─R─┘
#   │   [sw_a-] [sw_b-] [sw_c-]
#   └──────┴───────┴───────┘
#    (circuit.gnd)



def trefas(
    phaseFreq = 50 @u_Hz,                  # Huvudsakliga frekvensen i trefassteget
    triangleFreq = 450,                     # Triangelvågens frekvens i Hz
    triangleAmplitude = 1,                  # Triangelvågens amplitud
    sinAmplitude = 700 @u_mV,              # Sinussignalernas amplitud
    batteryVoltage = 1400,                  # Batterispänning Vbat = batteryVoltage * tanh(batteryGain * time). Enheter (ex. @ u_V) fungerar inte när man insertar i ett expression
    phaseResistance = 1 @u_Ohm,            # Fasresistans "motor"
    phaseInductance = 1 @u_mH              # Fasinduktans "motor"
):
    """ Konstruerar en trefas-krets med de givna parametrarna och returnar den """

    phaseDelay = (1 / phaseFreq) / 3 @ u_s # Fördröjningen mellan faserna (0°, 120°, 240°) i sekunder

    circuit = Circuit('Tre-fas inverter')

    # Spänningskälla batteri
    contStepSource(circuit, "1", 'Vbat', circuit.gnd, batteryVoltage)

    # Triangelvåg
    contTriangleSource(circuit, 'triangle_wave', 'check', circuit.gnd, frequency=triangleFreq, amplitude=triangleAmplitude)
    circuit.R('R', 'check', circuit.gnd, 1 @ u_kOhm)

    # Sinussignaler för faser
    circuit.SinusoidalVoltageSource('sin_a', 'a_a', circuit.gnd, amplitude=sinAmplitude, frequency=phaseFreq)
    circuit.SinusoidalVoltageSource('sin_b', 'b_b', circuit.gnd, amplitude=sinAmplitude, frequency=phaseFreq,
                                    delay=phaseDelay)
    circuit.SinusoidalVoltageSource('sin_c', 'c_c', circuit.gnd, amplitude=sinAmplitude, frequency=phaseFreq,
                                    delay=2 * phaseDelay)
    circuit.R('Rb', 'a_a', circuit.gnd, 10 @ u_Ohm)
    circuit.R('Rc', 'b_b', circuit.gnd, 10 @ u_Ohm)
    circuit.R('Rd', 'c_c', circuit.gnd, 10 @ u_Ohm)

    # Komparatorer (sin > tri)
    circuit.subcircuit(ContGreaterThanSubCircuit('sub_greaterThan', 1))
    circuit.X('gt_a', 'sub_greaterThan', 'a_a', 'check', 'control_a', circuit.gnd)
    circuit.X('gt_b', 'sub_greaterThan', 'b_b', 'check', 'control_b', circuit.gnd)
    circuit.X('gt_c', 'sub_greaterThan', 'c_c', 'check', 'control_c', circuit.gnd)


    # Fas-switchar

    # IGBT:er importerade från Infineon. Ersätter switcharna längre ned, kräver annan gate-spänning (5V). Ger error just nu.
    spice_library = SpiceLibrary('./libs/')
    circuit.include(spice_library["IKW40N65H5A_L2"])
    
    # circuit.X('sw_a+', 'IKW40N65H5A_L2', 'Vbat', 'control_a', 'a')
    # circuit.X('sw_b+', 'IKW40N65H5A_L2', 'Vbat', 'control_b', 'b')
    # circuit.X('sw_c+', 'IKW40N65H5A_L2', 'Vbat', 'control_c', 'c')

    # circuit.X('sw_a-', 'IKW40N65H5A_L2', 'a', 'control_a', circuit.gnd)
    # circuit.X('sw_b-', 'IKW40N65H5A_L2', 'b', 'control_b', circuit.gnd)
    # circuit.X('sw_c-', 'IKW40N65H5A_L2', 'c', 'control_c', circuit.gnd)

    circuit.subcircuit(SwitchSubCircuit('sub_switch'))
    circuit.X('sw_a+', 'sub_switch', 'Vbat', 'a', 'control_a', circuit.gnd)
    circuit.X('sw_b+', 'sub_switch', 'Vbat', 'b', 'control_b', circuit.gnd)
    circuit.X('sw_c+', 'sub_switch', 'Vbat', 'c', 'control_c', circuit.gnd)

    circuit.X('sw_a-', 'sub_switch', 'a', circuit.gnd, circuit.gnd, 'control_a')
    circuit.X('sw_b-', 'sub_switch', 'b', circuit.gnd, circuit.gnd, 'control_b')
    circuit.X('sw_c-', 'sub_switch', 'c', circuit.gnd, circuit.gnd, 'control_c')

    # Fasfilter "motor"
    circuit.L(1, 'a', 'aa', phaseInductance)
    circuit.R(1, 'aa', 'abc', phaseResistance)

    circuit.L(2, 'b', 'bb', phaseInductance)
    circuit.R(2, 'bb', 'abc', phaseResistance)

    circuit.L(3, 'c', 'cc', phaseInductance)
    circuit.R(3, 'cc', 'abc', phaseResistance)

    return circuit





# Simuleringarnas tidssteg
step_time = 1 @ u_us
# Simuleringarnas sluttid
final_time = 100 @ u_ms

# Fasresistansen som vi använder både i kretsen,, men också i simuleringen
phaseResistance = 1 @u_Ohm

if __name__ == '__main__':

    circuit = trefas(phaseResistance = phaseResistance)

    # SIMULERING
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    simulator.initial_condition(abc=0 @ u_V)

    analysis = simulator.transient(step_time=step_time, end_time=final_time)
    

    # PLOTTING
    #
    #    (Vbat)
    #   ┌──────┬───────┬───────┐
    #   │   [sw_a+] [sw_b+] [sw_c+]
    #  +│      ├(a)──────────────────L─(aa)─R─┐
    #   O      │       ├(b)──────────L─(bb)─R─┤(abc)
    #  -│      │       │       ├(c)──L─(cc)─R─┘
    #   │   [sw_a-] [sw_b-] [sw_c-]
    #   └──────┴───────┴───────┘
    #    (circuit.gnd)
    #
    #   Ex.
    #   plot(analysis['a'])
    #       för att plotta spänningen i nät (a)
    #
    #   plot((analysis['abc'] - analysis['aa']) / resistance)
    #       för att plotta strömmen genom R mellan (aa) och (abc)
    #

    # Plot över strömmarna genom de tre faserna, inkl dess summa (svart). Summan ska alltid vara noll, annars är något fel.
    plt.figure(3)
    plt.title('Phase currents')
    plt.xlabel('Time [s]')
    plt.ylabel('Current [A]')
    plt.grid()
    plot((analysis['abc'] - analysis['aa']) / phaseResistance, color='red', label="$\mathregular{I_a}$")
    plot((analysis['abc'] - analysis['bb']) / phaseResistance, color='blue', label="$\mathregular{I_b}$")
    plot((analysis['abc'] - analysis['cc']) / phaseResistance, color='green', label="$\mathregular{I_c}$")
    plot((analysis['abc'] + analysis['abc'] + analysis['abc'] - analysis['aa'] - analysis['bb'] - analysis[
        'cc']) / phaseResistance, color='black', label="$\mathregular{I_a+I_b+I_c}$")
    plt.legend()

    # Fourieranalys av strömmen genom fas a
    from scipy.fft import fft, fftfreq

    # Välj datan att analysera
    y = np.array((analysis['abc'] - analysis['aa']) / phaseResistance)

    ## Kod som behövs för fourier analysen
    # Number of sample points
    N = len(y)
    # sample spacing
    T = float(step_time)
    x = np.linspace(0.0, N * T, N, endpoint=False)
    yf = fft(y)
    xf = fftfreq(N, T)[:N // 2]
    ##

    # plotta fourier transformen i fig 1
    plt.figure(1)
    plt.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
    # avgränsa x-axeln
    plt.xlim(0, 5000)
    plt.grid()
    plt.show()
