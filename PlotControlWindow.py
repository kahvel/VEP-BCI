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
        self.garbage = []

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
        MyWindows.newTextBox(self.options_frame, "Beta:", 2, 4, self.options_textboxes)
        self.options_textboxes["Length"].insert(0, 512)
        self.options_textboxes["Step"].insert(0, 8)
        self.variables["Filter"] = Tkinter.IntVar()
        filter_checkbox = Tkinter.Checkbutton(self.options_frame, text="Filter", variable=self.variables["Filter"])
        filter_checkbox.grid(column=0, row=2, padx=5, pady=5)
        MyWindows.newTextBox(self.options_frame, "Low:", 0, 3, self.options_textboxes)
        MyWindows.newTextBox(self.options_frame, "High:", 2, 3, self.options_textboxes)
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
                # for generator in self.garbage:
                #     generator.close()
                # self.garbage = []
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
        # self.garbage.extend(windows[key].generators)
        self.closeGenerators(windows[key].generators)
        windows[key].destroy()
        windows[key] = None

    def reset(self, windows, key, sensor_names):
        window = windows[key]
        if window is not None:
            window.canvas.delete("all")
            # self.garbage.extend(window.generators)
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

    def start(self):
        channel_count = 0
        self.chosen_sensor_names = []
        for i in range(len(self.checkbox_values)):
            if self.checkbox_values[i].get() == 1:
                self.chosen_sensor_names.append(self.all_sensor_names[i])
                channel_count += 1
        if channel_count == 0:
            print "No channels chosen"
            return "Stop"

        min_packet = []
        max_packet = []
        averages = []
        initial_packets = [[] for _ in range(channel_count)]
        for _ in range(int(self.options_textboxes["Length"].get())):
            packet = self.recvPacket(self.plot_to_emo)
            if isinstance(packet, basestring):
                return packet
            for j in range(channel_count):
                initial_packets[j].append(packet.sensors[self.chosen_sensor_names[j]]["value"])
        for i in range(channel_count):
            averages.append(sum(initial_packets[i])/len(initial_packets[i]))
            min_packet.append(min(initial_packets[i])-averages[i])
            max_packet.append(max(initial_packets[i])-averages[i])
        for i in range(channel_count):
            for j in range(len(initial_packets[i])):
                initial_packets[i][j] -= averages[i]
        print averages, min_packet, max_packet, initial_packets

        for key in self.fft_plot_windows:
            if self.fft_plot_windows[key] is not None:
                self.reset(self.fft_plot_windows, key, self.chosen_sensor_names)
                self.fft_plot_windows[key].setInitSignal(min_packet, max_packet, averages, initial_packets)
                for i in range(0, 512, 40):  # scale for fft
                    self.fft_plot_windows[key].canvas.create_line(i, 0, i, 512, fill="red")
                    self.fft_plot_windows[key].canvas.create_text(i, 10, text=i/8)
        for key in self.signal_plot_windows:
            if self.signal_plot_windows[key] is not None:
                self.reset(self.signal_plot_windows, key, self.chosen_sensor_names)
                self.signal_plot_windows[key].setInitSignal(min_packet, max_packet, averages, initial_packets)

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

    def setSignalPlot(self, key):
        self.signal_plot_windows[key] = getattr(SignalPlot, key)()
        self.signal_plot_windows[key].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(self.signal_plot_windows, key))

    def setFFTPlot(self, key):
        self.fft_plot_windows[key] = getattr(FFTPlot, key)()
        self.fft_plot_windows[key].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(self.fft_plot_windows, key))