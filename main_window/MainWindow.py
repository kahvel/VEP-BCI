__author__ = 'Anti'

from main_window import MyWindows, ColorWindow
import Tkinter
import tkFileDialog
import multiprocessing
import multiprocessing.reduction
import Main
import win32api
import win32con


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "Main Menu", 310, 500)
        self.sensor_names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
        self.start_button = None
        self.start_button2 = None
        self.target_textboxes = {}
        self.background_textboxes = {}
        self.checkbox_values = []
        self.checkbox_values_fft = []
        self.targets = []
        self.initial_target = {"Height": 150,
                               "Width": 150,
                               "x": 0,
                               "y": 0,
                               "Freq": 10.0,
                               "Color1": "#ffffff",
                               "Color2": "#777777",
                               "Disable": 1}
        self.neutral_signal = None
        self.target_signal = [None for _ in range(6)]
        self.disable_checkbox_var = Tkinter.IntVar()
        # self.n_targets = 6
        for _ in range(7):
            self.targets.append(self.initial_target.copy())
        self.targets[0]["Disable"] = self.targets[1]["Disable"] = 0
        self.target_color_buttons = {}
        self.background_color_buttons = {}
        self.current_radio_button = Tkinter.IntVar()
        self.previous_radio_button = 0
        self.monitor_names = [win32api.GetMonitorInfo(monitor[0])["Device"] for monitor in win32api.EnumDisplayMonitors()]
        self.current_monitor = Tkinter.StringVar(value=self.monitor_names[0])
        self.initElements()
        self.connection, post_office_to_main = multiprocessing.Pipe()
        multiprocessing.Process(target=Main.runPostOffice, args=(post_office_to_main,)).start()
        self.lock = multiprocessing.Lock()
        self.newProcess(Main.runEmotiv, "Add emotiv", self.lock)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.mainloop()

    def initTitleFrame(self, title):
        frame = Tkinter.Frame(self)
        Tkinter.Label(frame, text=title).grid(column=0, row=0, padx=5, pady=5)
        return frame

    def initWindowFrame(self):
        window_frame = Tkinter.Frame(self)
        MyWindows.newTextBox(window_frame, "Width:", 0, 0, self.background_textboxes)
        MyWindows.newTextBox(window_frame, "Height:", 2, 0, self.background_textboxes)
        MyWindows.newColorButton(4, 0, self.backgroundColor, window_frame,
                                 "Color", self.background_textboxes, self.background_color_buttons)
        MyWindows.newTextBox(window_frame, "Freq:", 2, 1, self.background_textboxes)
        Tkinter.OptionMenu(window_frame, self.current_monitor, *self.monitor_names,
                           command=lambda a:
                           self.changeMonitor(a, self.background_textboxes["Freq"])).grid(row=1, column=0, columnspan=2)
        self.changeMonitor(self.monitor_names[0], self.background_textboxes["Freq"])
        self.background_textboxes["Width"].insert(0, 800)
        self.background_textboxes["Height"].insert(0, 600)
        self.background_textboxes["Color"].insert(0, "#000000")
        MyWindows.changeButtonColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])
        return window_frame

    def initRadiobuttonFrame(self):
        radiobuttons = []
        radiobutton_frame = Tkinter.Frame(self)
        radiobuttons.append(Tkinter.Radiobutton(radiobutton_frame, text="All", variable=self.current_radio_button,
                                                value=0, command=lambda:self.radioButtonChange()))
        radiobuttons[0].grid(column=0, row=0)
        radiobuttons[0].select()
        for i in range(1, 7):
            radiobuttons.append(Tkinter.Radiobutton(radiobutton_frame, text=i, variable=self.current_radio_button,
                                                    value=i, command=lambda:self.radioButtonChange()))
            radiobuttons[i].grid(column=i, row=0)
        return radiobutton_frame

    def initTargetFrame(self):
        frame = Tkinter.Frame(self)
        MyWindows.newTextBox(frame, "Freq:", 0, 0, self.target_textboxes, validatecommand=self.validateFreq)
        disable_checkbox = Tkinter.Checkbutton(frame, text="Disable", variable=self.disable_checkbox_var,
                                               command=lambda: self.disableButtonChange())
        disable_checkbox.grid(row=0, column=2, padx=5, pady=5, columnspan=2)
        MyWindows.newTextBox(frame, "Width:", 0, 1, self.target_textboxes)
        MyWindows.newTextBox(frame, "Height:", 2, 1, self.target_textboxes)
        MyWindows.newColorButton(4, 1, self.targetColor, frame, "Color1",
                                 self.target_textboxes, self.target_color_buttons)
        MyWindows.newTextBox(frame, "x:", 0, 2, self.target_textboxes)
        MyWindows.newTextBox(frame, "y:", 2, 2, self.target_textboxes)
        MyWindows.newColorButton(4, 2, self.targetColor, frame, "Color2",
                                 self.target_textboxes, self.target_color_buttons)
        self.loadValues(0)
        for key in self.target_color_buttons:
            MyWindows.changeButtonColor(self.target_color_buttons[key], self.target_textboxes[key])
        return frame

    def initButtonFrame(self, button_names, commands, start_column=0, default_frame=lambda a: Tkinter.Frame(a), *options):
        frame = default_frame(self)
        for i in range(len(button_names)):
            Tkinter.Button(frame, text=button_names[i],
                           command=lambda i=i: commands[i](*options)).grid(column=start_column+i, row=0, padx=5, pady=5)
        return frame

    def initTestFrame(self):
        textboxes = {}
        frame = self.initButtonFrame(["Test"], [self.testExtraction], 0, lambda a: Tkinter.Frame(a), textboxes)
        MyWindows.newTextBox(frame, "Length:", 1, 0, textboxes)
        MyWindows.newTextBox(frame, "Min:", 3, 0, textboxes)
        MyWindows.newTextBox(frame, "Max:", 5, 0, textboxes)
        textboxes["Length"].insert(0, 128*30)
        textboxes["Min"].insert(0, 128*2)
        textboxes["Max"].insert(0, 128*4)
        return frame

    def initMainButtons(self):
        frame = Tkinter.Frame(self)
        self.start_button = Tkinter.Button(frame, text="Start", command=lambda: self.start("Start"))
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        self.start_button2 = Tkinter.Button(frame, text="Start2", command=lambda: self.start("Start2"))
        self.start_button2.grid(row=0, column=1, padx=5, pady=5)
        self.initButtonFrame(["Save", "Load", "Exit"],
                             [self.saveFile, self.loadFile, self.exit], 2, default_frame=lambda a: frame)
        return frame

    def initRecordFrame(self):
        textboxes = {}
        frame = self.initButtonFrame(["Neutral", "Target", "Threshold"],
                                     [self.recordNeutral, self.recordTarget, self.calculateThreshold], 0,
                                     lambda a: Tkinter.Frame(a), textboxes)
        MyWindows.newTextBox(frame, "Length:", 3, 0, textboxes)
        textboxes["Length"].insert(0, 128*8)
        return frame

    def initElements(self):
        self.initTitleFrame("Window").pack()
        self.initWindowFrame().pack()
        self.initTitleFrame("Targets").pack()
        self.initRadiobuttonFrame().pack()
        self.initTargetFrame().pack()
        self.initTitleFrame("Record").pack()
        self.initRecordFrame().pack()
        self.initTitleFrame("Test").pack()
        self.initTestFrame().pack()
        self.initButtonFrame(["Targets", "Plots", "Extraction", "Game"],
                             [self.targetsWindow, self.plotWindow, self.extraction, self.game]).pack()
        self.initMainButtons().pack()
        self.initButtonFrame(["Reset"], [self.resetResults]).pack()

    def changeMonitor(self, monitor, textbox):
        textbox.delete(0, Tkinter.END)
        textbox.insert(0, getattr(win32api.EnumDisplaySettings(monitor, win32con.ENUM_CURRENT_SETTINGS), "DisplayFrequency"))

    def resetResults(self):
        self.connection.send("Reset results")

    def game(self):
        self.newProcess(Main.runGame, "Add game")

    def calculateThreshold(self, options):
        self.connection.send("Threshold")
        self.connection.send(self.getChosenFreq())

    def exit(self):
        print "Exiting main window"
        self.connection.send("Exit")
        self.destroy()

    def extraction(self):
        self.newProcess(Main.runExtractionControl, "Add extraction", self.sensor_names)

    def validateFreq(self, textbox):
        if textbox.get() != "":
            monitor_freq = int(self.background_textboxes["Freq"].get())
            freq = float(textbox.get())
            freq_on = int(monitor_freq/freq//2)
            freq_off = int(monitor_freq/freq/2.0+0.5)
            textbox.delete(0, Tkinter.END)
            textbox.insert(0, float(monitor_freq)/(freq_off+freq_on))
        return True

    def getEnabledTargets(self):
        targets = []
        for target in self.targets[1:]:
            if int(target["Disable"]) == 0:
                targets.append(target)
        return targets

    def getChosenFreq(self):
        freq = []
        for i in range(1, len(self.targets)):
            if int(self.targets[i]["Disable"]) == 0:
                freq.append(float(self.targets[i]["Freq"]))
        return freq

    def getBackgroundData(self):
        self.saveValues(self.current_radio_button.get())
        bk = {}
        for key in self.background_textboxes:
            bk[key] = self.background_textboxes[key].get()
        return bk

    def testExtraction(self, *options):
        self.start("Test", *options)

    def recordTarget(self, options):
        length = int(options["Length"].get())
        if self.current_radio_button.get() == 0:
            print "Choose target"
        else:
            self.connection.send("Record target")
            # self.connection.send(self.getEnabledTargets())
            self.connection.send(self.getBackgroundData())
            self.connection.send([self.targets[self.current_radio_button.get()]])
            self.connection.send(length)
            self.connection.send(self.current_radio_button.get())

    def recordNeutral(self, options):
        length = int(options["Length"].get())
        self.connection.send("Record neutral")
        self.connection.send(length)
        self.connection.send(self.current_radio_button.get())

    def sendOptions(self, options):
        if len(options) != 0:
            self.connection.send({key: int(options[0][key].get()) for key in options[0]})
        else:
            self.connection.send({"Length": float("inf")})

    def start(self, message, *options):
        self.saveValues(self.current_radio_button.get())
        self.start_button.configure(text="Stop", command=lambda: self.stop())
        self.start_button2.configure(text="Stop", command=lambda: self.stop())
        self.connection.send(message)
        self.sendOptions(options)
        self.connection.send(self.current_radio_button.get())
        self.connection.send(self.getBackgroundData())
        self.connection.send(self.getEnabledTargets())
        self.connection.send(self.getChosenFreq())

    def stop(self):
        self.start_button.configure(text="Start", command=lambda: self.start("Start"))
        self.start_button2.configure(text="Start2", command=lambda: self.start("Start2"))
        self.connection.send("Stop")

    def newProcess(self, func, message, *args):
        new_to_post_office, post_office_to_new = multiprocessing.Pipe()
        p = multiprocessing.Process(target=func, args=(new_to_post_office, args))
        p.start()
        self.connection.send(message)
        reduced = multiprocessing.reduction.reduce_connection(post_office_to_new)
        self.connection.send(reduced)

    def targetsWindow(self):
        self.newProcess(Main.runPsychopy, "Add psychopy", self.getBackgroundData(), self.lock)

    def plotWindow(self):
        self.newProcess(Main.runPlotControl, "Add plot", self.sensor_names)

    def loadValues(self, index):
        if index == 0:
            for key in self.target_textboxes:
                valid = False
                first_value = self.targets[1][key]
                for i in range(2, len(self.targets)):
                    if first_value != self.targets[i][key]:
                        valid = False
                        break
                    else:
                        valid = True
                self.target_textboxes[key].delete(0, Tkinter.END)
                if valid:
                    self.target_textboxes[key].insert(0, str(self.targets[0][key]))
        else:
            for key in self.target_textboxes:
                self.target_textboxes[key].delete(0, Tkinter.END)
                self.target_textboxes[key].insert(0, str(self.targets[index][key]))
        for key in self.target_color_buttons:
            MyWindows.changeButtonColor(self.target_color_buttons[key], self.target_textboxes[key])
        self.disable_checkbox_var.set(self.targets[index]["Disable"])
        self.validateFreq(self.target_textboxes["Freq"])

    def saveValues(self, index):
        self.validateFreq(self.target_textboxes["Freq"])
        if index == 0:
            for key in self.target_textboxes:
                if self.target_textboxes[key].get() != "":
                    for target in self.targets:
                        target[key] = self.target_textboxes[key].get()
        for key in self.target_textboxes:
            self.targets[index][key] = self.target_textboxes[key].get()
        self.targets[index]["Disable"] = self.disable_checkbox_var.get()

    def radioButtonChange(self):
        for key in self.target_textboxes:
            self.target_textboxes[key].config(state=Tkinter.NORMAL)
        self.saveValues(self.previous_radio_button)
        self.loadValues(self.current_radio_button.get())
        self.previous_radio_button = self.current_radio_button.get()
        self.disableButtonChange()

    def disableButtonChange(self):
        value = self.disable_checkbox_var.get()
        if value == 1:
            for key in self.target_textboxes:
                self.target_textboxes[key].config(state="readonly")
        else:
            for key in self.target_textboxes:
                self.target_textboxes[key].config(state=Tkinter.NORMAL)

        # if self.current_radio_button.get() == 0:
        #     value = self.targets[0]
        #     if self.all_disable:
        #         for i in range(1, len(self.targets)):
        #             self.targets[i]["Disable"] = value
        #     # self.disable_prev_value = value

    def saveFile(self):
        self.saveValues(self.current_radio_button.get())
        file = tkFileDialog.asksaveasfile()
        if file is not None:
            for key in sorted(self.background_textboxes):
                file.write(self.background_textboxes[key].get()+" ")
            file.write("\n")
            for target in self.targets[1:]:
                for key in sorted(target):
                    file.write(str(target[key])+" ")
                file.write("\n")
            file.close()

    def loadFile(self):
        file = tkFileDialog.askopenfile()
        if file is not None:
            line = file.readline()
            values = line.split()
            k = 0
            for key in sorted(self.background_textboxes):
                self.background_textboxes[key].delete(0, Tkinter.END)
                self.background_textboxes[key].insert(0, values[k])
                k += 1
            j = 1
            for line in file:
                values = line.split()
                target = self.targets[j]
                i = 0
                for key in sorted(target):
                    target[key] = values[i]
                    i += 1
                j += 1
        self.loadValues(self.current_radio_button.get())

    def targetColor(self, title):
        ColorWindow.TargetColorWindow(self, self.target_textboxes[title], title, self.targets[self.current_radio_button.get()],
                          self.target_color_buttons[title])

    def backgroundColor(self, title):
        ColorWindow.BackgroundColorWindow(self, self.background_textboxes[title], title, self.background_color_buttons[title])