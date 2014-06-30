__author__ = 'Anti'
from Tkinter import *
from MyWindows import *
import time

class Plot(ToplevelWindow):
    def __init__(self, fft_generator):
        ToplevelWindow.__init__(self, "Plot", 500, 500)
        #self.focus()
        self.plot_0 = 100, 250
        self.plot_length_x = 300
        self.plot_length_y = 200
        self.mark_length = 5
        self.canvas = Canvas(self, width=500, height=500)
        self.fft_generator = fft_generator
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True

        # self.scrollbar = Scrollbar(self.window, orient=HORIZONTAL)
        # self.scrollbar.pack(side=BOTTOM, fill=X)
        # self.scrollbar.config(command=self.canvas.xview)
        # self.canvas.config(xscrollcommand=self.scrollbar.set)
        self.canvas.pack()
        #self.initElements()
        self.canvas.configure(xscrollincrement="1")
        #self.focus()

    def exit2(self):
        self.continue_generating = False

    def setGenerator(self, generator):
        self.generator = generator

    # def initElements(self):
    #     self.canvas.create_line(self.plot_0, (self.plot_length_x+self.plot_0[0], self.plot_0[1]), width=2)
    #     self.canvas.create_line(self.plot_0, (self.plot_0[0], self.plot_0[1]-self.plot_length_y), width=2)
    #
    #     for i in range(11):
    #         x = self.plot_0[0] + (i * 30)
    #         self.canvas.create_line(x, self.plot_0[1], x, self.plot_0[1]-self.mark_length, width=2)
    #         self.canvas.create_text(x, self.plot_0[1]+self.mark_length, text='%d'% (10*i), anchor=N)
    #
    #     for i in range(6):
    #         y = self.plot_0[1] - (i * 40)
    #         self.canvas.create_line(self.plot_0[0], y, self.plot_0[0]+self.mark_length, y, width=2)
    #         self.canvas.create_text(self.plot_0[0]-self.mark_length, y, text='%d'% (50*i), anchor=E)

    def test7(self, index, start):
        prev = 500, 0
        count = 10
        lines = []
        x = 500
        lines.append(self.canvas.create_line(prev, prev))
        while x <= 500*2:
            list = []
            for i in range(count):
                for _ in range(2):
                    x += 1
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        break
                    list.append(x)
                    list.append(y/8192.0*start+index)

            lines.append(self.canvas.create_line(prev, list))
            prev = x, list[-1]

        while True:
            list = []
            for i in range(count):
                for _ in range(2):
                    x += 1
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        break
                    list.append(x)
                    list.append(y/8192.0*start+index)
            lines.append(self.canvas.create_line(prev, list))
            prev = x, list[-1]
            self.canvas.delete(lines[0])
            del lines[0]

    def test8(self, index, start):
        prev = 500, 0
        count = 10
        lines = []
        x = 500
        lines.append(self.canvas.create_line(prev, prev))
        while x <= 500*2:
            list = []
            for _ in range(count):
                for _ in range(2):
                    x += 1
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        break
                    list.append(x)
                    list.append(y/8192.0*start+index)
                self.canvas.xview_scroll(2, UNITS)
                self.canvas.update()
            lines.append(self.canvas.create_line(prev, list))
            prev = x, list[-1]

        while True:
            list = []
            for i in range(count):
                for _ in range(2):
                    x += 1
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        break
                    list.append(x)
                    list.append(y/8192.0*start+index)
                self.canvas.xview_scroll(2, UNITS)
                self.canvas.update()

            lines.append(self.canvas.create_line(prev, list))
            prev = x, list[-1]
            self.canvas.delete(lines[0])
            del lines[0]
        # prev = self.width, 0
        # packet = prev[1]
        # lines = []
        #
        # while prev[0]<=self.width+100:
        #     lines.append(self.canvas.create_line(prev, prev[0]+2, packet))
        #     #self.canvas.create_line(prev, prev[0]+2, packet)
        #     prev = prev[0]+2, packet
        #     packet = yield
        #     packet -= 8200
        #     self.canvas.update()
        #     self.canvas.xview_scroll(1, UNITS)
        # while True:
        #     lines.append(self.canvas.create_line(prev, prev[0]+2, packet))
        #     #self.canvas.create_line(prev, prev[0]+2, packet)
        #     prev = prev[0]+2, packet
        #     packet = yield
        #     packet -= 8200
        #     self.canvas.update()
        #     self.canvas.delete(lines[0])
        #     del lines[0]
        #     self.canvas.xview_scroll(1, UNITS)

