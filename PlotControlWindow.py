__author__ = 'Anti'

import MyWindows
import Tkinter
import multiprocessing
import SignalPlot
import FFTPlot
import Main


class Window(MyWindows.TkWindow):
    def __init__(self, connection, sensor_names):
        MyWindows.TkWindow.__init__(self, "Plot control", 310, 300)
        self.main_conn = connection
        self.sensor_names = sensor_names

        self.signal_plot_windows = {}
        self.fft_plot_windows = {}
        self.plot_names = ["MultipleRegular", "MultipleAverage", "SingleAverage"]
        # for key in self.plot_names:
        #     self.signal_plot_windows[key] = None
        #     self.fft_plot_windows[key] = None
        self.garbage = []

        self.other_buttons = {}
        self.fft_buttons = {}
        self.fft_reset_buttons = {}
        self.signal_buttons = {}
        self.signal_reset_buttons = {}
        self.checkbox_values = []
        self.checkbox_values_fft = []

        buttonframe0 = Tkinter.Frame(self)
        buttonframe1 = Tkinter.Frame(self)
        buttonframe2 = Tkinter.Frame(self)
        buttonframe3 = Tkinter.Frame(self)
        self.other_buttons["Start"] = Tkinter.Button(buttonframe0, text="Start", command=lambda: self.start())
        self.signal_reset_buttons["MultipleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg signal", command=lambda: self.reset(self.signal_plot_windows["MultipleAverage"], self.checkbox_values))
        self.signal_reset_buttons["SingleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg mul signal", command=lambda: self.reset(self.signal_plot_windows["SingleAverage"], self.checkbox_values))
        self.fft_reset_buttons["MultipleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg FFT", command=lambda: self.reset(self.fft_plot_windows["MultipleAverage"], self.checkbox_values_fft))
        self.fft_reset_buttons["SingleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg mul FFT", command=lambda: self.reset(self.fft_plot_windows["SingleAverage"], self.checkbox_values_fft))

        self.signal_buttons["MultipleRegular"] = Tkinter.Button(buttonframe2, text="Signal", command=lambda: self.setSignalPlot("MultipleRegular"))
        self.signal_buttons["MultipleAverage"] = Tkinter.Button(buttonframe2, text="Avg signal", command=lambda: self.setSignalPlot("MultipleAverage"))
        self.signal_buttons["SingleAverage"] = Tkinter.Button(buttonframe2, text="Avg mul signals", command=lambda: self.setSignalPlot("SingleAverage"))

        self.fft_buttons["MultipleRegular"] = Tkinter.Button(buttonframe3, text="FFT", command=lambda: self.setFFTPlot("MultipleRegular"))
        self.fft_buttons["MultipleAverage"] = Tkinter.Button(buttonframe3, text="Avg FFT", command=lambda: self.setFFTPlot("MultipleAverage"))
        self.fft_buttons["SingleAverage"] = Tkinter.Button(buttonframe3, text="Avg mul FFT", command=lambda: self.setFFTPlot("SingleAverage"))

        self.other_buttons["Start"].grid(column=0, row=0, padx=5, pady=5)
        for i in range(1, len(self.plot_names)):
            self.signal_reset_buttons[self.plot_names[i]].grid(column=(i-1) % 2, row=(i-1)//2, padx=5, pady=5)
            self.fft_reset_buttons[self.plot_names[i]].grid(column=(i-1) % 2, row=(i-1)//2+1, padx=5, pady=5)
        for i in range(len(self.plot_names)):
            self.signal_buttons[self.plot_names[i]].grid(column=i, row=0, padx=5, pady=5)
            self.fft_buttons[self.plot_names[i]].grid(column=i, row=0, padx=5, pady=5)

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
        buttonframe0.pack()

        self.mainloop()

    def reset(self, window, checkbox_values):
        # window.continue_generating = False
        window.canvas.delete("all")
        self.garbage.extend(window.generators)
        window.setup(checkbox_values, self.sensor_names)
        # window.continue_generating = True

    def stop(self):
        self.other_buttons["Start"].configure(text="Start", command=lambda: self.start())
        self.emo_conn.send("Stop")
        for key in self.signal_plot_windows:
            self.signal_plot_windows[key].continue_generating = False
        for key in self.fft_plot_windows:
            self.fft_plot_windows[key].continue_generating = False

    def start(self):
        self.other_buttons["Start"].configure(text="Stop", command=lambda: self.stop())
        plot_conn, self.emo_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=Main.runEmotiv, args=(plot_conn,))
        p.start()

        packets = []
        for key in self.fft_plot_windows:
            # if self.fft_plot_windows[key] is not None:
            self.fft_plot_windows[key].setup(self.checkbox_values_fft, self.sensor_names)
        for key in self.signal_plot_windows:
            # if self.fft_plot_windows[key] is not None:
            self.signal_plot_windows[key].setup(self.checkbox_values, self.sensor_names)
            if len(packets) == 0:
                print("Calculating averages")
                for _ in range(512):
                    packet = self.emo_conn.recv()
                    packets.append(packet)
            self.signal_plot_windows[key].calculateAverage(packets)

        while True:
            while not self.emo_conn.poll(0.1):
                self.update()
            packet = self.emo_conn.recv()
            for key in self.signal_plot_windows:
                if self.signal_plot_windows[key].continue_generating:
                    self.signal_plot_windows[key].sendPacket(packet)
            for key in self.fft_plot_windows:
                if self.fft_plot_windows[key].continue_generating:
                    self.fft_plot_windows[key].sendPacket(packet)
            stop = True
            for key in self.signal_plot_windows:
                if self.signal_plot_windows[key].continue_generating:
                    stop = False
                    break
            for key in self.fft_plot_windows:
                if self.fft_plot_windows[key].continue_generating:
                    stop = False
                    break
            if stop:
                print("Nothing to do!")
                break

        for generator in self.garbage:
            generator.close()
        self.garbage = []

    def setSignalPlot(self, key):
        self.signal_plot_windows[key] = getattr(SignalPlot, key)()
        self.signal_plot_windows[key].setExitProtocol(self.signal_plot_windows)

    def setFFTPlot(self, key):
        self.fft_plot_windows[key] = getattr(FFTPlot, key)()
        self.fft_plot_windows[key].setExitProtocol(self.fft_plot_windows)