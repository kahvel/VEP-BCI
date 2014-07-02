__author__ = 'Anti'
import MyWindows
import Tkinter
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class FFTWindow(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "FFT", 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False

    def generator(self):
        count = 16
        x = 0
        coordinates = []
        line = self.canvas.create_line(0,0,0,0)
        # self.canvas.create_line(80, 0, 80, 200)
        # self.canvas.create_line(160, 0, 160, 200)
        lis = []
        e = []
        p = []
        lis2 = []
        e2 = []
        p2 = []
        while True:
            for _ in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                coordinates.append(y)
                x += 1
            if x > 1024:
                # e.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))[79])
                # lis.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))[80])
                # p.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))[81])
                # e2.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))[159])
                # lis2.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))[160])
                # p2.append(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))[161])
                del coordinates[:count]
            self.canvas.delete(line)
            #line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(coordinates)))*-100+400)])
            line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(signal.detrend(coordinates))))*-50+400)])
            self.canvas.update()

            #print np.fft.rfftfreq(len(coordinates))[81]*128

            # print(sum(lis), (sum(e)+sum(p))/2)
            # lis = []
            # e = []
            # p = []
            # lis2 = []
            # e2 = []
            # p2 = []

            # if x>= 1024:#sum(e)+sum(p)!= 0 and sum(e2)+sum(p2) != 0:#len(lis) == 10:
            #     if abs(sum(lis)/(sum(e)+sum(p))/2) > abs(sum(lis2)/(sum(e2)+sum(p2))/2):
            #         print 1
            #     else:
            #         print 2
            #     lis = []
            #     e=[]
            #     p=[]
            #     lis2 = []
            #     e2=[]
            #     p2=[]

            # print np.abs(np.fft.rfft(signal.detrend(coordinates)))
            # freq = np.fft.rfftfreq(len(coordinates))*128
            # y = np.log10(np.fft.rfft(signal.detrend(coordinates)))
            # plt.plot(freq, y)
            # plt.show()
class AverageFFTWindow(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "Average FFT", 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.width = 512
        self.canvas.pack()
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False

    def generator(self):
        count = 1024
        average = [0 for _ in range(count)]
        line = self.canvas.create_line(0,0,0,0)
        j = 0
        while True:
            j += 1
            for i in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                average[i] = (average[i] * (j - 1) + y - 8000) / j
            self.canvas.delete(line)
            line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(average)))*-50+400)])
            self.canvas.update()