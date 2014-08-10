__author__ = 'Anti'
import numpy as np
import scipy.signal
import Tkinter
import ScrolledText
import ControllableWindow
import FFT


class ExtractionWindow(ControllableWindow.ControllableWindow):
    def __init__(self, title):
        ControllableWindow.ControllableWindow.__init__(self, title, 525, 200)
        self.canvas = ScrolledText.ScrolledText(self)
        self.canvas.pack()
        self.freq_points = None
        self.freq_indexes = None
        self.recorded_signals = None
        self.connection = None

    def resetCanvas(self):
        self.canvas.insert(Tkinter.END, "Starting\n")

    def setup(self, options, sensor_names, freq_points=None, recorded_signal=None, connection=None):
        self.freq_points = freq_points
        self.freq_indexes = []
        self.recorded_signals = recorded_signal
        self.connection = connection
        ControllableWindow.ControllableWindow.setup(self, options, sensor_names)

    def generator(self, index, start_deleting):
        coordinates_generator = self.coordinates_generator(index)
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
                    self.connection.send(self.freq_points[max_index])
                    # print np.argmax(coordinates[self.freq_indexes[i]-3:self.freq_indexes])
                    # print max_index, coordinates[self.freq_indexes[max_index]-3], coordinates[self.freq_indexes[max_index]-2], \
                    #     coordinates[self.freq_indexes[max_index]-1], coordinates[self.freq_indexes[max_index]],\
                    #     coordinates[self.freq_indexes[max_index]+1], coordinates[self.freq_indexes[max_index]+2]
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