#
# Innehåller olika vanliga Python-script för att förenkla programmeringen
#

import numpy as np
import matplotlib.pyplot as plt
from PySpice.Probe import WaveForm
from PySpice.Unit import *
from scipy.fft import fft, fftfreq

def plotFourier(waveform: WaveForm, step_time: PeriodValue):
    """ Plots a fourier transform of the supplied waveform """
    y = np.array(waveform)

    # Number of sample points
    N = len(y)
    # sample spacing
    T = float(step_time)
    x = np.linspace(0.0, N * T, N, endpoint=False)
    yf = fft(y)
    xf = fftfreq(N, T)[:N // 2]

    plt.plot(xf, 2.0 / N * np.abs(yf[0:N // 2]))


def plotSet(circuits: list, net: str, step_time: PeriodValue, final_time: PeriodValue):
    for circuit, label in circuits:
        simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        analysis = simulator.transient(step_time=step_time, end_time=final_time)
        plt.plot(analysis[net], label=f"$\mathregular{{{ label }}}$")
        