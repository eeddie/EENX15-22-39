#####################################################################
import os

import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import numpy as np

import PySpice.Logging.Logging as Logging
from scipy.constants import pico

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit, SubCircuit, SubCircuitFactory
from PySpice.Unit import *

logger = Logging.setup_logging()
#####################################################################
#
#   Kretsschema
#
#    (Vbat)
#   ┌───┬───┬───┐
#   │   Q   Q   Q
#  +│   ├(a)──────────L─(aa)─R─┐
#   O   │   ├(b)──────L─(bb)─R─┤(abc)
#  -│   │   │   ├(c)──L─(cc)─R─┘
#   │   Q   Q   Q
#   └───┴───┴───┘
#    (circuit.gnd)

# VARIABLER

# Simuleringarnas tidssteg
step_time = 1 @ u_us
# Simuleringarnas sluttid
final_time = 100 @ u_ms

# Huvudsakliga frekvensen i trefassteget
phaseFreq = 50 @ u_Hz
# Fördröjningen mellan faserna (0°, 120°, 240°) i sekunder
phaseDelay = (1 / phaseFreq) / 3 @ u_s

# Triangelvågens frekvens i GHz
triangleFreq = 450
# Triangelvågens amplitud
triangleAmplitude = 1

# Sinussignalernas amplitud
sinAmplitude = 700 @ u_mV

# Batterispänning
batteryVoltage = 1400 @ u_V

# Fasfilter "motor"
phaseResistance = 1 @ u_Ohm
phaseInductance = 1 @ u_mH


# KRETS
class SwitchSubCircuit(SubCircuit):
    __nodes__ = ('t_in', 't_out', 't_c+', 't_c-')

    def __init__(self, name):
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.raw_spice = '.Model DMOD D' + os.linesep
        self.model('switch', 'SW', Ron=1 @ u_mOhm, Roff=1 @ u_GOhm)

        self.D(1, 't_out', 't_in', model='DMOD')
        self.S(1, 't_in', 't_out', 't_c+', 't_c-', model='switch')

# if (a > b) {out = 1 V} else {out = -1 V}
class GreaterThanSubCircuit(SubCircuit):
    __nodes__ = ('a', 'b', 'out', 'gnd')

    def __init__(self, name):
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.NonLinearVoltageSource('comparator', 'out', 'gnd',
                                   expression='V(a, b)',
                                   table=((-1 @ u_nV, -1 @ u_V),
                                          (1 @ u_nV, 1 @ u_V)))
        self.R('parallel_R', 'out', 'gnd', 1 @ u_kOhm)


def triangle_wave_pulse(circ, name, in_node, out_node, frequency, amplitude):
    period = int(1 / frequency * 10**9) @u_ns
    circ.PulseVoltageSource(name, in_node, out_node, initial_value=-(amplitude), pulsed_value=(amplitude) @ u_V,
                            pulse_width=1 @ u_ns,
                            period=period, delay_time=0 @ u_ms, rise_time=period / 2, fall_time=period / 2)


if __name__ == '__main__':
    circuit = Circuit('Subfactories')

    # Spänningskälla batteri
    circuit.V(1, 'Vbat', circuit.gnd, batteryVoltage)

    # Triangelvåg
    circuit.raw_spice = '.MODEL ramp1 triangle(cntl_array = [-1 0 5 6] freq_array=[10 10 1000 1000] out_low = -5.0 out_high = 5.0 duty_cycle = 0.9)'
    triangle_wave_pulse(circuit, 'pwl1', 'check', circuit.gnd, frequency=triangleFreq, amplitude=triangleAmplitude)
    circuit.R('R', 'check', circuit.gnd, 1 @ u_kOhm)

    # Sinussignaler för faser
    circuit.SinusoidalVoltageSource('sin_a', 'a_a', circuit.gnd, amplitude=sinAmplitude, frequency=phaseFreq)
    circuit.SinusoidalVoltageSource('sin_b', 'b_b', circuit.gnd, amplitude=sinAmplitude, frequency=phaseFreq, delay=phaseDelay)
    circuit.SinusoidalVoltageSource('sin_c', 'c_c', circuit.gnd, amplitude=sinAmplitude, frequency=phaseFreq, delay=2 * phaseDelay)
    circuit.R('Rb', 'a_a', circuit.gnd, 10 @ u_Ohm)
    circuit.R('Rc', 'b_b', circuit.gnd, 10 @ u_Ohm)
    circuit.R('Rd', 'c_c', circuit.gnd, 10 @ u_Ohm)

    # Komparatorer (sin > tri)
    circuit.subcircuit(GreaterThanSubCircuit('sub_greaterThan'))
    circuit.X('gt_a', 'sub_greaterThan', 'a_a', 'check', 'control_a', circuit.gnd)
    circuit.X('gt_b', 'sub_greaterThan', 'b_b', 'check', 'control_b', circuit.gnd)
    circuit.X('gt_c', 'sub_greaterThan', 'c_c', 'check', 'control_c', circuit.gnd)

    # Fas-switchar
    circuit.subcircuit(SwitchSubCircuit('sub_switch'))
    circuit.X('sw_a+', 'sub_switch', 'Vbat', 'a', 'control_a', circuit.gnd)
    circuit.X('sw_b+', 'sub_switch', 'Vbat', 'b', 'control_b', circuit.gnd)
    circuit.X('sw_c+', 'sub_switch', 'Vbat', 'c', 'control_c', circuit.gnd)

    circuit.X('sw_a-', 'sub_switch', 'a', circuit.gnd, circuit.gnd, 'control_a')
    circuit.X('sw_b-', 'sub_switch', 'b', circuit.gnd, circuit.gnd, 'control_b')
    circuit.X('sw_c-', 'sub_switch', 'c', circuit.gnd, circuit.gnd, 'control_c')

    # Fasfilter "motor"
    circuit.R(1, 'aa', 'abc', phaseResistance)
    circuit.L(1, 'a', 'aa', phaseInductance)

    circuit.R(2, 'bb', 'abc', phaseResistance)
    circuit.L(2, 'b', 'bb', phaseInductance)

    circuit.R(3, 'cc', 'abc', phaseResistance)
    circuit.L(3, 'c', 'cc', phaseInductance)


    # SIMULERING
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    simulator.initial_condition(abc= 0 @ u_V )
    analysis = simulator.transient(step_time=step_time, end_time=final_time)


    # PLOTTING
    #
    #    (Vbat)
    #   ┌───┬───┬───┐
    #   │   Q   Q   Q
    #  +│   ├(a)──────────L─(aa)─R─┐
    #   O   │   ├(b)──────L─(bb)─R─┤(abc)
    #  -│   │   │   ├(c)──L─(cc)─R─┘
    #   │   Q   Q   Q
    #   └───┴───┴───┘
    #    (circuit.gnd)
    #
    #   Ex. 
    #   plot(analysis['a']) 
    #       för att plotta spänningen i nät (a)
    #
    #   plot((analysis['abc'] - analysis['aa']) / resistance
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
    plot((analysis['abc'] + analysis['abc'] + analysis['abc'] - analysis['aa'] - analysis['bb'] - analysis['cc']) / phaseResistance, color='black', label="$\mathregular{I_a+I_b+I_c}$")
    plt.legend()


    # Fourieranalys av strömmen genom fas a
    from scipy.fft import fft, fftfreq

    # Number of sample points
    y = np.array((analysis['abc'] - analysis['aa']) / phaseResistance)

    N = len(y)
    # sample spacing
    T = 1.0 / 1000000.0
    x = np.linspace(0.0, N * T, N, endpoint=False)
    yf = fft(y)
    xf = fftfreq(N, T)[:N // 2]
    plt.figure(1)

    plt.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))
    plt.xlim(0, 5000)
    plt.grid()
    plt.show()
