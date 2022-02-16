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
#   (nVin)┌─[Xa]──┬─(n1)──[L1]─┬(nout)─┐
#        +│       │            │       │
#         O      [Xb]        [Cout] [Rload]
#        -│       │            │       │
#         └───────┴────────────┴───────┘
#          (circuit.gnd)


def buckConverter(
    inV     = 12,
    inL     = 1     @u_mH,   # Spolens induktans
    outC    = 33    @u_uF,   # Utgångskondensatorns kapacitans
    gateR   = 0.25  @u_Ohm,  # Switcharnas/transistorernas gate-resistans
    loadR   = 0.5   @u_Ohm,  # Lastens resistans
    pwmFreq = 10**4,
    pwmDutyCycle = 0.5,
    pwmAmp = 5,
    pwmOffset = 0
):
    """ Returns a PySpice Circuit buck-converter with the parameters specified """
    
    spice_library = SpiceLibrary("./libs/")

    circuit = Circuit('Buck-converter')

    contStepSource(circuit, 'in', 'nVin', circuit.gnd, inV, smoothness=0.01)

    contTriangleSource(circuit, "tri", 'nTri', circuit.gnd, pwmFreq, 0.5, 0.5, smoothness=0.001)

    # PWM-källor
    circuit.BehavioralSource('pwm_a', 'npwm_a', circuit.gnd, v=f"{pwmOffset} + {pwmAmp} * tanh(10 * ({pwmDutyCycle} - V(nTri)))")
    circuit.BehavioralSource('pwm_b', 'npwm_b', circuit.gnd, v=f"{pwmOffset} + {pwmAmp} * tanh(10 * (-{pwmDutyCycle}+0.03 + V(nTri)))")

    # MOSFET-Transistorer
    # circuit.include(spice_library["BSB012N03LX3"])
    # circuit.X('a', "BSB012N03LX3", 'nVin', 'nGateA', 'n1', 25, 25)
    # circuit.X('b', "BSB012N03LX3", 'n1', 'nGateB', circuit.gnd, 25, 25)

    # Ideella switchar
    circuit.subcircuit(SwitchSubCircuit('sub_switch'))
    circuit.X('a', 'sub_switch', 'nVin', 'n1', 'nGateA', circuit.gnd)
    circuit.X('b', 'sub_switch', 'n1', circuit.gnd, 'nGateB', circuit.gnd)

    # Gate-resistorer
    circuit.R('gateA', 'npwm_a', 'nGateA', gateR)
    circuit.R('gateB', 'npwm_b', 'nGateB', gateR)

    # Induktor
    circuit.L(1, 'n1', 'nout', inL)

    # Spänningsutjämnande utgångs-kondensator
    circuit.C('out', 'nout', circuit.gnd, outC)

    # Last
    circuit.R('load', 'nout', circuit.gnd, loadR)

    return circuit



# Simuleringarnas tidssteg
step_time = 1 @u_us

# Simuleringarnas sluttid
final_time = 20 @u_ms

if __name__ == '__main__':

    plt.figure(1)
    plt.title(f'D = 0.5')
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')
    plt.grid()
    circuit = buckConverter(pwmDutyCycle=0.5)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.transient(step_time=step_time, end_time=final_time)
    plt.plot((analysis["npwm_a"]), label="$\mathregular{V_{pwm,a}}$")
    plt.plot((analysis["npwm_b"]), label="$\mathregular{V_{pwm,b}}$")
    plt.plot((analysis["nVin"]-analysis["n1"]), label="$\mathregular{V_{Qa}}$")
    plt.plot((analysis["n1"]), label="$\mathregular{V_{Qb}}$")
    plt.legend()

    plt.figure(2)
    for fig, dc in [[2, 0.1], [3, 0.5], [4, 0.9]]:
        #plt.title(f'D = {dc}')
        plt.xlabel('Time [s]')
        plt.ylabel('Voltage [V]')
        plt.grid()
        circuit = buckConverter(pwmDutyCycle=dc)
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=step_time, end_time=final_time)
        if fig == 2: plt.plot((analysis["nVin"]), label="$\mathregular{V_{in}}$")
        plt.plot((analysis["nout"]), label=f"$\mathregular{{V_{{out,{dc}}}}}$")
        plt.legend()
    
    
    
    # plt.figure(2)
    # plotFourier(analysis['n_out'], step_time)
    # plt.xlim(0, 5000)
    # plt.grid()
    
    plt.show()
    
    

