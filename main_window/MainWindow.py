__author__ = 'Anti'

from main_window import MyWindows
import Tkinter
import tkFileDialog
import multiprocessing
import multiprocessing.reduction
import Main
import win32api
import win32con
import ttk


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "Main Menu", 310, 500)
        self.sensor_names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
        self.start_button = None
        self.target_count = 6
        self.target_textboxes = [{} for _ in range(self.target_count+1)]
        self.background_textboxes = {}
        self.target_color_buttons = [{} for _ in range(self.target_count+1)]
        self.background_color_buttons = {}
        self.frequency_textbox = None

        self.neutral_signal = None
        self.target_signal = [None for _ in range(self.target_count)]
        self.test_vars = {name: Tkinter.IntVar() for name in ["Random", "Standby"]}
        self.test_textboxes = {}
        self.record_textboxes = {}
        self.disable_vars = [Tkinter.IntVar() for _ in range(self.target_count+1)]

        self.monitor_names = [win32api.GetMonitorInfo(monitor[0])["Device"] for monitor in win32api.EnumDisplayMonitors()]
        self.current_monitor = Tkinter.StringVar(value=self.monitor_names[0])

        self.initNotebook()
        self.loadValues(self.target_count, self.target_textboxes, self.target_color_buttons, "default.txt")
        self.initBottomFrame(self).pack()

        self.connection, post_office_to_main = multiprocessing.Pipe()
        multiprocessing.Process(target=Main.runPostOffice, args=(post_office_to_main,)).start()
        self.lock = multiprocessing.Lock()
        self.newProcess(Main.runEmotiv, "Add emotiv", self.lock)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.mainloop()

    def initBottomFrame(self, parent):
        frame = Tkinter.Frame(parent)
        self.start_button = Tkinter.Button(frame, text="Start", command=lambda: self.start("Start"))
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        self.initButtonFrame(frame, ["Save", "Load", "Exit"], [self.saveFile, self.askLoadFile, self.exit], 1)
        return frame

    def loadValues(self, target_count, target_textboxes, target_color_buttons, default_file_name):
        try:
            file = open(default_file_name)
            self.loadFile(file)
        except IOError:
            default_values = {"Height": 150,
                               "Width": 150,
                               "x": 0,
                               "y": 0,
                               "Freq": 10.0,
                               "Color1": "#ffffff",
                               "Color2": "#777777",
                               "Delay": 0}
            for i in range(1, target_count+1):
                for key in default_values:
                    target_textboxes[i][key].delete(0, Tkinter.END)
                    target_textboxes[i][key].insert(0, default_values[key])
                for key in target_color_buttons[i]:
                    MyWindows.changeButtonColor(target_color_buttons[i][key], target_textboxes[i][key])
            self.background_textboxes["Width"].insert(0, 800)
            self.background_textboxes["Height"].insert(0, 600)
            self.background_textboxes["Color"].insert(0, "#000000")
            MyWindows.changeButtonColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])
            self.test_textboxes["Length"].insert(0, 128*30)
            self.test_textboxes["Min"].insert(0, 128*2)
            self.test_textboxes["Max"].insert(0, 128*4)
            self.record_textboxes["Length"].insert(0, 128*8)
            for i in range(2, self.target_count+1):
                self.disable_vars[i].set(1)
            self.disableTargets()

    def windowFrame(self, parent):
        window_frame = Tkinter.Frame(parent)
        self.background_textboxes["Width"] = MyWindows.newTextBox(window_frame, "Width", 0, 0)
        self.background_textboxes["Height"] = MyWindows.newTextBox(window_frame, "Height", 2, 0)
        self.background_textboxes["Color"] = MyWindows.newColorButton(4, 0, window_frame, "Color", self.background_textboxes, self.background_color_buttons)
        self.frequency_textbox = MyWindows.newTextBox(window_frame, "Freq", 2, 1)
        Tkinter.OptionMenu(window_frame, self.current_monitor, *self.monitor_names, command=lambda a:
                           self.changeMonitor(a, self.frequency_textbox)).grid(row=1, column=0, columnspan=2)
        self.changeMonitor(self.monitor_names[0], self.frequency_textbox)
        return window_frame

    def targetFrame(self, parent, textboxes, disable_var, color_buttons):
        frame = Tkinter.Frame(parent)
        textboxes["Freq"] = MyWindows.newTextBox(frame, "Freq", 0, 0, validatecommand=self.validateFreq)
        textboxes["Delay"] = MyWindows.newTextBox(frame, "Delay", 2, 0)
        Tkinter.Checkbutton(frame, text="Disable", variable=disable_var, command=lambda: self.disableButtonChange(textboxes, disable_var)).grid(row=0, column=4, padx=5, pady=5, columnspan=2)
        textboxes["Width"] = MyWindows.newTextBox(frame, "Width", 0, 1)
        textboxes["Height"] = MyWindows.newTextBox(frame, "Height", 2, 1)
        textboxes["Color1"] = MyWindows.newColorButton(4, 1, frame, "Color1", textboxes, color_buttons)
        textboxes["x"] = MyWindows.newTextBox(frame, "x", 0, 2)
        textboxes["y"] = MyWindows.newTextBox(frame, "y", 2, 2)
        textboxes["Color2"] = MyWindows.newColorButton(4, 2, frame, "Color2", textboxes, color_buttons)
        return frame

    def targetNotebookFrame(self, parent):
        frame = Tkinter.Frame(parent)
        notebook = ttk.Notebook(frame)
        for i in range(self.target_count+1):
            if i == 0:
                notebook.add(self.targetFrame(parent, self.target_textboxes[i], self.disable_vars[i], self.target_color_buttons[i]), text="All")
            else:
                notebook.add(self.targetFrame(parent, self.target_textboxes[i], self.disable_vars[i], self.target_color_buttons[i]), text=i)
        notebook.pack()
        return frame

    def initButtonFrame(self, frame, button_names, commands, column=0, row=0):
        for i in range(len(button_names)):
            Tkinter.Button(frame, text=button_names[i],command=commands[i]).grid(column=column+i, row=row, padx=5, pady=5)

    def recordFrame(self, parent):
        frame = Tkinter.Frame(parent)
        self.initButtonFrame(frame, ["Neutral", "Target", "Threshold"], [self.recordNeutral, self.recordTarget, self.calculateThreshold])
        self.record_textboxes["Length"] = MyWindows.newTextBox(frame, "Length", 3, 0)
        return frame

    def testFrame(self, parent):
        frame = Tkinter.Frame(parent)
        self.test_textboxes["Length"] = MyWindows.newTextBox(frame, "Length", 0, 0)
        self.test_textboxes["Min"] = MyWindows.newTextBox(frame, "Min", 2, 0)
        self.test_textboxes["Max"] = MyWindows.newTextBox(frame, "Max", 4, 0)
        Tkinter.Checkbutton(frame, text="Random", variable=self.test_vars["Random"]).grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        Tkinter.Checkbutton(frame, text="Standby", variable=self.test_vars["Standby"]).grid(row=1, column=2, padx=5, pady=5, columnspan=2)
        self.initButtonFrame(frame, ["Targets", "Plots", "Extraction", "Game"], [self.targetsWindow, self.plotWindow, self.extraction, self.game], row=2)
        return frame

    def resultsFrame(self, parent):
        frame = Tkinter.Frame(parent)
        self.initButtonFrame(frame, ["Reset", "Show"], [self.resetResults, self.showResults])
        return frame

    def initNotebook(self):
        notebook = ttk.Notebook(self)
        notebook.add(self.windowFrame(self), text="Window")
        notebook.add(self.targetNotebookFrame(self), text="Targets")
        notebook.add(self.recordFrame(self), text="Record")
        notebook.add(self.testFrame(self), text="Test")
        notebook.add(self.resultsFrame(self), text="Results")
        notebook.pack()

    def changeMonitor(self, monitor, textbox):
        self.frequency_textbox.config(state=Tkinter.NORMAL)
        textbox.delete(0, Tkinter.END)
        textbox.insert(0, getattr(win32api.EnumDisplaySettings(monitor, win32con.ENUM_CURRENT_SETTINGS), "DisplayFrequency"))
        self.frequency_textbox.config(state="readonly")

    def resetResults(self):
        self.connection.send("Reset results")

    def showResults(self):
        self.connection.send("Show results")

    def game(self):
        self.newProcess(Main.runGame, "Add game")

    def calculateThreshold(self):
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
            monitor_freq = int(self.frequency_textbox.get())
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

    def recordTarget(self):
        length = int(self.record_textboxes["Length"].get())
        if self.current_radio_button.get() == 0:
            print "Choose target"
        else:
            self.connection.send("Record target")
            # self.connection.send(self.getEnabledTargets())
            self.connection.send(self.getBackgroundData())
            self.connection.send([self.targets[self.current_radio_button.get()]])
            self.connection.send(length)
            self.connection.send(self.current_radio_button.get())

    def recordNeutral(self):
        self.connection.send("Record neutral")
        self.connection.send(int(self.record_textboxes["Length"].get()))
        self.connection.send(self.current_radio_button.get())

    def sendOptions(self):
        options = self.test_textboxes.update(self.test_vars)
        self.connection.send({key: int(options[key].get()) for key in options})

    def start(self, message):
        self.saveValues(self.current_radio_button.get())
        self.start_button.configure(text="Stop", command=lambda: self.stop())
        self.connection.send(message)
        self.sendOptions()
        self.connection.send((self.current_radio_button.get(),
                              self.getBackgroundData(),
                              self.getEnabledTargets(),
                              self.getChosenFreq()))

    def stop(self):
        self.start_button.configure(text="Start", command=lambda: self.start("Start"))
        self.connection.send("Stop")

    def newProcess(self, func, message, *args):
        new_to_post_office, post_office_to_new = multiprocessing.Pipe()
        multiprocessing.Process(target=func, args=(new_to_post_office, args)).start()
        self.connection.send(message)
        self.connection.send(multiprocessing.reduction.reduce_connection(post_office_to_new))

    def targetsWindow(self):
        self.newProcess(Main.runPsychopy, "Add psychopy", self.getBackgroundData(), self.lock)

    def plotWindow(self):
        self.newProcess(Main.runPlotControl, "Add plot", self.sensor_names)

    def disableButtonChange(self, textboxes, disable_var):
        if disable_var.get() == 1:
            state = "readonly"
        else:
            state = Tkinter.NORMAL
        for key in textboxes:
            textboxes[key].config(state=state)

        # if self.current_radio_button.get() == 0:
        #     value = self.targets[0]
        #     if self.all_disable:
        #         for i in range(1, len(self.targets)):
        #             self.targets[i]["Disable"] = value
        #     # self.disable_prev_value = value

    def saveDict(self, dictionary, file):
        for key in sorted(dictionary):
            file.write(str(dictionary[key].get())+" ")
        file.write("\n")

    def saveList(self, list, file):
        for value in list:
            file.write(str(value.get())+" ")
        file.write("\n")

    def saveFile(self):
        file = tkFileDialog.asksaveasfile()
        if file is not None:
            self.saveDict(self.background_textboxes, file)
            self.saveDict(self.test_textboxes, file)
            self.saveDict(self.test_vars, file)
            self.saveDict(self.record_textboxes, file)
            self.saveList(self.disable_vars, file)
            for textboxes in self.target_textboxes[1:]:
                for key in sorted(textboxes):
                    file.write(str(textboxes[key].get())+" ")
                file.write("\n")
            file.close()

    def askLoadFile(self):
        file = tkFileDialog.askopenfile()
        self.loadFile(file)

    def loadDict(self, dictionary, file, set):
        for key, value in zip(sorted(dictionary), file.readline().split()):
            set(dictionary[key], value)

    def loadTextbox(self, textbox, value):
        textbox.delete(0, Tkinter.END)
        textbox.insert(0, value)

    def loadVar(self, var, value):
        var.set(value)

    def loadList(self, list, file):
        for i, value in enumerate(file.readline().split()):
            self.loadVar(list[i], value)

    def disableTargets(self):
        for i in range(self.target_count+1):
            self.disableButtonChange(self.target_textboxes[i], self.disable_vars[i])

    def loadFile(self, file):
        if file is not None:
            self.loadDict(self.background_textboxes, file, self.loadTextbox)
            MyWindows.changeButtonColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])
            self.loadDict(self.test_textboxes, file, self.loadTextbox)
            self.loadDict(self.test_vars, file, self.loadVar)
            self.loadDict(self.record_textboxes, file, self.loadTextbox)
            self.loadList(self.disable_vars, file)
            for line, textboxes, color_buttons in zip(file, self.target_textboxes[1:], self.target_color_buttons[1:]):
                for key, value in zip(sorted(textboxes), line.split()):
                    self.loadTextbox(textboxes[key], value)
                for key in color_buttons:
                    MyWindows.changeButtonColor(color_buttons[key], textboxes[key])
            self.disableTargets()
