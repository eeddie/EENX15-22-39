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
#   (Vin)┌─[Lin]─(a)─[Rin]─┬(b)─→[D1]→──┬──(out)─┐
#       +│               [Rsw]       [Rout]      │
#        O               (sw)          (c)    [Rload]
#       -│         (pwm)─[sw]        [Cout]      │
#        └─────────────────┴────────────┴────────┘
#         (circuit.gnd)


def buckConverter(
    inV     = 12,
    inL     = 10    @u_mH,
    inR     = 1     @u_Ohm,
    outC    = 220   @u_uF,
    outR    = 1     @u_Ohm,
    swR     = 1     @u_Ohm,
    loadR   = 1     @u_kOhm,
    pwmFreq = 10**3,
    pwmDutyCycle = 0.5,
    pwmAmp = 5,
    pwmOffset = -0.5
):
    """ Returns a PySpice Circuit buck-converter with the parameters specified """
    circuit = Circuit('Buck-converter')

    contStepSource(circuit, 'in', 'n_Vin', circuit.gnd, inV)

    contPWMSource(circuit, 'pwm', 'n_pwm', circuit.gnd, pwmFreq, pwmAmp, pwmDutyCycle, pwmOffset)

    circuit.L('in', 'n_Vin', 'n_a', inL)
    circuit.R('in', 'n_a', 'n_b', inR)

    circuit.R('sw', 'n_b', 'n_sw', swR)

    spice_library = SpiceLibrary("./libs/")
    # circuit.include(spice_library["S3_30_l_var"])
    # circuit.X('sw', "S3_30_l_var", 'n_sw', 'n_pwm', circuit.gnd, 25)  # Tj = 25, junction temperature is 25 degrees C

    circuit.subcircuit(SwitchSubCircuit('sub_sw'))
    circuit.X('sw', 'sub_sw', 'n_sw', circuit.gnd, 'n_pwm', circuit.gnd)

    circuit.include(spice_library["DI_1N4002G"])
    circuit.Diode(1, 'n_out', 'n_b', model="DI_1N4002G")

    circuit.R('out', 'n_out', 'n_c', outR)
    circuit.C('out', 'n_c', circuit.gnd, outC)

    circuit.R('load', 'n_out', circuit.gnd, loadR)

    return circuit



# Simuleringarnas tidssteg
step_time = 100 @u_us

# Simuleringarnas sluttid
final_time = 1000 @u_ms

from plotting import plotFourier, plotSet

if __name__ == '__main__':
    circuit = buckConverter()

    # simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    # analysis = simulator.transient(step_time=step_time, end_time=final_time)


    #Plot över utspänning
    plt.figure(1)
    plt.title('Output voltage')
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')
    plt.grid()
    plotSet(circuits=[
        [buckConverter(pwmDutyCycle=0.1), "D=0.1"],
        [buckConverter(pwmDutyCycle=0.5), "D=0.5"],
        [buckConverter(pwmDutyCycle=0.9), "D=0.9"]
        ],
        net="n_out",
        step_time=step_time,
        final_time=final_time
    )
    #plot(analysis['n_out'], label="$\mathregular{V_{out}}$")
    #plot(analysis['n_Vin'], label="$\mathregular{V_{in}}$")
    #plot(analysis['n_pwm'], label="$\mathregular{V_{pwm}}$")
    plt.legend()

    # plt.figure(2)
    # plotFourier(analysis['n_out'], step_time)
    # plt.xlim(0, 5000)
    # plt.grid()
    
    plt.show()
    
    

