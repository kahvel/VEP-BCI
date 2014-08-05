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

    def recvPacket(self):
        while True:
            self.update()
            if self.connection.poll():
                message = self.connection.recv()
                return message
            if self.exitFlag:
                return "Exit"

    def setSensorNames(self):
        self.chosen_sensor_names = []
        for i in range(len(self.checkbox_values)):
            if self.checkbox_values[i].get() == 1:
                self.chosen_sensor_names.append(self.all_sensor_names[i])
        if len(self.chosen_sensor_names) == 0:
            print "No channels chosen"

    def setupWindows(self):
        for group_name in self.window_group_names:
            for name in self.window_names:
                if self.window_groups[group_name][name] is not None:
                    self.reset(self.window_groups[group_name], name, self.chosen_sensor_names)

    def start(self):
        self.setSensorNames()
        self.setupWindows()
        self.startPacketSending()