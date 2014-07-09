__author__ = 'Anti'

import MyWindows
import Tkinter
import multiprocessing
import SignalWindow
import FFTWindow
import Main


class Window(MyWindows.TkWindow):
    def __init__(self, connection, sensor_names):
        MyWindows.TkWindow.__init__(self, "Plot control", 310, 300)
        self.main_conn = connection
        self.sensor_names = sensor_names

        self.plot_windows = {}
        self.garbage = []

        self.buttons = []
        self.checkbox_values = []
        self.checkbox_values_fft = []

        buttonframe1 = Tkinter.Frame(self)
        buttonframe2 = Tkinter.Frame(self)
        buttonframe3 = Tkinter.Frame(self)
        self.buttons.append(Tkinter.Button(buttonframe1, text="Start", command=lambda: self.start()))
        self.buttons.append(Tkinter.Button(buttonframe1, text="Reset avg signal", command=lambda: self.reset(self.plot_windows["AvgSignal"], self.checkbox_values)))
        self.buttons.append(Tkinter.Button(buttonframe1, text="Reset avg mul signal", command=lambda: self.reset(self.plot_windows["AvgMulSignal"], self.checkbox_values)))
        self.buttons.append(Tkinter.Button(buttonframe1, text="Reset avg FFT", command=lambda: self.reset(self.plot_windows["AvgFFt"], self.checkbox_values_fft)))
        self.buttons.append(Tkinter.Button(buttonframe1, text="Reset avg mul FFT", command=lambda: self.reset(self.plot_windows["AvgMulFFT"], self.checkbox_values_fft)))

        self.buttons.append(Tkinter.Button(buttonframe2, text="Signal", command=lambda: self.plot()))
        self.buttons.append(Tkinter.Button(buttonframe2, text="Avg signal", command=lambda: self.avgPlot()))
        self.buttons.append(Tkinter.Button(buttonframe2, text="Avg mul signals", command=lambda: self.avg()))

        self.buttons.append(Tkinter.Button(buttonframe3, text="FFT", command=lambda: self.fft()))
        self.buttons.append(Tkinter.Button(buttonframe3, text="Avg FFT", command=lambda: self.avgFft()))
        self.buttons.append(Tkinter.Button(buttonframe3, text="Avg mul FFT", command=lambda: self.avgFft2()))

        self.buttons[0].grid(column=0, row=2, padx=5, pady=5)
        for i in range(1, 5):
            self.buttons[i].grid(column=(i-1) % 2, row=(i-1)//2, padx=5, pady=5)
        for i in range(5, 8):
            self.buttons[i].grid(column=i, row=0, padx=5, pady=5)
        for i in range(8, 11):
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

    def reset(self, window, checkbox_values):
        # window.continue_generating = False
        window.canvas.delete("all")
        self.garbage.extend(window.generators)
        window.setup(checkbox_values, self.sensor_names)
        # window.continue_generating = True

    def stop(self):
        self.buttons[0].configure(text="Start", command=lambda: self.start())
        self.emo_conn.send("Stop")
        for key in self.plot_windows:
            self.plot_windows[key].continue_generating = False

    def start(self):
        self.buttons[0].configure(text="Stop", command=lambda: self.stop())
        plot_conn, self.emo_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=Main.runEmotiv, args=(plot_conn,))
        p.start()

        packets = []
        for key in self.plot_windows:
            if isinstance(self.plot_windows[key], SignalWindow.AbstractSignalWindow):
                self.plot_windows[key].setup(self.checkbox_values, self.sensor_names)
                if len(packets) == 0:
                    print("Calculating averages")
                    for _ in range(512):
                        packet = self.emo_conn.recv()
                        packets.append(packet)
                self.plot_windows[key].calculateAverage(packets)
            else:
                self.plot_windows[key].setup(self.checkbox_values_fft, self.sensor_names)

        while True:
            while not self.emo_conn.poll(0.1):
                self.update()
            packet = self.emo_conn.recv()
            for key in self.plot_windows:
                if self.plot_windows[key].continue_generating:
                    self.plot_windows[key].sendPacket(packet)
            stop = True
            for key in self.plot_windows:
                if self.plot_windows[key].continue_generating:
                    stop = False
                    break
            if stop:
                print("Nothing to do!")
                break

        for generator in self.garbage:
            generator.close()
        self.garbage = []

    def plot(self):
        self.plot_windows["Signal"] = SignalWindow.SignalWindow()

    def avg(self):
        self.plot_windows["AvgMulSignal"] = SignalWindow.AverageSignalWindow2()

    def avgFft(self):
        self.plot_windows["AvgFFt"] = FFTWindow.AverageFFTWindow()

    def avgFft2(self):
        self.plot_windows["AvgMulFFT"] = FFTWindow.AverageFFTWindow2()

    def avgPlot(self):
        self.plot_windows["AvgSignal"] = SignalWindow.AverageSignalWindow()

    def fft(self):
        self.plot_windows["FFT"] = FFTWindow.FFTWindow()