__author__ = 'Anti'
import Tkinter
import MyWindows


def scaleY(y, average, index, plot_count):
    return ((y-average) + index*512 + 512/2) / plot_count


def resetAverage(average):
    for i in range(len(average)):
        if i % 2 == 0:
            average[i] = i/2
        else:
            average[i] = 0
    print("Plot average reset")


class AbstractPlotWindow(MyWindows.ToplevelWindow):
    def __init__(self, title):
        MyWindows.ToplevelWindow.__init__(self, title, 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.protocol("WM_DELETE_WINDOW", self.exit2)
        self.continue_generating = True
        self.canvas.pack()

    def exit2(self):
        self.continue_generating = False


class PlotWindow(AbstractPlotWindow):
    def __init__(self):
        AbstractPlotWindow.__init__(self, "Plot")
        self.canvas.configure(xscrollincrement="1")

    def generator(self, index, plot_count):
        lines = []
        x = 512
        average = yield
        prev = 512, 0
        lines.append(self.canvas.create_line(prev, prev))
        while True:
            coordinates = []
            for i in range(0, 10, 2):  # get 20 values before drawing new line
                for _ in range(2):     # get 2 values before scrolling
                    x += 1
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        return
                    coordinates.append(x)
                    coordinates.append(scaleY(y, average, index, plot_count))
                if index == plot_count-1:
                    self.canvas.xview_scroll(2, Tkinter.UNITS)
                    self.canvas.update()
            lines.append(self.canvas.create_line(prev, coordinates))
            prev = x, coordinates[-1]
            if x > 1024:  # x value starts at 512
                self.canvas.delete(lines[0])
                del lines[0]


class AveragePlotWindow(AbstractPlotWindow):
    def __init__(self):
        AbstractPlotWindow.__init__(self, "Average Plot")

    def resetAverage(self, average):
        resetAverage(average)

    def generator(self, index, plot_count):
        coordinates = [0 for _ in range(1024)]
        self.resetAverage(coordinates)
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        avg = yield
        while True:
            j += 1
            for i in range(1, 1024, 2):  # get 512 values before drawing new line
                y = yield self.continue_generating
                if not self.continue_generating:
                    return
                coordinates[i] = (coordinates[i] * (j - 1) + scaleY(y, avg, index, plot_count)) / j
            self.canvas.delete(line)
            line = self.canvas.create_line(coordinates)
            if index == plot_count-1:
                self.canvas.update()


class AveragePlotWindow2(AbstractPlotWindow):
    def __init__(self):
        AbstractPlotWindow.__init__(self, "Average Plot")

    def resetAverage(self, average):
        resetAverage(average)

    def generator(self, plot_count):
        coordinates = [0 for _ in range(1024)]
        self.resetAverage(coordinates)
        line = self.canvas.create_line(0, 0, 0, 0)
        j = 0
        avg = yield
        while True:
            j += 1
            for i in range(1, 1024, 2):      # get 512 values before drawing
                for l in range(plot_count):  # get value for each channel
                    y = yield self.continue_generating
                    if not self.continue_generating:
                        return
                    coordinates[i] = (coordinates[i] * (j - 1) + scaleY(y, avg[l], 0, 1)) / j
            self.canvas.delete(line)
            line = self.canvas.create_line(coordinates)
            self.canvas.update()