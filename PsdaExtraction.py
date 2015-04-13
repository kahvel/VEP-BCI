__author__ = 'Anti'

import constants as c
from signal_processing import Signal, FFT
import numpy as np
import scipy.interpolate


class PsdaExtraction(object):
    def __init__(self, connection):
        self.connection = connection
        """ @type : ConnectionProcessEnd.PlotConnection """
        self.pw = None
        self.values = [0 for _ in range(100)]
        self.coordinates_generator = None
        self.button_key_to_class_key = {
            c.PSDA:     c.MULTIPLE_REGULAR,
            c.SUM_PSDA: c.SINGLE_REGULAR,
            c.CCA:      c.MULTIPLE_AVERAGE,#?
            c.BOTH:     c.SINGLE_AVERAGE,#?
            c.SUM_BOTH: c.MULTIPLE_REGULAR#?
        }
        self.sensors = None
        self.connection.waitMessages(self.start, lambda: None, lambda: None, self.setup)

    def start(self):
        while True:
            message = self.connection.receiveMessagePoll(0.1)
            if isinstance(message, basestring):
                return message
            if message is not None:
                for sensor in self.sensors:
                    result = self.coordinates_generator.send(message.sensors[sensor]["value"])
                if result is not None:
                    print(result)
                    self.connection.sendMessage(result)
                    self.connection.sendMessage("PSDA")
                    self.main_generator.next()

    def setup(self):
        options, target_freqs = self.connection.receiveOptions()
        self.sensors = self.getSensors(options)
        coordinates_generator = [self.setupGenerator(options) for _ in range(len(self.sensors))]
        self.main_generator = self.setupMainGenerator(options, coordinates_generator, target_freqs)
        return c.SUCCESS_MESSAGE

    def setupGenerator(self, options):
        generator_class = self.getGeneratorClass(options)
        """ @type : Signal.Signal | FFT.FFT """
        generator_class.setup(options)
        coordinates_generator = generator_class.coordinates_generator()
        coordinates_generator.send(None)
        return coordinates_generator

    def setupMainGenerator(self, options, coordinates_generator, target_freqs):
        return mainGenerator(
            options[c.OPTIONS_LENGTH],
            options[c.OPTIONS_STEP],
            c.HEADSET_FREQ,
            coordinates_generator,
            target_freqs,
        )

    def getGeneratorClass(self, options):
        return getattr(
            FFT,
            self.button_key_to_class_key[options[c.DATA_METHOD]]
        )()

    def getSensors(self, options):
        raise NotImplementedError("getSensors not implemented!")


class MultipleChannelPsda(PsdaExtraction):
    def __init__(self, connection):
        PsdaExtraction.__init__(self, connection)

    def getSensors(self, options):
        return [options[c.DATA_SENSOR]]


class SingleChannelPsda(PsdaExtraction):
    def __init__(self, connection):
        PsdaExtraction.__init__(self, connection)

    def getSensors(self, options):
        return options[c.DATA_SENSORS]


def getMagnitude(freq, h_start, h_end, interpolation):
    result = 0
    for harmonic in range(h_start, h_end+1):
        result += interpolation(freq*harmonic)
    return result


def getSNR(freq, h_start, h_end, interpolation):
    result = 0
    for harmonic in range(h_start, h_end+1):
        harmonic_freq = freq*harmonic
        result += interpolation(harmonic_freq)*2/(interpolation(harmonic_freq-1)+interpolation(harmonic_freq+1))
    return result


def getMax(getValue, h_start, h_end, interpolation, target_freqs):
    max = 0
    max_index = -1
    for i in range(len(target_freqs)):
        ratio = getValue(target_freqs[i], h_start, h_end, interpolation)
        if ratio > max:
            max = ratio
            max_index = i
    return max, max_index


def mainGenerator(length, step, sampling_freq, coordinates_generators, target_freqs):
    coord_gen_count = len(coordinates_generators)
    coordinates = [None for _ in range(coord_gen_count)]
    calculate_indices = True
    for generator in coordinates_generators:
        generator.send(None)
    while True:
        max_freqs = [0 for _ in range(len(target_freqs))]
        j = 0
        while j != coord_gen_count:
            for channel in range(coord_gen_count):
                y = yield
                result = coordinates_generators[channel].send(y)
                if result is not None:
                    coordinates[channel] = result
                    j += 1
                    coordinates_generators[channel].next()
        ps_len = len(coordinates[0])
        if calculate_indices:
            if ps_len == length//2+1:
                calculate_indices = False
            freq_indices = []
            for freq in target_freqs:
                index = int(freq*(ps_len-1)*2/sampling_freq)
                freq_indices.append(index)
                freqs = np.fft.rfftfreq((ps_len-1)*2)*sampling_freq
        for channel in range(coord_gen_count):
            interpolation_fun = scipy.interpolate.interp1d(freqs, coordinates[channel])
            actual_max, max_index = getMax(getMagnitude, 1, 2, interpolation_fun, target_freqs)
            # print actual_max, sum(coordinates[channel])/len(coordinates[channel])*2+1
            # if sum(coordinates[channel])/len(coordinates[channel])*2+1 < actual_max:
            #     max_freqs[max_index] += 1
            max_freqs[max_index] += 1
            # textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(actual_max)+"  ")
            # maximum, max_index = getMax(getMagnitude, 2, 2, interpolation_fun, target_freqs)
            # textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"  ")
            # maximum, max_index = getMax(getMagnitude, 3, 3, interpolation_fun, target_freqs)
            # textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"\n")
            # maximum, max_index = getMax(getSNR, 1, 1, interpolation_fun, target_freqs)
            # textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"  ")
            # maximum, max_index = getMax(getSNR, 2, 2, interpolation_fun, target_freqs)
            # textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"  ")
            # maximum, max_index = getMax(getSNR, 3, 3, interpolation_fun, target_freqs)
            # textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(maximum)+"\n\n")
            # textbox.yview(Tkinter.END)
        for i in range(len(max_freqs)):
            if max_freqs[i] >= coord_gen_count:
                yield target_freqs[i]