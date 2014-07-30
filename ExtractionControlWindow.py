__author__ = 'Anti'
import MyWindows
import Tkinter
import SNRExtraction


class Window(MyWindows.TkWindow):
    def __init__(self, ps_to_main, ps_to_emo, sensor_names, detection_to_targets):
        MyWindows.TkWindow.__init__(self, "Target Extraction", 320, 320)
        self.ps_to_emo = ps_to_emo
        self.ps_to_main = ps_to_main
        self.all_sensor_names = sensor_names
        self.detection_to_targets = detection_to_targets

        self.buttons = {}
        self.windows = {}
        self.checkbox_values = []
        self.button_names = ["SNR", "SNR2"]
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

        buttonframe = Tkinter.Frame(self)
        self.buttons["SNR"] = Tkinter.Button(buttonframe, text="SNR", command=lambda: self.set("SNR"))
        self.buttons["SNR2"] = Tkinter.Button(buttonframe, text="SNR2", command=lambda: self.set("SNR2"))
        for i in range(len(self.button_names)):
            self.buttons[self.button_names[i]].grid(column=i % 4, row=i//4, padx=5, pady=5)

        checkboxframe.pack()
        buttonframe.pack()
        self.options_frame.pack()
        self.exitFlag = False
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.myMainloop()

    def set(self, key):
        self.windows[key] = getattr(SNRExtraction, key)()
        self.windows[key].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(self.windows, key))

    def closeGenerators(self, generators):
        for generator in generators:
            generator.close()

    def closeWindow(self, windows, key):
        windows[key].continue_generating = False
        self.closeGenerators(windows[key].generators)
        windows[key].destroy()
        windows[key] = None

    def exit(self):
        self.exitFlag = True

    def myMainloop(self):
        while True:
            message = self.recvPacket(self.ps_to_main)
            if message == "Start":
                print "Starting extraction"
                self.freq_points = self.ps_to_main.recv()
                while self.ps_to_emo.poll():
                    print self.ps_to_emo.recv()
                message = self.start()
            if message == "Stop":
                print "Extraction stopped"
            if message == "Exit":
                print "Exiting extraction"
                break

    def recvPacket(self, connection):
        while True:
            self.update()
            if self.ps_to_main.poll():
                message = self.ps_to_main.recv()
                return message
            if self.exitFlag:
                return "Exit"
            if connection.poll(0.1):
                return connection.recv()

    def reset(self, windows, key, sensor_names):
        window = windows[key]
        if window is not None:
            window.canvas.insert(Tkinter.END, "Starting\n")
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options_textboxes, self.variables, sensor_names, self.freq_points)

    def start(self):
        channel_count = 0
        self.chosen_sensor_names = []
        for i in range(len(self.checkbox_values)):
            if self.checkbox_values[i].get() == 1:
                self.chosen_sensor_names.append(self.all_sensor_names[i])
                channel_count += 1
        if channel_count == 0:
            print "No channels chosen"

        min_packet = []
        max_packet = []
        averages = []
        initial_packets = [[] for _ in range(channel_count)]
        for _ in range(int(self.options_textboxes["Length"].get())):
            packet = self.recvPacket(self.ps_to_emo)
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

        for key in self.windows:
            if self.windows[key] is not None:
                self.reset(self.windows, key, self.chosen_sensor_names)
                self.windows[key].setInitSignal(min_packet, max_packet, averages, initial_packets)

        while True:
            packet = self.recvPacket(self.ps_to_emo)
            if isinstance(packet, basestring):
                return packet
            for key in self.windows:
                if self.windows[key] is not None:
                    if self.windows[key].continue_generating:
                        e = self.windows[key].sendPacket(packet)
                        if e is not None:
                            self.detection_to_targets.send(e)


