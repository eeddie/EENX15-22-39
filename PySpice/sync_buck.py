#####################################################################

## Den här funkar inte alls, den hänger på att man ska kunna importera en nmos men det går verkligen inte
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

# Simulation params
tstep = 1 @u_ns
tfinal = 180 @u_us

# Component values
Lf = 1 @u_mH
Cf = 33 @u_uF
ESR_Cf = 0.25 @u_Ohm
Rload = 0.5 @u_Ohm
Rg = 0.25 @u_Ohm

# Control params
Vin = 12
Fsw = 10**6
Gain = 100
Duty = 0.28
step_delta = 0.001
Vgs = 15

if __name__ == '__main__':
    circuit = Circuit("Synchronous Buck Inverter")

    ## Main circuit
    new_line = ".include 'MOS.lib'"
    circuit.raw_spice += new_line + os.linesep
    print(circuit)
    contStepSource1(circuit, "in", "Vin", circuit.gnd, Vin, step_delta)
    circuit.M("sw1","Vin", "G1", "S1", "IXFH58N20")                      # "Switching MOSFET"
    circuit.M("sw2","S1", "G2", circuit.gnd, "IXFH58N20")                # Rectification MOSFET
    circuit.L("Lf", "S1", "out", Lf)                                        # Choke
    circuit.R("ESR", "out", "Vc", ESR_Cf)                                   # ESR of filtering capacitor
    circuit.C("Cf", "Vc", circuit.gnd, Cf)                                  # Filtering capacitor
    circuit.R("Rload", "out", circuit.gnd, Rload)                           # Load resistance

    ## Triangle wave
    circuit.BehavioralSource("Tri", "Triangle", circuit.gnd, v=f"0.5 + asin(sin(2*Pi*{Fsw}*time))/Pi")

    ## Control signal for M1
    circuit.BehavioralSource("E_PWMa", "PWMa", circuit.gnd, v=f"{Vgs}*tanh({Gain}*({Duty}-V(Triangle)))")

    ## Control signal for M2
    circuit.BehavioralSource("E_PWMb", "PWMb", circuit.gnd, v=f"{Vgs}*tanh({Gain}*(-({Duty}+0.03)+V(Triangle)))")

    ## Gate driver for M1, dependent voltage source
    circuit.BehavioralSource("Dr1", "GR1", "S1", v=f"V(PWMa)")
    circuit.R("Rg1", "GR1", "G1", Rg)

    ## Gate driver for M2, dependent voltage source
    circuit.BehavioralSource("Dr2", "GR2", circuit.gnd, v=f"V(PWMa)")
    circuit.R("Rg2", "GR2", "G2", Rg)

    print(circuit)

    ## Set up simulation
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    simulator.initial_condition(out = 0)
    analysis = simulator.transient(step_time=tstep, end_time=tfinal)
    y = np.array(analysis['out'])

    plt.figure(3)
    plt.title('Output voltage')
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')
    plt.grid()
    plot(analysis["out"],color='green', label="$\mathregular{V_out}}$")
    plt.legend()
    plt.show()
