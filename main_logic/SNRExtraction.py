__author__ = 'Anti'

from controllable_windows import ExtractionWindow
from signal_processing import FFT
from main_logic import Abstract
import Tkinter
import numpy as np


class SNRExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)

    def startDeleting(self):
        return lambda x: True

    def generator(self, index, start_deleting):
        coordinates_generator = self.getGenerator()
        try:
            for freq in self.freq_points:
                self.freq_indexes.append(int(freq*self.options["Length"]/self.headset_freq))
                print np.fft.rfftfreq(self.options["Length"])[self.freq_indexes[-1]]*self.headset_freq
            coordinates_generator.send(None)
            while True:
                y = yield
                coordinates = coordinates_generator.send(y)
                if coordinates is not None:
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]
                        ratio += coordinates[self.freq_indexes[i]*2-1]
                        if ratio> max:
                            max = ratio
                            max_index = i
                    self.connection.send(self.freq_points[max_index])
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]*2-1]
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]*3-1]
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"\n")
                    max = 0
                    max_index = -1
                    # peaks = scipy.signal.find_peaks_cwt(-coordinates, np.array([0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4, 1.6, 1.8, 2]))
                    # actual_index = 0
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]*2/(coordinates[self.freq_indexes[i]-2]+coordinates[self.freq_indexes[i]])
                        # asd = min(peaks, key=lambda x:abs(x-self.freq_indexes[i]))
                        # ratio = coordinates[asd]
                        if ratio> max:
                            max = ratio
                            # actual_index = asd
                            max_index = i
                    # print self.freq_indexes[max_index], actual_index, peaks
                    # print np.argmax(coordinates[self.freq_indexes[i]-3:self.freq_indexes])
                    # print max_index, coordinates[self.freq_indexes[max_index]-3], coordinates[self.freq_indexes[max_index]-2], \
                    #     coordinates[self.freq_indexes[max_index]-1], coordinates[self.freq_indexes[max_index]],\
                    #     coordinates[self.freq_indexes[max_index]+1], coordinates[self.freq_indexes[max_index]+2]
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]*2-1]*2/(coordinates[self.freq_indexes[i]*2-2]+coordinates[self.freq_indexes[i]*2])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]*3-1]*2/(coordinates[self.freq_indexes[i]*3-2]+coordinates[self.freq_indexes[i]*3])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"\n\n")
                    self.canvas.yview(Tkinter.END)
                    coordinates_generator.next()
        finally:
            print "Closing generator"
            coordinates_generator.close()


class Single(Abstract.Single, SNRExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        SNRExtraction.__init__(self, "Sum SNR")

    def getGenerator(self):
        return FFT.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class Multiple(Abstract.Multiple, SNRExtraction):
    def __init__(self):
        Abstract.Multiple.__init__(self)
        SNRExtraction.__init__(self, "SNR")

    def getGenerator(self):
        return FFT.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()