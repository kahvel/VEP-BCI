__author__ = 'Anti'

from controllable_windows import ExtractionWindow
from signal_processing import FFT
from main_logic import Abstract
import Tkinter
import numpy as np


class PSDAExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)

    def getGenerator(self, index):
        return self.generator(index)

    def generator(self, index):
        coordinates_generators = [self.getCoordGenerator() for _ in range(self.getCoordGenCount())]
        main_generator = mainGenerator(self.options["Length"], self.options["Step"], self.headset_freq,
                                       coordinates_generators, self.freq_points, self.canvas)
        main_generator.send(None)
        i = 0
        while True:
            i += 1
            coordinate = yield
            result = main_generator.send(coordinate)
            if result is not None:
                self.actual_result[result] += 1
                self.connection.send(result)
                main_generator.next()


def mainGenerator(length, step, sampling_freq, coordinates_generators, target_freqs, textbox):
    count = [0 for _ in range(len(target_freqs))]
    coord_gen_count = len(coordinates_generators)
    coordinates = [None for _ in range(coord_gen_count)]
    freq_indices = []
    for freq in target_freqs:
        freq_indices.append(int(freq*length/sampling_freq))
        print np.fft.rfftfreq(length)[freq_indices[-1]]*sampling_freq
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
        for channel in range(coord_gen_count):
            max = 0
            max_index = -1
            for i in range(len(freq_indices)):
                ratio = coordinates[channel][freq_indices[i]-1]
                ratio += coordinates[channel][freq_indices[i]*2-1]
                if ratio> max:
                    max = ratio
                    max_index = i
            max_freqs[max_index] += 1
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(max)+"  ")
            max = 0
            max_index = -1
            for i in range(len(freq_indices)):
                ratio = coordinates[channel][freq_indices[i]*2-1]
                if ratio > max:
                    max = ratio
                    max_index = i
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(max)+"  ")
            max = 0
            max_index = -1
            for i in range(len(freq_indices)):
                ratio = coordinates[channel][freq_indices[i]*3-1]
                if ratio > max:
                    max = ratio
                    max_index = i
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(max)+"\n")
            max = 0
            max_index = -1
            # peaks = scipy.signal.find_peaks_cwt(-coordinates, np.array([0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]))
            # actual_index = 0
            for i in range(len(freq_indices)):
                ratio = coordinates[channel][freq_indices[i]-1]*2/(coordinates[channel][freq_indices[i]-2]+coordinates[channel][freq_indices[i]])
                # asd = min(peaks, key=lambda x:abs(x-freq_indices[i]))
                # ratio = coordinates[asd]
                if ratio> max:
                    max = ratio
                    # actual_index = asd
                    max_index = i
            # print freq_indices[max_index], actual_index, peaks
            # print np.argmax(coordinates[freq_indices[i]-3:freq_indices])
            # print max_index, coordinates[freq_indices[max_index]-3], coordinates[freq_indices[max_index]-2], \
            #     coordinates[freq_indices[max_index]-1], coordinates[freq_indices[max_index]],\
            #     coordinates[freq_indices[max_index]+1], coordinates[freq_indices[max_index]+2]
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(max)+"  ")
            max = 0
            max_index = -1
            for i in range(len(freq_indices)):
                ratio = coordinates[channel][freq_indices[i]*2-1]*2/(coordinates[channel][freq_indices[i]*2-2]+coordinates[channel][freq_indices[i]*2])
                if ratio > max:
                    max = ratio
                    max_index = i
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(max)+"  ")
            max = 0
            max_index = -1
            for i in range(len(freq_indices)):
                ratio = coordinates[channel][freq_indices[i]*3-1]*2/(coordinates[channel][freq_indices[i]*3-2]+coordinates[channel][freq_indices[i]*3])
                if ratio > max:
                    max = ratio
                    max_index = i
            textbox.insert(Tkinter.END, str(target_freqs[max_index])+" "+str(max)+"\n\n")
            textbox.yview(Tkinter.END)
        # print max_freqs, count
        for i in range(len(max_freqs)):
            if max_freqs[i] == coord_gen_count:
                yield target_freqs[i]
                count[i] += 1


class Single(Abstract.Single, PSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        PSDAExtraction.__init__(self, "Sum Power Spectrum Density Analysis")

    def getCoordGenCount(self):
        return 1

    def getCoordGenerator(self):
        return FFT.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class Multiple(Abstract.Single, PSDAExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        PSDAExtraction.__init__(self, "Power Spectrum Density Analysis")

    def getCoordGenCount(self):
        return self.channel_count

    def getCoordGenerator(self):
        return FFT.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()