#
#   Samling funktioner användbara för PySpice
#

import os

from PySpice.Spice.Netlist import SubCircuit
from PySpice.Unit import *

from math import pi,atan,acos


# Kontinuerliga spänningskällor
# Desmos: https://www.desmos.com/calculator/578tvcfhoz
# Källa: https://mathematica.stackexchange.com/questions/38293/make-a-differentiable-smooth-sawtooth-waveform

# tri = 1 - 2 ArcCos[(1 - δ) Sin[2 π x]]/π;
def contTriangleSource(circuit, name, in_node, out_node, frequency, amplitude, offset=0, smoothness = 0.001):
    """
    Lägger till en kontinuerlig triangelvågskälla till circuit som går från -amplitude till +amplitude

    smoothness - ändrar den kontinuerliga triangelvågens skarphet. 0 ger perfekt (diskont.?) triangelvåg, 0.1 och högre ger sinusvåg.
    """

    # factor ser till att signalens amplitud är 'amplitude' oavsett smoothness
    factor = 1 / float((1-(2/pi)*acos(1-smoothness)))
    period = 1 / float(frequency)
    circuit.BehavioralSource(name, in_node, out_node, v=f"{offset} + {amplitude * factor} * (1 - 2 * acos((1 - {smoothness}) * sin(2 * {pi} * (time / {period})))/{pi})")


#sqr 2 ArcTan[Sin[2 π x]/δ]/π;
def contSquareSource(circuit, name, in_node, out_node, frequency, amplitude, offset=0, smoothness = 0.001):
    """
    Lägger till en kontinuerlig fyrkantsvågskälla till circuit som går från 0V till +amplitude

    smoothness - ändrar den kontinuerliga fyrkantsvågens skarphet. 0 ger perfekt (diskont.?) fyrkantsvåg, 0.1 och högre ger sinusvåg.
    """
    
    # factor ser till att signalens amplitud är 'amplitude' oavsett smoothness
    factor = 1 / float(atan(1/(smoothness * pi)))
    period = 1 / float(frequency)
    circuit.BehavioralSource(name, in_node, out_node, v=f"{offset} + {amplitude} / 2 * (1 + {factor} * atan( sin({pi} * time / {period}) / {delta*pi}))")

# Lägger till en kontinuerlig step-källa till circuit som stiger från 0V till +amplitude vid time = 0
def contStepSource(circuit, name, in_node, out_node, amplitude):
    # delta ändrar stegets skarphet. 0 ger ett perfekt (diskont.?) steg
    delta = 0.000
    circuit.BehavioralSource(name, in_node, out_node, v=f"{amplitude} * tanh(time / {delta})")

def contStepSource1(circuit, name, in_node, out_node, amplitude, delta):
    # delta ändrar stegets skarphet. 0 ger ett perfekt (diskont.?) steg
    circuit.BehavioralSource(name, in_node, out_node, v=f"{amplitude} * tanh(time / {delta})")

# Lägger till en kontinuerlig pwm-källa till circuit som går från 0V till +amplitude
def contPWMSource(circuit, name, in_node, out_node, frequency, amplitude, dutyCycle, offset=0):
    # delta ändrar den kontinuerliga fyrkantsvågens skarphet. 0 ger perfekt (diskont.?) fyrkantsvåg, 0.1 och högre ger sinusvåg.
    delta = 0.0001
    # factor ser till att signalens amplitud är 'amplitude' oavsett delta (trubbighet)
    factor = 1 / float(atan(1/(delta * pi)))
    period = 1 / float(frequency)
    circuit.BehavioralSource(name, in_node, out_node, v=f"{offset} + {amplitude} / 4 * ((1 + {factor} * atan( sin({pi} * time / {period}) / {smoothness*pi})) - (1 + {factor} * atan( sin({pi} * ((time/{period}) - {dutyCycle}) ) / {smoothness*pi})))**2")



class ContGreaterThanSubCircuit(SubCircuit):
    """ Kontinuerlig greater than subcircuit  a>b => out=+amplitude, a<b => out=-amplitude """
    __nodes__ = ('a', 'b', 'out', 'gnd')

    def __init__(self, name, amplitude, smoothness = 0.001):
        SubCircuit.__init__(self, name, *self.__nodes__)
        
        self.BehavioralSource(name, 'out', 'gnd', v=f"{amplitude} * tanh({1/smoothness} * V(a,b))")


class SwitchSubCircuit(SubCircuit):
    """ Subkrets med en diod och switch i parallell koppling """
    
    __nodes__ = ('t_in', 't_out', 't_c+', 't_c-')

    def __init__(self, name):
        SubCircuit.__init__(self, name, *self.__nodes__)
        self.raw_spice = '.Model DMOD D' + os.linesep
        self.model('switch', 'SW', Ron=1 @ u_mOhm, Roff=1 @ u_GOhm)

        self.D(1, 't_out', 't_in', model='DMOD')
        self.S(1, 't_in', 't_out', 't_c+', 't_c-', model='switch')