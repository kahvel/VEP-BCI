__author__ = 'Anti'
import numpy as np
import scipy.signal


class FFT(object):
    def __init__(self):
        self.start_deleting = lambda x: True

    def filterSignal(self, signal):
        if self.filter:
            if self.filter_prev_state is None:
                return scipy.signal.lfilter(self.filter_coefficients, 1.0, signal)
            else:
                result, self.filter_prev_state = scipy.signal.lfilter(self.filter_coefficients, 1.0, signal, zi=self.filter_prev_state)
                return result
        else:
            return signal
        # if self.filter:
        #     if self.filter_prev_state is None:
        #         return scipy.signal.lfilter(self.filter_coefficients, 1.0, signal)
        #     else:
        #         signal_segment = self.getSegment(signal, 0)
        #         result1, current_state = scipy.signal.lfilter(self.filter_coefficients, 1.0, signal_segment, zi=self.filter_prev_state)
        #         self.filter_prev_state = current_state
        #         result2, state = scipy.signal.lfilter(self.filter_coefficients, 1.0, signal[self.step:], zi=current_state)
        #         return list(result1)+list(result2)
        # else:
        #     return signal

    def normaliseSpectrum(self, fft):
        if self.normalise:
            return fft/sum(fft)
        else:
            return np.log10(fft)

    def scaleYa(self, y,  index, plot_count, new_max=-100, new_min=100):
        return ((((y - (-10)) * (new_max - new_min)) / (10 - (-10))) + new_min
                + index*self.window_height + self.window_height/2) / plot_count

    def scalea(self, coordinates, index, packet_count):
        result = []
        for i in range(len(coordinates)):
            result.append(i*self.window_width/len(coordinates))
            result.append(self.scaleYa(coordinates[i], index, self.plot_count))
        return result

    def segmentPipeline(self, coordinates):
        detrended_segment = self.detrendSignal(coordinates)
        filtered_segment = self.filterSignal(detrended_segment)
        return filtered_segment

    def signalPipeline(self, coordinates):
        windowed_signal = self.windowSignal(coordinates, self.window_function)
        amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        self.canvas.delete(self.line)
        self.line = self.canvas.create_line(self.scalea(windowed_signal, 0, 0), fill="Red")
        return amplitude_spectrum


        # detrended_signal = self.detrendSignal(coordinates)
        # filtered_signal = self.filterSignal(detrended_signal)
        # windowed_signal = self.windowSignal(filtered_signal, self.window_function)
        # amplitude_spectrum = np.abs(np.fft.rfft(windowed_signal))
        # self.canvas.delete(self.line)
        # self.line = self.canvas.create_line(self.scalea(windowed_signal, 0, 0), fill="Red")
        # return amplitude_spectrum