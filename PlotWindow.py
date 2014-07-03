__author__ = 'Anti'
import Tkinter
import MyWindows


class PlotWindow(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "Plot", 512, 512)
        # self.plot_0 = 100, 250
        # self.plot_length_x = 300
        # self.plot_length_y = 200
        # self.mark_length = 5
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True
        # self.scrollbar = Scrollbar(self.window, orient=HORIZONTAL)
        # self.scrollbar.pack(side=BOTTOM, fill=X)
        # self.scrollbar.config(command=self.canvas.xview)
        # self.canvas.config(xscrollcommand=self.scrollbar.set)
        self.canvas.pack()
        #self.initElements()
        self.canvas.configure(xscrollincrement="1")

    def exit2(self):
        self.continue_generating = False

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

    def generator(self, index, height, plot_count):
        prev = 512, 0
        count = 10
        lines = []
        x = 512
        lines.append(self.canvas.create_line(prev, prev))
        average = yield
        while True:
            list = []
            for i in range(count):
                for _ in range(2):
                    x += 1
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        break
                    list.append(x)
                    # list.append(y-8000)
                    # list.append(y/8192.0*height*2+index*height)
                    list.append(scaleY(y, average, index, height, plot_count))
                if index == plot_count-1:
                    self.canvas.xview_scroll(2, Tkinter.UNITS)
                    self.canvas.update()
            lines.append(self.canvas.create_line(prev, list))
            prev = x, list[-1]
            if x > 512*2:
                self.canvas.delete(lines[0])
                del lines[0]


def scaleY(y, average, index, height, plot_count):
    return (y-average)/(plot_count)+index*height+height/2


class AveragePlotWindow(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "Average Plot", 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True
        self.canvas.pack()
        self.canvas.configure(xscrollincrement="1")

    def exit2(self):
        self.continue_generating = False

    def resetAverage(self, average):
        print("Plot average reset")
        for i in range(1024):
            if i % 2 == 0:
                average.append(i/2)
            else:
                average.append(0)

    def generator(self, index, height, plot_count):
        count = 512
        average = []
        self.resetAverage(average)
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        avg = yield
        while True:
            j += 1
            for i in range(1, count*2, 2):
                y = yield self.continue_generating
                if not self.continue_generating:
                    break
                average[i] = (average[i] * (j - 1) + scaleY(y, avg, index, height, plot_count)) / j
            self.canvas.delete(line)
            #print(average)
            line = self.canvas.create_line(average)
            if index == plot_count-1:
                self.canvas.update()

class AveragePlotWindow2(MyWindows.ToplevelWindow):
    def __init__(self):
        MyWindows.ToplevelWindow.__init__(self, "Average Plot", 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True
        self.canvas.pack()
        self.canvas.configure(xscrollincrement="1")

    def exit2(self):
        self.continue_generating = False

    def resetAverage(self, average):
        print("Plot average reset")
        for i in range(1024):
            if i % 2 == 0:
                average.append(i/2)
            else:
                average.append(0)

    def generator(self, index, height, plot_count):
        count = 512
        average = []
        self.resetAverage(average)
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        avg = yield
        while True:
            j += 1
            for i in range(1, count*2, 2):
                for l in range(plot_count):
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        break
                    average[i] = (average[i] * (j - 1) + scaleY(y, avg[l], index, height, 1)) / j
            self.canvas.delete(line)
            #print(average)
            line = self.canvas.create_line(average)
            #if index == plot_count-1:
            self.canvas.update()