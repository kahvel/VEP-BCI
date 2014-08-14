__author__ = 'Anti'

import ExtractionWindow
import Signal
import scipy.signal
import Tkinter
import numpy as np
import matplotlib.pyplot as plt


class TemplateExtraction(ExtractionWindow.ExtractionWindow):
    def __init__(self, title):
        ExtractionWindow.ExtractionWindow.__init__(self, title)

    def startDeleting(self):
        return lambda x: True

    def generator(self, index, start_deleting):
        coordinates_generator = self.getGenerator()
        coordinates_generator.send(None)
        recorded_signals = []
        for signal in self.recorded_signals:
            if signal is not None:
                recorded_signals.append([])
                for packet in signal:
                    for i in range(len(self.sensor_names)):
                        coordinates = coordinates_generator.send(float(packet.sensors[self.sensor_names[i]]["value"]))
                        if coordinates is not None:
                            recorded_signals[-1].extend(coordinates)
            else:
                recorded_signals.append(None)
        print recorded_signals[0]
        print recorded_signals[1]

        # recorded_signals = []
        # for j in range(len(self.recorded_signals)):
        #     if self.recorded_signals[j] is not None:
        #         recorded_signals.append([])
        #         for i in range(len(self.recorded_signals[j])):
        #             for name in self.sensor_names:
        #                 recorded_signals[j].append(self.recorded_signals[j][i].sensors[name]["value"])
        #     else:
        #         recorded_signals.append(None)
        # for i in range(len(recorded_signals)):
        #     recorded_signals[i] = Signal.Signal.signalPipeline()

        # recorded_signals = []
        # x = np.arange(0, 512)
        # recorded_signals.append(np.sin(2*np.pi/12*x))
        # recorded_signals.append(np.sin(2*np.pi/15*x))
        # recorded_signals.append(np.sin(2*np.pi/20*x))

        count = [0 for _ in range(len(recorded_signals))]
        coordinates_generator = self.getGenerator()
        try:
            coordinates_generator.send(None)
            while True:
                y = yield
                coordinates = coordinates_generator.send(y)
                if coordinates is not None:
                    max = 0
                    max_index = 0
                    print coordinates
                    for i in range(len(recorded_signals[:-1])):
                        if recorded_signals[i] is not None:
                            conv = scipy.signal.correlate(recorded_signals[i], coordinates)
                            asd = np.max(conv)
                            if asd > max:
                                max = asd
                                max_index = i
                    count[max_index] += 1
                    print count
                    self.canvas.insert(Tkinter.END, str(max_index)+" "+str(max)+"\n")
                    self.canvas.yview(Tkinter.END)
                    coordinates_generator.next()
        finally:
            print "Closing generator"
            coordinates_generator.close()


class Single(TemplateExtraction, Signal.Single):
    def __init__(self):
        TemplateExtraction.__init__(self, "Template Extraction")
        Signal.Single.__init__(self)

    def getGenerator(self):
        return Signal.Regular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()


class Multiple(TemplateExtraction, Signal.Multiple):
    def __init__(self):
        TemplateExtraction.__init__(self, "Template Extraction")
        Signal.Multiple.__init__(self)

    def getGenerator(self):
        return Signal.Regular(self.options, self.window_function, self.channel_count, self.filter_coefficients).coordinates_generator()