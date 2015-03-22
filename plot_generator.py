__author__ = 'Anti'

import scipy.signal
import numpy as np
import matplotlib.pyplot as plt


def getWave(freq, time, duty=0.5):
    np_square_wave_period = 2 * np.pi
    return [i if i != -1 else 0 for i in scipy.signal.square(time * np_square_wave_period * freq, duty=duty)]


def newSignalPlot(signal, plot_nr, freq):
    ax = plt.subplot(3, 1, plot_nr)
    plt.tight_layout()
    plt.title(str(freq)+" Hz")
    plt.ylim(-0.5, 1.5)
    ax.set_yticks(ticks=[0, 1])
    ax.set_xticks(ticks=[float(i)/60 for i in range(60)], minor=True)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("State")
    ax.grid(which='minor', alpha=0.7)
    ax.grid(which='major', alpha=0.7)
    #plt.grid(which="both")
    plt.plot(time, signal)


def squareWaves():
    newSignalPlot(wave10, 1, 10)
    newSignalPlot(wave11a, 2, 11)
    newSignalPlot(wave12a, 3, 12)


def rectWaves():
    newSignalPlot(wave10, 1, 10)
    newSignalPlot(wave11b, 2, 11)
    newSignalPlot(wave12b, 3, 12)


time = np.linspace(0, 1, 6000)

wave10 = getWave(10, time)
wave11b = [1 if i < 3 or i > 6 and i < 9 or i > 11 and i < 14 or i > 17 and i < 20 or i > 22 and i < 25 or i > 28 and i < 30 or \
               i > 33 and i < 36 or i > 39 and i < 41 or i > 44 and i < 47 or i > 50 and i < 52 or i > 55 and i < 58 else 0 for i in time*60]
wave11a = getWave(11, time)
wave12a = getWave(12, time)
wave12b = getWave(12, time, duty=0.6)

rectWaves()
#squareWaves()

# fft11 = np.abs(np.fft.rfft(wave10)**2)
# plt.subplot(212)
# plt.xlim(0, 100)
# plt.grid(True)
# plt.plot(fft11)

plt.show()
