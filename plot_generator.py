__author__ = 'Anti'

import scipy.signal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib2tikz
from scipy import interpolate


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

def runOldPlotGenerator():
    rectWaves()
    #squareWaves()

    # fft11 = np.abs(np.fft.rfft(wave10)**2)
    # plt.subplot(212)
    # plt.xlim(0, 100)
    # plt.grid(True)
    # plt.plot(fft11)

    plt.show()

def detrend():
    samples = 40
    rec_period = 3
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)

    sin = np.sin(time*2*np.pi)
    sin_trend = sin+time
    #const_trend = [3 for _ in range(len(time))]
    #sin_const_trend = sin+const_trend

    sin_detrend = scipy.signal.detrend(sin_trend)
    fft_detrend = np.fft.rfft(sin_detrend)
    fft_trend = np.fft.rfft(sin_trend)
    #fft_const_trend = np.fft.rfft(sin_const_trend)
    bins = (np.fft.rfftfreq(len(sin))*sampling_rate)[1:]

    plt.subplot(311)
    plt.plot(time, sin_trend, "b")
    plt.plot(time, time, "k")
    plt.plot(time, sin_detrend, "g")
    plt.plot(time, [0 for _ in range(len(time))], "k")
    #plt.plot(time, sin_const_trend, "r")
    #plt.plot(time, const_trend, "k")
    plt.subplot(312)
    plt.plot(bins, (np.abs(fft_trend))[1:]*2/samples, "o")
    plt.plot(bins, (np.abs(fft_detrend))[1:]*2/samples, "o")
    #plt.plot(bins, (np.abs(fft_const_trend))[1:], "o")
    plt.subplot(313)
    plt.plot((np.fft.rfftfreq(len(time))*sampling_rate)[1:], np.abs(np.fft.rfft(time))[1:]*2/samples, "o")
    plt.plot(bins, np.abs(np.fft.rfft([0 for _ in range(len(time))]))[1:]*2/samples, "o")
    #plt.plot(bins, np.abs(np.fft.rfft(const_trend))[1:]*2/samples, "o")
    #matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()

def step():
    time = np.linspace(0, np.pi*10, 100)
    sin = np.sin(time)
    sin_step = sin+np.sign(time-np.pi*5)

    sin_detrend = scipy.signal.detrend(sin_step, bp=1)
    fft_detrend = np.fft.rfft(sin_detrend)
    fft_step = np.fft.rfft(sin_step)
    bins = np.fft.rfftfreq(len(sin))

    plt.subplot(211)
    plt.plot(time, sin_step)
    plt.plot(time, sin_detrend)
    plt.subplot(212)
    plt.plot(bins, np.log10(np.abs(fft_step)), "o")
    plt.plot(bins, np.log10(np.abs(fft_detrend)), "o")
    plt.plot()
    plt.show()

def pure_tone():
    samples = 40
    rec_period = 2
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)
    sin = np.sin(time*2*np.pi)

    fft = np.fft.rfft(sin)
    bins = (np.fft.rfftfreq(len(sin))*sampling_rate)[1:]

    plt.subplot(211)
    plt.plot(time, sin, "b")
    plt.subplot(212)
    plt.plot(bins, (np.abs(fft))[1:]*2/samples, "o")
    #matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()

def square_wave():
    samples = 80
    rec_period = 2
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)
    sin1 = np.sin(time*2*np.pi)
    sin2 = np.sin(time*2*np.pi*3)/3
    sin3 = np.sin(time*2*np.pi*5)/5
    square = scipy.signal.square(time*2*np.pi)/4*np.pi

    fft1 = np.fft.rfft(sin1)
    fft2 = np.fft.rfft(sin2)
    fft3 = np.fft.rfft(sin3)
    fft_square = np.fft.rfft(square)
    bins = (np.fft.rfftfreq(len(sin1))*sampling_rate)[1:]

    plt.subplot(211)
    plt.plot(time, sin1)
    plt.plot(time, sin2+sin1)
    plt.plot(time, sin3+sin2+sin1)
    plt.plot(time, square)
    plt.subplot(212)
    plt.plot(bins[1:4], (np.abs(fft1))[1:4]*2/samples, "o")
    plt.plot(bins[4:8], (np.abs(fft2))[4:8]*2/samples, "o")
    plt.plot(bins[8:12], (np.abs(fft3))[8:12]*2/samples, "o")
    plt.plot(bins[12:], (np.abs(fft_square))[12:-1]*2/samples, "o")
    #matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()

def zero_padding():
    samples = 77
    rec_period = 4
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)
    sin = np.sin(time*3.75*np.pi)
    win = np.hanning(len(sin))

    pad_count = 23
    padded_sin = np.pad(sin, (0,pad_count), 'constant')

    fft = np.fft.rfft(sin)
    fft_padded = np.fft.rfft(padded_sin)
    bins = (np.fft.rfftfreq(len(sin))*sampling_rate)[1:]

    plt.subplot(321)
    plt.plot(time, sin)
    plt.subplot(322)
    plt.plot(bins, (np.abs(fft))[1:]*2/samples, "o")
    plt.subplot(323)
    plt.plot(np.linspace(0, (samples+pad_count)*rec_period/float(samples), samples+pad_count), padded_sin)
    plt.subplot(324)
    plt.plot((np.fft.rfftfreq(len(padded_sin))*sampling_rate)[1:], (np.abs(fft_padded))[1:]*2/samples, "o")
    plt.subplot(325)
    padded_sin_win = np.pad(sin*win, (0, pad_count), 'constant')
    plt.plot(np.linspace(0, (samples+pad_count)*rec_period/float(samples), samples+pad_count), padded_sin_win)
    plt.subplot(326)
    plt.plot((np.fft.rfftfreq(len(padded_sin_win))*sampling_rate)[1:], np.abs(np.fft.rfft(padded_sin_win))[1:]*2/samples, "o")
    matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()

def interpolation():
    samples = 77
    rec_period = 4
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)
    sin = np.sin(time*3.75*np.pi)

    pad_count = 23
    padded_sin = np.pad(np.sin(time*3.75*np.pi), (0,pad_count), 'constant')

    fft = np.fft.rfft(sin)
    fft_padded = np.fft.rfft(padded_sin)
    bins = (np.fft.rfftfreq(len(sin))*sampling_rate)[1:]

    #print(np.insert(bins, 7, 1.875))
    new_bins = np.insert(bins, 7, 1.875)
    interpolation_fun = interpolate.interp1d(bins, np.abs(fft)[1:]*2/samples, "linear") #quadratic
    asd = np.fft.rfftfreq(100)[2:-1]*sampling_rate
    interpolationb = interpolate.barycentric_interpolate(bins, np.abs(fft)[1:]*2/samples, new_bins)

    plt.subplot(221)
    plt.plot(time, sin)
    plt.subplot(222)
    plt.plot(bins, (np.abs(fft))[1:]*2/samples)
    plt.plot(new_bins, [interpolation_fun(i) for i in new_bins], "o")
    plt.plot(new_bins, interpolationb)
    plt.subplot(223)
    plt.plot(np.linspace(0, (samples+pad_count)*rec_period/float(samples), samples+pad_count), padded_sin)
    plt.subplot(224)
    plt.plot((np.fft.rfftfreq(len(padded_sin))*sampling_rate)[1:], (np.abs(fft_padded))[1:]*2/samples, "o")
    #matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()

def cross_correlation():
    samples = 40
    rec_period = 1
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)
    time_long = np.linspace(0, rec_period*2, samples*2)
    signal = np.sin(time*2*np.pi)
    sin = np.sin(time_long*2*np.pi)
    cos = np.cos(time_long*2*np.pi)
    result_sin = (np.correlate(sin, signal, "valid"))
    result_cos = (np.correlate(cos, signal, "valid"))

    plt.subplot(122)
    plt.plot(np.linspace(-rec_period/2.0, rec_period/2.0, samples+1), np.abs(result_sin*2/samples))
    plt.plot(np.linspace(-rec_period/2.0, rec_period/2.0, samples+1), np.abs(result_cos*2/samples))
    plt.subplot(121)
    plt.plot(time_long, sin)
    plt.plot(time_long, cos)
    lag = rec_period/2.0
    plt.plot(np.linspace(lag, rec_period+lag, samples), signal)
    #matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()


def window():
    samples = 120
    rec_period = 7.4
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)
    sin = np.sin(time*2*np.pi)
    win = np.hanning(len(sin))
    #rect_win = np.kaiser(len(sin), 0)

    sin_win = sin*win
    fft = np.fft.rfft(sin)
    fft_win = np.fft.rfft(sin_win)
    bins = (np.fft.rfftfreq(len(sin))*sampling_rate)[1:]
    #new_bins = np.insert(bins, 3, 1) #80, 3.4, time*2*np.pi

    #interpolation_sin = interpolate.barycentric_interpolate(bins, np.abs(fft)[1:]*2/samples, new_bins)
    #interpolation_win = interpolate.barycentric_interpolate(bins, np.abs(fft_win)[1:]*2/samples, new_bins)
    plt.subplot(321)
    plt.plot(time, sin)
    plt.plot(time, sin_win)
    plt.subplot(322)
    #plt.plot(new_bins, interpolation_sin, "o")
    #plt.plot(new_bins, interpolation_win, "o")
    plt.plot(bins, (np.abs(fft))[1:]/np.sum(np.abs(fft)[1:]), "o")#*2/samples
    plt.plot(bins, (np.abs(fft_win)[1:])/np.sum(np.abs(fft_win)[1:]), "o")
    plt.subplot(323)
    plt.plot(time, win, "k")
    plt.plot(time, -win, "k")
    plt.plot(time, sin_win, "g")
    plt.subplot(324)
    plt.plot(time, win, "k")


    #plt.subplot(325)
    #plt.plot(time, sin*win)
    #plt.plot(time, (sin+1)*win)
    #plt.plot(235)
    #plt.plot(bins, (np.abs(np.fft.rfft(sin*win)))[1:]/np.sum(np.abs(np.fft.rfft(sin*win))[1:]))
    #plt.plot(bins, (np.abs(np.fft.rfft((sin+1)*win)))[1:]/np.sum(np.abs(np.fft.rfft((sin+1)*win))[1:]))

    #plt.subplot(325)
    #plt.plot(time, sin)
    #plt.plot(time, rect_win, "k")
    #plt.plot(time, -rect_win, "k")
    #plt.subplot(326)
    #plt.plot(time, rect_win, "k")
    #matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()

def window2():
    samples = 70
    rec_period = 5.4
    sampling_rate = samples/rec_period
    time = np.linspace(0, rec_period, samples)
    sin = np.sin(time*2*np.pi)
    win = np.hanning(len(sin))
    bins = (np.fft.rfftfreq(len(sin))*sampling_rate)[1:]

    const = 1

    plt.subplot(221)
    plt.plot(time, sin+const)
    plt.plot(time, (sin+const)*win)
    plt.plot(time, win*2)
    plt.subplot(222)
    plt.plot(bins, np.abs(np.fft.rfft(sin+const))[1:]/np.sum(np.abs(np.fft.rfft(sin+const))[1:]))
    plt.plot(bins, np.abs(np.fft.rfft((sin+const)*win))[1:]/np.sum(np.abs(np.fft.rfft((sin+const)*win))[1:]))
    #plt.plot(bins, np.abs(np.fft.rfft((sin+const)*win))[1:]-np.abs(np.fft.rfft(sin*win))[1:])
    #print(np.abs(np.fft.rfft((sin+const)*win))[1:]-np.abs(np.fft.rfft(sin*win))[1:])
    plt.subplot(223)
    plt.plot(time, win*const)
    plt.subplot(224)
    plt.plot(bins, np.abs(np.fft.rfft(win*const))[1:]*2/samples)
    #matplotlib2tikz.save( 'myfile.tikz' )
    plt.show()
