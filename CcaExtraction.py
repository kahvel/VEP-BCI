__author__ = 'Anti'

import numpy as np
import sklearn.cross_decomposition


def mainGenerator(length, step, sampling_freq, coordinates_generators, target_freqs):
    get_segment = True
    coord_gen_count = len(coordinates_generators)
    h = 3  # number of harmonics
    target_signals = []
    t = np.arange(0, length)
    for freq in target_freqs:
        target_signals.append([])
        for harmonic in range(1, h+1):
            target_signals[-1].append(np.sin(np.pi*2*harmonic*freq/sampling_freq*t))
            target_signals[-1].append(np.cos(np.pi*2*harmonic*freq/sampling_freq*t))
    cca = sklearn.cross_decomposition.CCA(n_components=1)
    coordinates = [None for _ in range(coord_gen_count)]
    while True:
        for j in range(length/step):
            # print coordinates
            i = 0
            while i != coord_gen_count:
                for channel in range(coord_gen_count):
                    y = yield
                    result = coordinates_generators[channel].send(y)
                    if result is not None:
                        coordinates[channel] = np.roll(result, -(j+1)*step)
                        i += 1
                        coordinates_generators[channel].next()
            maximum = 0
            max_index = 0
            for i in range(len(target_signals)):
                if get_segment:
                    signal_segment = np.array([target_signals[i][j][:len(coordinates[0])] for j in range(len(target_signals[i]))]).T
                    if len(coordinates) == length:
                        get_segment = False
                    res_x, res_y = cca.fit_transform(np.array(coordinates).T, signal_segment)
                else:
                    res_x, res_y = cca.fit_transform(np.array(coordinates).T, target_signals[i].T)
                corr = np.corrcoef(res_x.T, res_y.T)[0][1]
                if corr > maximum:
                    maximum = corr
                    max_index = i
            # print maximum, 0.2
            # if maximum > 0.2:
            #     yield target_freqs[max_index]
            yield target_freqs[max_index]