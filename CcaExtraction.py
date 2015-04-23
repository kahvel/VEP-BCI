__author__ = 'Anti'

import numpy as np
import sklearn.cross_decomposition
import constants as c


def mainGenerator(length, step, target_freqs, generator_count):
    get_segment = True
    h = 3  # number of harmonics
    reference_signals = []
    t = np.arange(0, length)  # TODO???
    for freq in target_freqs:
        reference_signals.append([])
        for harmonic in range(1, h+1):
            reference_signals[-1].append(np.sin(np.pi*2*harmonic*freq/c.HEADSET_FREQ*t))
            reference_signals[-1].append(np.cos(np.pi*2*harmonic*freq/c.HEADSET_FREQ*t))
    cca = sklearn.cross_decomposition.CCA(n_components=1)
    coordinates = [None for _ in range(generator_count)]
    while True:
        for j in range(length/step):
            for i in range(generator_count):
                coordinates[i] = yield
            maximum = 0
            max_index = 0
            for i in range(len(reference_signals)):
                if get_segment:
                    signal_segment = np.array([reference_signals[i][j][:len(coordinates[0])] for j in range(len(reference_signals[i]))]).T
                    if len(coordinates) == length:
                        get_segment = False
                    cca.fit(np.array(coordinates).T, signal_segment)
                    res_x, res_y = cca.transform(np.array(coordinates).T, signal_segment)
                else:
                    cca.fit(np.array(coordinates).T, reference_signals[i].T)
                    res_x, res_y = cca.transform(np.array(coordinates).T, reference_signals[i].T)
                corr = np.corrcoef(res_x.T, res_y.T)[0][1]
                if corr > maximum:
                    maximum = corr
                    max_index = i
            # print maximum, 0.2
            # if maximum > 0.2:
            #     yield target_freqs[max_index]
            yield target_freqs[max_index]