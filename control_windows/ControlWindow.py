__author__ = 'Anti'

from main_window import MyWindows
import Tkinter
import numpy as np
import scipy.signal


class ControlWindow(MyWindows.TkWindow):
    def __init__(self, title, width, height, sensor_names):
        MyWindows.TkWindow.__init__(self, title, width, height)
        self.name = title
        self.all_sensor_names = sensor_names
        self.chosen_sensor_names = []
        self.headset_freq = 128
        self.filter_coefficients = None
        self.window_function = None

        self.checkbox_values = []
        checkboxframe = Tkinter.Frame(self)
        for i in range(len(self.all_sensor_names)):
            self.checkbox_values.append(Tkinter.IntVar())
            box = Tkinter.Checkbutton(checkboxframe, text=self.all_sensor_names[i], variable=self.checkbox_values[i])
            box.grid(column=i % 7, row=i//7)

        self.options_textboxes = {}
        self.variables = {}
        self.options = {}
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

    def myMainloop(self):
        while True:
            message = self.recvPacket()
            if message == "Start":
                print "Starting", self.name
                message = self.start()
                if message == "Stop":
                    print "Stopping", self.name
            if message == "Exit" or self.exitFlag:
                print "Exiting", self.name
                break
        self.connection.send("Close")
        self.connection.close()
        self.destroy()

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

    def reset(self, windows, key, sensor_names):
        window = windows[key]
        if window is not None:
            window.resetCanvas()
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options, sensor_names, self.window_function, self.filter_coefficients)

    def start(self):
        self.setSensorNames()
        self.setOptions(self.options_textboxes, self.variables)
        self.setupWindows()
        return self.startPacketSending()

    def startPacketSending(self):
        while True:
            packet = self.recvPacket()
            if isinstance(packet, basestring):
                return packet
            for group_name in self.window_group_names:
                for name in self.window_names:
                    window = self.window_groups[group_name][name]
                    if window is not None:
                        if window.continue_generating:
                            window.sendPacket(packet, window.generators, self.chosen_sensor_names)

    def setWindowFunction(self, options_textboxes, variables):
        window_var = variables["Window"].get()
        if window_var == "None":
            self.options["Window"] = False
            self.window_function = None
        else:
            self.options["Window"] = True
            if window_var == "hanning":
                self.window_function = np.hanning(self.options["Length"])
            elif window_var == "hamming":
                self.window_function = np.hamming(self.options["Length"])
            elif window_var == "blackman":
                self.window_function = np.blackman(self.options["Length"])
            elif window_var == "kaiser":
                self.window_function = np.kaiser(self.options["Length"], float(options_textboxes["Arg"].get()))
            elif window_var == "bartlett":
                self.window_function = np.bartlett(self.options["Length"])

    def setFilter(self, options_textboxes, variables):
        if variables["Filter"].get() == 1:
            self.options["Filter"] = True
            to_value = options_textboxes["To"].get()
            from_value = options_textboxes["From"].get()
            num_taps = int(options_textboxes["Taps"].get())
            nyq = self.headset_freq/2.0
            if from_value != "" and to_value != "":
                to_value = float(to_value)
                from_value = float(from_value)
                self.filter_coefficients = scipy.signal.firwin(num_taps, [from_value/nyq, to_value/nyq], pass_zero=False)
            elif to_value != "":
                to_value = float(to_value)
                self.filter_coefficients = scipy.signal.firwin(num_taps, to_value/nyq)
            elif from_value != "":
                from_value = float(from_value)
                self.filter_coefficients = scipy.signal.firwin(num_taps, from_value/nyq, pass_zero=False)
            else:
                print "Insert from and/or to value"
                self.options["Filter"] = False
                self.filter_coefficients = None
        else:
            self.options["Filter"] = False
            self.filter_coefficients = None

    def setNormalisation(self, variables):
        if variables["Norm"].get() == 1:
            self.options["Normalise"] = True
        else:
            self.options["Normalise"] = False

    def setDetrend(self, options_textboxes, variables):
        if variables["Detrend"].get() == 1:
            self.options["Detrend"] = True
            breakpoints = options_textboxes["Break"].get()
            if breakpoints == "" or breakpoints == "0":
                self.options["Breakpoints"] = 0
            else:
                breakpoints_list = []
                breakpoints = int(breakpoints)
                for i in range(breakpoints):
                    breakpoints_list.append(self.options["Step"]/breakpoints*(i+1))
                self.options["Breakpoints"] = breakpoints_list
        else:
            self.options["Detrend"] = False

    def setOptions(self, options_textboxes, variables):
        self.options["Length"] = int(options_textboxes["Length"].get())
        self.options["Step"] = int(options_textboxes["Step"].get())
        self.setWindowFunction(options_textboxes, variables)
        self.setFilter(options_textboxes, variables)
        self.setNormalisation(variables)
        self.setDetrend(options_textboxes, variables)