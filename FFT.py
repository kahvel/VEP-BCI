__author__ = 'Anti'
import numpy as np
import scipy.signal


class FFT(object):
    def __init__(self):
        self.start_deleting = lambda x: True

    def normaliseSpectrum(self, fft):
        if self.normalise:
            return fft/sum(fft)
        else:
            return np.log10(fft)[1:]

    def scaleYa(self, y,  index, plot_count, new_max=-100, new_min=100):
        return ((((y - (-10)) * (new_max - new_min)) / (10 - (-10))) + new_min
                + index*self.window_height + self.window_height/2) / plot_count

    def scalea(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*self.window_width/len(coordinates))
            result.append(self.scaleYa(coordinates[i], index, self.plot_count))
        return result

    def segmentPipeline(self, coordinates, filter_prev_state):
        detrended_segment = self.detrendSignal(coordinates)
        filtered_segment, filter_prev_state = self.filterSignal(detrended_segment, filter_prev_state)
        return filtered_segment, filter_prev_state

    def signalPipeline(self, coordinates):
        windowed_signal = self.windowSignal(coordinates, self.window_function)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        # self.canvas.delete(self.line)
        # self.line = self.canvas.create_line(self.scalea(windowed_signal, 0, 0), fill="Red")
        return amplitude_spectrum