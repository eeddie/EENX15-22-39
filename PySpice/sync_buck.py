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
# Lf = 1 @u_mH
#Cf = 33 @u_uF
#ESR_Cf = 0.25 @u_Ohm
#Rload = 0.5 @u_Ohm
#Rg = 0.25 @u_Ohm

# Control params
#Vin = 12
#Fsw = 10**6
#Gain = 100
#Duty = 0.28
#step_delta = 0.001
#Vgs = 15

if __name__ == '__main__':
    circuit = Circuit("Synchronous Buck Inverter")

    ## Main circuit
    circuit.raw_spice += """Vin N001 0 PULSE(0 12 0 20us)
M1 N001 G1 E1 BSB012N03LX3
L1 E1 Out 1u
R1 Out Cin 0.25
C1 Cin 0 33u
R2 Out 0 0.5
BTri Triangle 0 V=0.5 + asin(sin(2*Pi*Fsw*Time))/Pi
BE_PWMa N003 0 V=15*tanh(Gain*(Duty-V(Triangle)))
BE_PWMb N004 0 V=15*tanh(Gain*(-(Duty+0.03)+V(Triangle)))
EDr1 N002 E1 N003 0 1
EDr2 N005 0 N004 0 1
Rg1 N002 G1 0.25
Rg2 N005 G2 0.25
M2 E1 G2 0 0 BSB012N03LX3
.model NMOS NMOS
.model PMOS PMOS
.inc C:\\Users\\ed_th\\OneDrive\\Dokument\\LTspiceXVII\\lib\\cmp\\standard.mos
.ic V(Out)=0
.param Duty = 0.28
.param Gain = 100
.param Fsw= 1.0Meg"""
    ## Set up simulation
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    print(simulator)
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
