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
        #self.canvas.configure(xscrollincrement="1")
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

    def exit2(self):
        self.continue_generating = False

    def generator(self):
        count = 16
        x=0
        list = []
        line = self.canvas.create_line(0,0,0,0)
        # lis = []
        # e = []
        # p = []
        # lis2 = []
        # e2 = []
        # p2 = []
        while True:
            for _ in range(count):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                list.append(y)
                x += 1
            if x >= 1024:
                del list[:count]
            self.canvas.delete(line)
            #line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(list)))*-100+400)])
            line = self.canvas.create_line([i for i in enumerate(np.log10(np.abs(np.fft.rfft(signal.detrend(list))))*-100+400)])
            self.canvas.update()

            #print np.fft.rfftfreq(len(list))[81]*128
            # e.append(np.log10(np.abs(signal.detrend(np.fft.rfft(list))))[79])
            # lis.append(np.log10(np.abs(signal.detrend(np.fft.rfft(list))))[80])
            # p.append(np.log10(np.abs(signal.detrend(np.fft.rfft(list))))[81])
            # e2.append(np.log10(np.abs(signal.detrend(np.fft.rfft(list))))[159])
            # lis2.append(np.log10(np.abs(signal.detrend(np.fft.rfft(list))))[160])
            # p2.append(np.log10(np.abs(signal.detrend(np.fft.rfft(list))))[161])
            # if len(lis) == 10:
            #     if sum(lis)/(sum(e)+sum(p))/2 >sum(lis2)/(sum(e2)+sum(p2))/2:
            #         print 1
            #     else:
            #         print 2
            #     lis = []
            #     e=[]
            #     p=[]
            #     lis2 = []
            #     e2=[]
            #     p2=[]

            # print np.abs(signal.detrend(np.fft.rfft(list)))
            # freq = np.fft.rfftfreq(len(list))*128
            # y = np.log10(signal.detrend(np.fft.rfft(list)))
            # plt.plot(freq, y)
            # plt.show()


