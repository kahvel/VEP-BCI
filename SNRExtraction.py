__author__ = 'Anti'

import ExtractionWindow
import FFT
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
            packet_count = 0
            for freq in self.freq_points:
                self.freq_indexes.append(int(freq*self.options["Length"]/self.headset_freq))
                print np.fft.rfftfreq(self.options["Length"])[self.freq_indexes[-1]]*self.headset_freq
            coordinates_generator.send(None)
            while True:
                y = yield
                coordinates = coordinates_generator.send(y)
                if coordinates is not None:
                    if start_deleting(packet_count):
                        packet_count = 0
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]
                        if ratio> max:
                            max = ratio
                            max_index = i
                    print max_index, self.freq_points
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/2-1]
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/4-1]
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"\n")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]-1]*2/(coordinates[self.freq_indexes[i]-2]+coordinates[self.freq_indexes[i]])
                        if ratio> max:
                            max = ratio
                            max_index = i
                    self.connection.send(self.freq_points[max_index])
                    # print np.argmax(coordinates[self.freq_indexes[i]-3:self.freq_indexes])
                    # print max_index, coordinates[self.freq_indexes[max_index]-3], coordinates[self.freq_indexes[max_index]-2], \
                    #     coordinates[self.freq_indexes[max_index]-1], coordinates[self.freq_indexes[max_index]],\
                    #     coordinates[self.freq_indexes[max_index]+1], coordinates[self.freq_indexes[max_index]+2]
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/2-1]*2/(coordinates[self.freq_indexes[i]/2-2]+coordinates[self.freq_indexes[i]/2])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"  ")
                    max = 0
                    max_index = -1
                    for i in range(len(self.freq_indexes)):
                        ratio = coordinates[self.freq_indexes[i]/4-1]*2/(coordinates[self.freq_indexes[i]/4-2]+coordinates[self.freq_indexes[i]/4])
                        if ratio > max:
                            max = ratio
                            max_index = i
                    self.canvas.insert(Tkinter.END, str(self.freq_points[max_index])+" "+str(max)+"\n\n")
                    self.canvas.yview(Tkinter.END)
                    coordinates_generator.next()
                packet_count += 1
        finally:
            print "Closing generator"
            coordinates_generator.close()


class SumSNR(SNRExtraction, FFT.Single):
    def __init__(self):
        SNRExtraction.__init__(self, "Sum SNR")
        FFT.Single.__init__(self)

    def getGenerator(self):
        return FFT.SingleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class SNR(SNRExtraction, FFT.Multiple):
    def __init__(self):
        SNRExtraction.__init__(self, "SNR")
        FFT.Multiple.__init__(self)

    def getGenerator(self):
        return FFT.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()