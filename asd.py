__author__ = 'Anti'

import MyWindows
import Tkinter
import multiprocessing
import PlotWindow
import FFTWindow
import Main


class Window(MyWindows.TkWindow):
    def __init__(self, connection, sensor_names):
        MyWindows.TkWindow.__init__(self, "Plot control", 310, 300)
        self.main_conn = connection
        self.sensor_names = sensor_names

        self.plot_windows = []
        self.plot_other = []

        self.buttons = []
        self.checkbox_values = []
        self.checkbox_values_fft = []

        buttonframe1 = Tkinter.Frame(self)
        buttonframe2 = Tkinter.Frame(self)
        buttonframe3 = Tkinter.Frame(self)
        self.buttons.append(Tkinter.Button(buttonframe1, text="Start", command=lambda: self.start()))

        self.buttons.append(Tkinter.Button(buttonframe2, text="Plot", command=lambda: self.plot()))
        self.buttons.append(Tkinter.Button(buttonframe2, text="AvgP", command=lambda: self.avgPlot()))
        self.buttons.append(Tkinter.Button(buttonframe2, text="AvgP2", command=lambda: self.avg()))

        self.buttons.append(Tkinter.Button(buttonframe3, text="FFT", command=lambda: self.fft()))
        self.buttons.append(Tkinter.Button(buttonframe3, text="AvgF", command=lambda: self.avgFft()))
        self.buttons.append(Tkinter.Button(buttonframe3, text="AvgF2", command=lambda: self.avgFft2()))

        for i in range(1):
            self.buttons[i].grid(column=i, row=0, padx=5, pady=5)
        for i in range(1, 4):
            self.buttons[i].grid(column=i, row=0, padx=5, pady=5)
        for i in range(4, 7):
            self.buttons[i].grid(column=i, row=0, padx=5, pady=5)

        checkboxframe = Tkinter.Frame(self)
        for i in range(len(self.sensor_names)):
            self.checkbox_values.append(Tkinter.IntVar())
            box = Tkinter.Checkbutton(checkboxframe, text=self.sensor_names[i], variable=self.checkbox_values[i])
            box.grid(column=i % 7, row=i//7)

        checkboxframe_fft = Tkinter.Frame(self)
        for i in range(len(self.sensor_names)):
            self.checkbox_values_fft.append(Tkinter.IntVar())
            box = Tkinter.Checkbutton(checkboxframe_fft, text=self.sensor_names[i], variable=self.checkbox_values_fft[i])
            box.grid(column=i % 7, row=i//7)

        buttonframe2.pack()
        checkboxframe.pack()
        buttonframe3.pack()
        checkboxframe_fft.pack()
        buttonframe1.pack()

        self.mainloop()

    def start(self):
        plot_conn, self.emo_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=Main.runEmotiv, args=(plot_conn,))
        p.start()
        self.stardipoiss()

    def stardipoiss(self):
        packets = []
        for i in range(len(self.plot_other)):
            if isinstance(self.plot_windows[i], PlotWindow.AbstractPlotWindow):
                self.plot_other[i].setSensorNames(self.checkbox_values, self.sensor_names)
                if len(packets) == 0:
                    print("Calculating averages")
                    for _ in range(512):
                        packet = self.emo_conn.recv()
                        packets.append(packet)
                self.plot_other[i].setup(self.plot_windows[i])
                self.plot_other[i].calculateAverage(packets)
            else:
                self.plot_other[i].setSensorNames(self.checkbox_values_fft, self.sensor_names)
                self.plot_other[i].setup(self.plot_windows[i])

        while True:
            packet = self.emo_conn.recv()
            for i in range(len(self.plot_other)):
                self.plot_other[i].sendPacket(packet)
            stop = True
            for i in range(len(self.plot_other)):
                if self.plot_other[i].do == True:
                    stop = False
            if stop:
                print("Nothing to do!")
                break

    def plot(self):
        self.plot_windows.append(PlotWindow.PlotWindow())
        self.plot_other.append(Plot())

    def avg(self):
        self.plot_windows.append(PlotWindow.AveragePlotWindow2())
        self.plot_other.append(AveragePlot())

    def avgFft(self):
        self.plot_windows.append(FFTWindow.AverageFFTWindow())
        self.plot_other.append(Plot())

    def avgFft2(self):
        self.plot_windows.append(FFTWindow.AverageFFTWindow2())
        self.plot_other.append(AveragePlot())

    def avgPlot(self):
        self.plot_windows.append(PlotWindow.AveragePlotWindow())
        self.plot_other.append(Plot())

    def fft(self):
        self.plot_windows.append(FFTWindow.FFTWindow())
        self.plot_other.append(Plot())

    def cleanUpAll(self):
        self.avg_fft.cleanUp()
        self.avg_mul_ffts.cleanUp()
        self.fft.cleanUp()
        self.signal.cleanUp()
        self.avg_signal.cleanUp()
        self.avg_mul_signals.cleanUp()
        self.cleanUp()

class AbstractPlot:
    def __init__(self):
        self.generator = None
        self.window = None
        self.do = False
        self.sensor_names = []
        self.plot_count = 0

    def cleanUp(self):
        if self.window is not None:
            self.do = False
            self.window.destroy()
            self.window = None
            for gen in self.generator:
                while True:
                    try:
                        gen.send(1)
                        print("Send")
                    except:
                        print("Empty")
                        break

    def setSensorNames(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.plot_count += 1
                self.sensor_names.append(sensor_names[i])


class Plot(AbstractPlot):
    def __init__(self):
        AbstractPlot.__init__(self)

    def calculateAverage(self, packets):
        if self.do:
            averages = [0 for _ in range(self.plot_count)]
            for j in range(1, len(packets)+1):
                for i in range(self.plot_count):
                    averages[i] = (averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]) / j
            for i in range(self.plot_count):
                self.generator[i].send(averages[i])
            print(averages)

    def sendPacket(self, packet):
        if self.do:
            for i in range(self.plot_count):
                if not self.generator[i].send(packet.sensors[self.sensor_names[i]]["value"]):
                    self.cleanUp()
                    break

    def setup(self, window):
        if window is not None and window.winfo_exists() == 1:
            self.generator = []
            for i in range(self.plot_count):
                self.generator.append(window.generator(i, self.plot_count))
                self.generator[i].send(None)
            self.window = window
            self.do = True
            window.addGenCleanup()


class AveragePlot(AbstractPlot):
    def __init__(self):
        AbstractPlot.__init__(self)

    def calculateAverage(self, packets):
        if self.do:
            averages = [0 for _ in range(self.plot_count)]
            for j in range(1, len(packets)+1):
                for i in range(self.plot_count):
                    averages[i] = (averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]) / j
            self.generator[0].send(averages)
            print(averages)

    def sendPacket(self, packet):
        if self.do:
            for i in range(self.plot_count):
                if not self.generator[0].send(packet.sensors[self.sensor_names[i]]["value"]):
                    self.cleanUp()
                    break

    def setup(self, window):
        if window is not None and window.winfo_exists() == 1:
            self.generator = []
            self.generator.append(window.generator(self.plot_count))
            self.generator[0].send(None)
            self.window = window
            self.do = True
            window.addGenCleanup()