#####################################################################
# STANDARD DECLARATIONS
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

import math

logger = Logging.setup_logging()


#####################################################################
class MySubCir(SubCircuit):
    __nodes__ = ('t_in', 't_out', 't_c+', 't_c-')

    def __init__(self, name):
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.raw_spice = '.Model DMOD D' + os.linesep
        self.model('switch', 'SW', Ron=1 @ u_mOhm, Roff=1 @ u_GOhm)

        self.D(1, 't_out', 't_in', model='DMOD')
        self.S(1, 't_in', 't_out', 't_c+', 't_c-', model='switch')


def triangle_wave_pulse(circ, name, in_node, out_node, frequency, amplitude):
    freq = 1 / frequency * 1000 * 1000 * 1000
    fr = int(freq) @ u_ns
    circ.PulseVoltageSource(name, in_node, out_node, initial_value=-(amplitude), pulsed_value=(amplitude) @ u_V,
                            pulse_width=1 @ u_ns,
                            period=fr, delay_time=0 @ u_ms, rise_time=fr / 2, fall_time=fr / 2)


if __name__ == '__main__':
    circuit = Circuit('Subfactories')

    step_time = 1 @ u_us
    final_time = 100 @ u_ms

    circuit.raw_spice = '.MODEL ramp1 triangle(cntl_array = [-1 0 5 6] freq_array=[10 10 1000 1000] out_low = -5.0 out_high = 5.0 duty_cycle = 0.9)'

    triangle_wave_pulse(circuit, 'pwl1', 'check', circuit.gnd, frequency=450, amplitude=1)
    circuit.R('R', 'check', circuit.gnd, 1 @ u_kOhm)

    freq = 50 @ u_Hz
    delay = int(1000 * ((1 / 50) / 3)) @ u_ms

    circuit.SinusoidalVoltageSource('sin_a', 'a_a', circuit.gnd, amplitude=700 @ u_mV, frequency=freq)
    circuit.SinusoidalVoltageSource('sin_b', 'b_b', circuit.gnd, amplitude=700 @ u_mV, frequency=freq, delay=delay)
    circuit.SinusoidalVoltageSource('sin_c', 'c_c', circuit.gnd, amplitude=700 @ u_mV, frequency=freq, delay=2 * delay)
    circuit.R('Rb', 'a_a', circuit.gnd, 10 @ u_Ohm)
    circuit.R('Rc', 'b_b', circuit.gnd, 10 @ u_Ohm)
    circuit.R('Rd', 'c_c', circuit.gnd, 10 @ u_Ohm)

    circuit.NonLinearVoltageSource('first_comparator', 'control_1', circuit.gnd,
                                   expression='V(a_a, check)',
                                   table=((-1 @ u_nV, -1 @ u_V),
                                          (1 @ u_nV, 1 @ u_V)))
    circuit.R('first_R', 'control_1', circuit.gnd, 1 @ u_kOhm)
    circuit.NonLinearVoltageSource('second_comparator', 'control_2', circuit.gnd,
                                   expression='V(b_b, check)',
                                   table=((-1 @ u_nV, -1 @ u_V),
                                          (1 @ u_nV, 1 @ u_V)))
    circuit.R('second_R', 'control_2', circuit.gnd, 1 @ u_kOhm)
    circuit.NonLinearVoltageSource('third_comparator', 'control_3', circuit.gnd,
                                   expression='V(c_c, check)',
                                   table=((-1 @ u_nV, -1 @ u_V),
                                          (1 @ u_nV, 1 @ u_V)))
    circuit.R('third_R', 'control_3', circuit.gnd, 1 @ u_kOhm)

    circuit.V(1, 1, circuit.gnd, 1400 @ u_V)

    circuit.subcircuit(MySubCir('sub_1'))
    circuit.X(1, 'sub_1', 1, 'a', 'control_1', circuit.gnd)
    circuit.subcircuit(MySubCir('sub_2'))
    circuit.X(2, 'sub_2', 1, 'b', 'control_2', circuit.gnd)
    circuit.subcircuit(MySubCir('sub_3'))
    circuit.X(3, 'sub_3', 1, 'c', 'control_3', circuit.gnd)

    circuit.subcircuit(MySubCir('sub_4'))
    circuit.X(4, 'sub_4', 'a', circuit.gnd, circuit.gnd, 'control_1')
    circuit.subcircuit(MySubCir('sub_5'))
    circuit.X(5, 'sub_5', 'b', circuit.gnd, circuit.gnd, 'control_2')
    circuit.subcircuit(MySubCir('sub_6'))
    circuit.X(6, 'sub_6', 'c', circuit.gnd, circuit.gnd, 'control_3')

    resistance = 1 @ u_Ohm
    inductance = 1 @ u_mH

    circuit.R(1, 'aa', 'abc', resistance)
    circuit.L(1, 'a', 'aa', inductance)
    circuit.R(2, 'bb', 'abc', resistance)
    circuit.L(2, 'b', 'bb', inductance)
    circuit.R(3, 'cc', 'abc', resistance)
    circuit.L(3, 'c', 'cc', inductance)

    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    ic = 0 @ u_V
    simulator.initial_condition(abc=ic)
    analysis = simulator.transient(step_time=step_time, end_time=final_time)

    plt.figure(2)
    plt.title('Voltage across Capacitor')
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')
    plt.grid()
    plot((analysis['abc'] - analysis['aa']) / resistance, color='black')

    from scipy.fft import fft, fftfreq

    # Number of sample points
    y = np.array((analysis['abc'] - analysis['aa']) / resistance)

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
