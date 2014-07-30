__author__ = 'Anti'

import MyWindows
import Tkinter
import SignalPlot
import FFTPlot


class Window(MyWindows.TkWindow):
    def __init__(self, plot_to_main, plot_to_emo, sensor_names):
        MyWindows.TkWindow.__init__(self, "Plot control", 320, 370)
        self.plot_to_main = plot_to_main
        self.plot_to_emo = plot_to_emo
        self.all_sensor_names = sensor_names
        self.chosen_sensor_names = []

        self.signal_plot_windows = {}
        self.fft_plot_windows = {}
        self.plot_names = ["MultipleAverage", "SingleAverage", "MultipleRegular", "SingleRegular"]
        for key in self.plot_names:
            self.signal_plot_windows[key] = None
            self.fft_plot_windows[key] = None

        self.other_buttons = {}
        self.fft_buttons = {}
        self.fft_reset_buttons = {}
        self.signal_buttons = {}
        self.signal_reset_buttons = {}
        self.checkbox_values = []

        buttonframe1 = Tkinter.Frame(self)
        buttonframe2 = Tkinter.Frame(self)
        buttonframe3 = Tkinter.Frame(self)

        self.signal_reset_buttons["MultipleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg signal", command=lambda: self.reset(self.signal_plot_windows, "MultipleAverage", self.chosen_sensor_names))
        self.signal_reset_buttons["SingleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg mul signal", command=lambda: self.reset(self.signal_plot_windows, "SingleAverage", self.chosen_sensor_names))
        self.fft_reset_buttons["MultipleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg FFT", command=lambda: self.reset(self.fft_plot_windows, "MultipleAverage", self.chosen_sensor_names))
        self.fft_reset_buttons["SingleAverage"] = Tkinter.Button(buttonframe1, text="Reset avg mul FFT", command=lambda: self.reset(self.fft_plot_windows, "SingleAverage", self.chosen_sensor_names))

        self.signal_buttons["MultipleRegular"] = Tkinter.Button(buttonframe2, text="Signal", command=lambda: self.setSignalPlot("MultipleRegular"))
        self.signal_buttons["SingleRegular"] = Tkinter.Button(buttonframe2, text="Mul signal", command=lambda: self.setSignalPlot("SingleRegular"))
        self.signal_buttons["MultipleAverage"] = Tkinter.Button(buttonframe2, text="Avg signal", command=lambda: self.setSignalPlot("MultipleAverage"))
        self.signal_buttons["SingleAverage"] = Tkinter.Button(buttonframe2, text="Avg mul signal", command=lambda: self.setSignalPlot("SingleAverage"))
        # self.signal_buttons["CCARegular"] = Tkinter.Button(buttonframe2, text="CCA signal", command=lambda: self.setSignalPlot("CCARegular"))

        self.fft_buttons["MultipleRegular"] = Tkinter.Button(buttonframe3, text="FFT", command=lambda: self.setFFTPlot("MultipleRegular"))
        self.fft_buttons["SingleRegular"] = Tkinter.Button(buttonframe3, text="Mul FFT", command=lambda: self.setFFTPlot("SingleRegular"))
        self.fft_buttons["MultipleAverage"] = Tkinter.Button(buttonframe3, text="Avg FFT", command=lambda: self.setFFTPlot("MultipleAverage"))
        self.fft_buttons["SingleAverage"] = Tkinter.Button(buttonframe3, text="Avg mul FFT", command=lambda: self.setFFTPlot("SingleAverage"))
        # self.fft_buttons["CCARegular"] = Tkinter.Button(buttonframe3, text="CCA FFT", command=lambda: self.setFFTPlot("CCARegular"))

        for i in range(2):
            self.signal_reset_buttons[self.plot_names[i]].grid(column=i % 2, row=i//2, padx=5, pady=5)
            self.fft_reset_buttons[self.plot_names[i]].grid(column=i % 2, row=i//2+1, padx=5, pady=5)
        for i in range(len(self.plot_names)):
            self.signal_buttons[self.plot_names[i]].grid(column=i % 4, row=i//4, padx=5, pady=5)
            self.fft_buttons[self.plot_names[i]].grid(column=i % 4, row=i//4, padx=5, pady=5)

        checkboxframe = Tkinter.Frame(self)
        for i in range(len(self.all_sensor_names)):
            self.checkbox_values.append(Tkinter.IntVar())
            box = Tkinter.Checkbutton(checkboxframe, text=self.all_sensor_names[i], variable=self.checkbox_values[i])
            box.grid(column=i % 7, row=i//7)

        self.options_textboxes = {}
        self.variables = {}
        self.options_frame = Tkinter.Frame(self)
        self.variables["Norm"] = Tkinter.IntVar()
        norm_checkbox = Tkinter.Checkbutton(self.options_frame, text="Normalise FFT", variable=self.variables["Norm"])
        norm_checkbox.grid(column=0, row=0, padx=5, pady=5, columnspan=2)
        MyWindows.newTextBox(self.options_frame, "Step:", 0, 1, self.options_textboxes)
        MyWindows.newTextBox(self.options_frame, "Length:", 2, 1, self.options_textboxes)
        self.variables["Window"] = Tkinter.StringVar()
        self.variables["Window"].set("None")
        window_box = Tkinter.OptionMenu(self.options_frame, self.variables["Window"], "None", "hanning", "hamming", "blackman",
                                        "kaiser", "bartlett")
        window_box.grid(column=0, row=4, padx=5, pady=5, columnspan=2)
        MyWindows.newTextBox(self.options_frame, "Arg:", 2, 4, self.options_textboxes)
        self.options_textboxes["Length"].insert(0, 512)
        self.options_textboxes["Step"].insert(0, 8)
        self.variables["Filter"] = Tkinter.IntVar()
        filter_checkbox = Tkinter.Checkbutton(self.options_frame, text="Filter", variable=self.variables["Filter"])
        filter_checkbox.grid(column=0, row=2, padx=5, pady=5)
        MyWindows.newTextBox(self.options_frame, "From:", 0, 3, self.options_textboxes)
        MyWindows.newTextBox(self.options_frame, "To:", 2, 3, self.options_textboxes)
        MyWindows.newTextBox(self.options_frame, "Taps:", 4, 3, self.options_textboxes)

        buttonframe2.pack()
        checkboxframe.pack()
        buttonframe3.pack()
        self.options_frame.pack()
        buttonframe1.pack()

        self.exitFlag = False
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.myMainloop()

    # def windowChange(self, val):
    #     if val == "kaiser":

    def exit(self):
        self.exitFlag = True

    def myMainloop(self):
        while True:
            message = self.recvPacket(self.plot_to_main)
            if message == "Start":
                print "Starting plot"
                message = self.start()
                while self.plot_to_emo.poll():
                    print self.plot_to_emo.recv()
            if message == "Stop":
                print "Plot stopped"
            if message == "Exit":
                print "Exiting plot"
                break

        self.plot_to_emo.send("Close")
        self.plot_to_emo.close()
        self.plot_to_main.send("Close")
        self.plot_to_main.close()
        self.destroy()

    def closeGenerators(self, generators):
        for generator in generators:
            generator.close()

    def closeWindow(self, windows, key):
        windows[key].continue_generating = False
        self.closeGenerators(windows[key].generators)
        windows[key].destroy()
        windows[key] = None

    def reset(self, windows, key, sensor_names):
        window = windows[key]
        if window is not None:
            window.canvas.delete("all")
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options_textboxes, self.variables, sensor_names)

    def recvPacket(self, connection):
        while True:
            self.update()
            if self.plot_to_main.poll():
                message = self.plot_to_main.recv()
                return message
            if self.exitFlag:
                return "Exit"
            if connection.poll(0.1):
                return connection.recv()

    def setSensorNames(self):
        self.chosen_sensor_names = []
        for i in range(len(self.checkbox_values)):
            if self.checkbox_values[i].get() == 1:
                self.chosen_sensor_names.append(self.all_sensor_names[i])
        if len(self.chosen_sensor_names) == 0:
            print "No channels chosen"

    def getSensorValues(self, channel_count, packets):
        result = [[] for _ in range(channel_count)]
        for i in range(channel_count):
            for packet in packets:
                result[i].append(packet.sensors[self.chosen_sensor_names[i]]["value"])
        return result

    def getMinMaxAvg(self, channel_count, init_signal):
        min_packet = []
        max_packet = []
        averages = []
        for i in range(channel_count):
            averages.append(sum(init_signal[i])/len(init_signal[i]))
            min_packet.append(min(init_signal[i])-averages[i])
            max_packet.append(max(init_signal[i])-averages[i])
        print averages, min_packet, max_packet, init_signal
        return min_packet, max_packet, averages

    def subtractaverages(self, channel_count, signal, averages):
        for i in range(channel_count):
            for j in range(len(signal[i])):
                signal[i][j] -= averages[i]

    def getInitialSignal(self, prev_packets, init_packets):
        channel_count = len(self.chosen_sensor_names)
        prev_signal = self.getSensorValues(channel_count, prev_packets)
        init_signal = self.getSensorValues(channel_count, init_packets)
        min_packet, max_packet, averages = self.getMinMaxAvg(channel_count, init_signal)
        self.subtractaverages(channel_count, init_signal, averages)
        self.subtractaverages(channel_count, prev_signal, averages)
        return min_packet, max_packet, averages, init_signal, prev_signal

    def setupPlotWindows(self, min_packet, max_packet, averages, init_signal, prev_signal):
        for key in self.fft_plot_windows:
            if self.fft_plot_windows[key] is not None:
                self.reset(self.fft_plot_windows, key, self.chosen_sensor_names)
                self.fft_plot_windows[key].setInitSignal(min_packet, max_packet, averages, init_signal, prev_signal)
                for i in range(0, 512, 40):  # scale for fft
                    self.fft_plot_windows[key].canvas.create_line(i, 0, i, 512, fill="red")
                    self.fft_plot_windows[key].canvas.create_text(i, 10, text=i/8)
        for key in self.signal_plot_windows:
            if self.signal_plot_windows[key] is not None:
                self.reset(self.signal_plot_windows, key, self.chosen_sensor_names)
                self.signal_plot_windows[key].setInitSignal(min_packet, max_packet, averages, init_signal)

    def startPacketSending(self):
        while True:
            packet = self.recvPacket(self.plot_to_emo)
            if isinstance(packet, basestring):
                return packet
            for key in self.signal_plot_windows:
                if self.signal_plot_windows[key] is not None:
                    if self.signal_plot_windows[key].continue_generating:
                        self.signal_plot_windows[key].sendPacket(packet)
            for key in self.fft_plot_windows:
                if self.fft_plot_windows[key] is not None:
                    if self.fft_plot_windows[key].continue_generating:
                        self.fft_plot_windows[key].sendPacket(packet)

    def getPackets(self, length, array):
        for _ in range(length):
            packet = self.recvPacket(self.plot_to_emo)
            if isinstance(packet, basestring):
                return packet
            array.append(packet)

    def start(self):
        init_packets = []
        prev_packets = []
        message = self.getPackets(100, prev_packets)
        if message is not None:
            return message
        message = self.getPackets(int(self.options_textboxes["Length"].get()), init_packets)
        if message is not None:
            return message
        self.setSensorNames()
        min_packet, max_packet, averages, init_signal, prev_signal = self.getInitialSignal(prev_packets, init_packets)
        self.setupPlotWindows(min_packet, max_packet, averages, init_signal, prev_signal)
        self.startPacketSending()

    def setSignalPlot(self, key):
        self.signal_plot_windows[key] = getattr(SignalPlot, key)()
        self.signal_plot_windows[key].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(self.signal_plot_windows, key))

    def setFFTPlot(self, key):
        self.fft_plot_windows[key] = getattr(FFTPlot, key)()
        self.fft_plot_windows[key].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(self.fft_plot_windows, key))