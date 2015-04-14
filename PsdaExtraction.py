__author__ = 'Anti'

import numpy as np
import scipy.interpolate


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
        for i in range(len(max_freqs)):
            if max_freqs[i] >= coord_gen_count:
                yield target_freqs[i]