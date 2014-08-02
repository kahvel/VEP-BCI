__author__ = 'Anti'
import MyWindows
import Tkinter


class ControlWindow(MyWindows.TkWindow):
    def __init__(self, title, width, height, sensor_names):
        MyWindows.TkWindow.__init__(self, title, width, height)
        self.all_sensor_names = sensor_names
        self.chosen_sensor_names = []

        self.checkbox_values = []
        checkboxframe = Tkinter.Frame(self)
        for i in range(len(self.all_sensor_names)):
            self.checkbox_values.append(Tkinter.IntVar())
            box = Tkinter.Checkbutton(checkboxframe, text=self.all_sensor_names[i], variable=self.checkbox_values[i])
            box.grid(column=i % 7, row=i//7)

        self.options_textboxes = {}
        self.variables = {}
        options_frame = Tkinter.Frame(self)
        self.variables["Norm"] = Tkinter.IntVar()
        norm_checkbox = Tkinter.Checkbutton(options_frame, text="Normalise FFT", variable=self.variables["Norm"])
        norm_checkbox.grid(column=0, row=0, padx=5, pady=5, columnspan=2)
        self.variables["Detrend"] = Tkinter.IntVar()
        detrend_checkbox = Tkinter.Checkbutton(options_frame, text="Detrend signal", variable=self.variables["Detrend"])
        detrend_checkbox.grid(column=2, row=0, padx=5, pady=5, columnspan=2)
        self.variables["Filter"] = Tkinter.IntVar()
        filter_checkbox = Tkinter.Checkbutton(options_frame, text="Filter signal", variable=self.variables["Filter"])
        filter_checkbox.grid(column=4, row=0, padx=5, pady=5, columnspan=2)
        MyWindows.newTextBox(options_frame, "Step:", 0, 1, self.options_textboxes)
        MyWindows.newTextBox(options_frame, "Length:", 2, 1, self.options_textboxes)
        MyWindows.newTextBox(options_frame, "Break:", 4, 1, self.options_textboxes)
        self.variables["Window"] = Tkinter.StringVar()
        self.variables["Window"].set("None")
        window_box = Tkinter.OptionMenu(options_frame, self.variables["Window"], "None", "hanning", "hamming", "blackman",
                                        "kaiser", "bartlett")
        window_box.grid(column=0, row=4, padx=5, pady=5, columnspan=2)
        MyWindows.newTextBox(options_frame, "Arg:", 2, 4, self.options_textboxes)
        self.options_textboxes["Length"].insert(0, 512)
        self.options_textboxes["Step"].insert(0, 8)
        MyWindows.newTextBox(options_frame, "From:", 0, 3, self.options_textboxes)
        MyWindows.newTextBox(options_frame, "To:", 2, 3, self.options_textboxes)
        MyWindows.newTextBox(options_frame, "Taps:", 4, 3, self.options_textboxes)

        self.window_groups = {}
        button_frames = []
        button_groups = {}
        for group_name in self.window_group_names:
            windows = {}
            button_frames.append(Tkinter.Frame(self))
            for window_name in self.window_names:
                windows[window_name] = None
            self.window_groups[group_name] = windows

        for i in range(len(self.window_group_names)):
            buttons = {}
            group_name = self.window_group_names[i]
            for j in range(len(self.window_names)):
                name = self.window_names[j]
                buttons[self.window_names[j]] = Tkinter.Button(button_frames[i],
                                                          text=self.button_names[j]+" "+group_name,
                                                          command=lambda a_name=name, a_file=self.files[i], a_group=self.window_groups[group_name]: self.setWindow(a_name, a_file, a_group))
            button_groups[self.window_group_names[i]] = buttons

        for i in range(len(self.window_group_names)):
            group_name = self.window_group_names[i]
            for j in range(len(self.window_names)):
                name = self.window_names[j]
                button_groups[group_name][name].grid(row=0, column=j % 4,padx=5, pady=5)

        checkboxframe.pack()
        for i in range(len(button_frames)):
            button_frames[i].pack()
        options_frame.pack()

        self.exitFlag = False
        self.protocol("WM_DELETE_WINDOW", self.exit)

    def exit(self):
        self.exitFlag = True

    def setWindow(self, name, file, group):
        group[name] = getattr(file, name)()
        group[name].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(group, name))

    def closeWindow(self, windows, key):
        windows[key].continue_generating = False
        self.closeGenerators(windows[key].generators)
        windows[key].destroy()
        windows[key] = None

    def closeGenerators(self, generators):
        for generator in generators:
            generator.close()

    def recvPacket(self, connection):
        while True:
            self.update()
            if self.to_main.poll():
                message = self.to_main.recv()
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
                result[i].append(float(packet.sensors[self.chosen_sensor_names[i]]["value"]))
        return result

    def getMinMaxAvg(self, channel_count, init_signal):
        min_packet = []
        max_packet = []
        averages = []
        for i in range(channel_count):
            averages.append(float(sum(init_signal[i]))/len(init_signal[i]))
            min_packet.append(min(init_signal[i])-averages[i])
            max_packet.append(max(init_signal[i])-averages[i])
        print averages, min_packet, max_packet, init_signal
        return min_packet, max_packet, averages

    def subtractaverages(self, channel_count, signal, averages):
        for i in range(channel_count):
            for j in range(len(signal[i])):
                signal[i][j] = float(signal[i][j] - averages[i])

    def getInitialSignal(self, init_packets):
        channel_count = len(self.chosen_sensor_names)
        init_signal = self.getSensorValues(channel_count, init_packets)
        min_packet, max_packet, averages = self.getMinMaxAvg(channel_count, init_signal)
        self.subtractaverages(channel_count, init_signal, averages)
        return min_packet, max_packet, averages, init_signal

    def setupWindows(self, min_packet, max_packet, averages, init_signal):
        for group_name in self.window_group_names:
            for name in self.window_names:
                if self.window_groups[group_name][name] is not None:
                    self.reset(self.window_groups[group_name], name, self.chosen_sensor_names)
                    self.window_groups[group_name][name].setInitSignal(min_packet, max_packet, averages, init_signal)

    def getPackets(self, length, array):
        for _ in range(length):
            packet = self.recvPacket(self.to_emotiv)
            if isinstance(packet, basestring):
                return packet
            array.append(packet)

    def start(self):
        init_packets = []
        message = self.getPackets(int(self.options_textboxes["Length"].get()), init_packets)
        if message is not None:
            return message
        self.setSensorNames()
        min_packet, max_packet, averages, init_signal = self.getInitialSignal(init_packets)
        self.setupWindows(min_packet, max_packet, averages, init_signal)
        self.startPacketSending()