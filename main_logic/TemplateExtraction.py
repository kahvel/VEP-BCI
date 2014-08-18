__author__ = 'Anti'

from controllable_windows import ExtractionWindow
from signal_processing import Signal
from main_logic import Abstract
import scipy.signal
import Tkinter
import numpy as np
import sklearn.cross_decomposition


# class TemplateExtraction(ExtractionWindow.ExtractionWindow):
#     def __init__(self, title):
#         ExtractionWindow.ExtractionWindow.__init__(self, title)
#
#     def startDeleting(self):
#         return lambda x: True
#
#     def generator(self, index, start_deleting):
#         coordinates_generator = self.getGenerator()
#         coordinates_generator.send(None)
#         recorded_signals = []
#         for signal in self.recorded_signals:
#             if signal is not None:
#                 recorded_signals.append([])
#                 for packet in signal:
#                     for i in range(len(self.sensor_names)):
#                         coordinates = coordinates_generator.send(float(packet.sensors[self.sensor_names[i]]["value"]))
#                         if coordinates is not None:
#                             recorded_signals[-1].extend(coordinates)
#             else:
#                 recorded_signals.append(None)
#         print recorded_signals[0]
#         print recorded_signals[1]
#
#         # recorded_signals = []
#         # for j in range(len(self.recorded_signals)):
#         #     if self.recorded_signals[j] is not None:
#         #         recorded_signals.append([])
#         #         for i in range(len(self.recorded_signals[j])):
#         #             for name in self.sensor_names:
#         #                 recorded_signals[j].append(self.recorded_signals[j][i].sensors[name]["value"])
#         #     else:
#         #         recorded_signals.append(None)
#         # for i in range(len(recorded_signals)):
#         #     recorded_signals[i] = Signal.Signal.signalPipeline()
#
#         # recorded_signals = []
#         # x = np.arange(0, 512)
#         # recorded_signals.append(np.sin(2*np.pi/12*x))
#         # recorded_signals.append(np.sin(2*np.pi/15*x))
#         # recorded_signals.append(np.sin(2*np.pi/20*x))
#
#         count = [0 for _ in range(len(recorded_signals))]
#         coordinates_generator = self.getGenerator()
#         try:
#             coordinates_generator.send(None)
#             while True:
#                 y = yield
#                 coordinates = coordinates_generator.send(y)
#                 if coordinates is not None:
#                     max = 0
#                     max_index = 0
#                     print coordinates
#                     for i in range(len(recorded_signals[:-1])):
#                         if recorded_signals[i] is not None:
#                             conv = scipy.signal.correlate(recorded_signals[i], coordinates)
#                             asd = np.max(conv)
#                             if asd > max:
#                                 max = asd
#                                 max_index = i
#                     count[max_index] += 1
#                     print count
#                     self.canvas.insert(Tkinter.END, str(max_index)+" "+str(max)+"\n")
#                     self.canvas.yview(Tkinter.END)
#                     coordinates_generator.next()
#         finally:
#             print "Closing generator"
#             coordinates_generator.close()

class TemplateExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)

    def generator(self, index):
        h = 3  # number of harmonics
        target_signals = []
        t = np.arange(0, self.options["Length"])
        for freq in self.freq_points:
            target_signals.append([])
            for harmonic in range(1, h+1):
                target_signals[-1].append(np.sin(np.pi*2*harmonic*freq/self.headset_freq*t))
                target_signals[-1].append(np.cos(np.pi*2*harmonic*freq/self.headset_freq*t))
        cca = sklearn.cross_decomposition.CCA(n_components=1)
        count = [0 for _ in range(len(self.freq_points))]
        coordinates_generators = [self.getGenerator() for _ in range(self.channel_count)]
        try:
            for generator in coordinates_generators:
                generator.send(None)
            i = 0
            coordinates = [None for _ in range(self.channel_count)]
            while i != self.options["Length"]/self.options["Step"]*self.channel_count:
                for channel in range(self.channel_count):
                    y = yield
                    result = coordinates_generators[channel].send(y)
                    if result is not None:
                        i += 1
                        coordinates[channel] = result
            while True:
                for j in range(self.options["Length"]/self.options["Step"]):
                    print coordinates
                    i = 0
                    while i != self.channel_count:
                        for channel in range(self.channel_count):
                            y = yield
                            result = coordinates_generators[channel].send(y)
                            if result is not None:
                                coordinates[channel] = np.roll(result, -(j+1)*self.options["Step"])
                                i += 1
                    max = 0
                    max_index = 0
                    for i in range(len(target_signals)):
                        res_x, res_y = cca.fit_transform(np.array(coordinates).T, np.array(target_signals[i]).T)
                        corr = np.corrcoef(res_x.T, res_y.T)[0][1]
                        # print self.freq_points[i], corr
                        if corr > max:
                            max = corr
                            max_index = i
                    count[max_index] += 1
                    print self.freq_points[max_index], max
                    print count
                    self.connection.send(self.freq_points[max_index])
                    for generator in coordinates_generators:
                        generator.next()
        finally:
            print "Closing generator"
            for generator in coordinates_generators:
                generator.close()


class Single(Abstract.Single, TemplateExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        TemplateExtraction.__init__(self, "Template Extraction")

    def getGenerator(self):
        return Signal.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class Multiple(Abstract.Single, TemplateExtraction):
    def __init__(self):
        Abstract.Single.__init__(self)
        TemplateExtraction.__init__(self, "Template Extraction")

    def getGenerator(self):
        return Signal.MultipleRegular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()