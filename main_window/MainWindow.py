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
import Notebook


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "VEP-BCI", 310, 500)
        default_file_name = "default.txt"
        self.start_button = None
        self.target_textboxes = []
        self.background_textboxes = {}
        self.target_color_buttons = []
        self.background_color_buttons = {}
        self.frequency_textbox = None

        self.test_vars = {name: Tkinter.IntVar() for name in ["Random", "Standby"]}
        self.test_textboxes = {}
        self.record_textboxes = {}
        self.disable_vars = []
        self.vep_type_var = Tkinter.StringVar()
        self.seed_textbox = None

        self.monitor_names = [win32api.GetMonitorInfo(monitor[0])["Device"] for monitor in win32api.EnumDisplayMonitors()]
        self.current_monitor = Tkinter.StringVar(value=self.monitor_names[0])

        self.sensor_checkbox_vars = []
        self.target_notebook = None
        self.extraction_notebook = None

        self.initNotebook()
        self.loadValues(self.target_textboxes, self.target_color_buttons, default_file_name)
        self.initBottomFrame(self).pack()

        self.neutral_signal = None
        self.target_signal = [None for _ in range(self.target_notebook.tab_count)]

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
        MyWindows.initButtonFrame(frame, ["Save", "Load", "Exit"], [self.saveFile, self.askLoadFile, self.exit], 1)
        return frame

    def loadValues(self, target_textboxes, target_color_buttons, default_file_name):
        try:
            file = open(default_file_name)
            self.loadFile(file)
        except IOError:
            for _ in range(6):
                self.target_notebook.addTab()
            self.background_textboxes["Width"].insert(0, 800)
            self.background_textboxes["Height"].insert(0, 600)
            self.background_textboxes["Color"].insert(0, "#000000")
            MyWindows.changeButtonColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])
            self.test_textboxes["Length"].insert(0, 128*30)
            self.test_textboxes["Min"].insert(0, 128*2)
            self.test_textboxes["Max"].insert(0, 128*4)
            self.record_textboxes["Length"].insert(0, 128*8)
            for i in range(2, self.target_notebook.tab_count+1):
                self.updateVar(self.disable_vars[i], 1)
            self.disableTargets()
            self.vep_type_var.set("removeEvent")
            #self.vepTypeChange()

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

    # def targetFrame(self, parent):
    #     frame = Tkinter.Frame(parent)
    #     Tkinter.Button(frame, text="- ").grid(row=0, column=0)
    #     Tkinter.Button(frame, text="+").grid(row=0, column=1)
    #     Tkinter.Radiobutton(frame, text="removeEvent-VEP", variable=self.vep_type_var, value="removeEvent", command=self.vepTypeChange).grid(row=0, column=2)
    #     Tkinter.Radiobutton(frame, text="c-VEP", variable=self.vep_type_var, value="c", command=self.vepTypeChange).grid(row=0, column=3)
    #     self.seed_textbox = MyWindows.newTextBox(frame, "Seed", 4, 0, 10)
    #     self.targetNotebookFrame(frame).grid(row=1, columnspan=6)
    #     return frame

    def vepTypeChange(self):
        if self.vep_type_var.get() == "removeEvent":
            self.seed_textbox.config(state="readonly")
        else:
            self.seed_textbox.config(state=Tkinter.NORMAL)

    def recordFrame(self, parent):
        frame = Tkinter.Frame(parent)
        MyWindows.initButtonFrame(frame, ["Neutral", "Target", "Threshold"], [self.recordNeutral, self.recordTarget, self.calculateThreshold])
        self.record_textboxes["Length"] = MyWindows.newTextBox(frame, "Length", 3, 0)
        return frame

    def testFrame(self, parent):
        frame = Tkinter.Frame(parent)
        self.test_textboxes["Length"] = MyWindows.newTextBox(frame, "Length", 0, 0)
        self.test_textboxes["Min"] = MyWindows.newTextBox(frame, "Min", 2, 0)
        self.test_textboxes["Max"] = MyWindows.newTextBox(frame, "Max", 4, 0)
        Tkinter.Checkbutton(frame, text="Random", variable=self.test_vars["Random"]).grid(row=1, column=0, padx=5, pady=5, columnspan=2)
        Tkinter.Checkbutton(frame, text="Standby", variable=self.test_vars["Standby"]).grid(row=1, column=2, padx=5, pady=5, columnspan=2)
        MyWindows.initButtonFrame(frame, ["Targets", "Plots", "Extraction"], [self.targetsWindow, self.plotWindow, self.extraction], row=2)
        return frame

    def resultsFrame(self, parent):
        frame = Tkinter.Frame(parent)
        MyWindows.initButtonFrame(frame, ["Show", "Reset"], [self.showResults, self.resetResults])
        return frame

    def gameFrame(self, parent):
        frame = Tkinter.Frame(parent)
        MyWindows.initButtonFrame(frame, ["Game"], [self.game])
        return frame

    def initNotebook(self):
        main_notebook = ttk.Notebook(self)  # Has to be defined before inner notebooks!
        main_notebook.add(self.windowFrame(self), text="Window")
        # frequency_textbox gets value from windowFrame and it is needed in TargetNotebook
        self.target_notebook = Notebook.TargetNotebook(main_notebook, self.target_textboxes, self.disable_vars,
                                                       self.target_color_buttons, self.frequency_textbox)
        main_notebook.add(self.target_notebook, text="Targets")
        main_notebook.add(self.recordFrame(self), text="Record")
        main_notebook.add(self.testFrame(self), text="Test")
        main_notebook.add(self.resultsFrame(self), text="Results")
        self.extraction_notebook = Notebook.ExctractionNotebook(main_notebook, self.sensor_checkbox_vars)
        main_notebook.add(self.extraction_notebook, text="Extraction")
        main_notebook.add(self.gameFrame(self), text="Game")
        main_notebook.pack()

    def changeMonitor(self, monitor, textbox):
        self.frequency_textbox.config(state=Tkinter.NORMAL)
        MyWindows.updateTextbox(textbox, getattr(win32api.EnumDisplaySettings(monitor, win32con.ENUM_CURRENT_SETTINGS), "DisplayFrequency"))
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
        self.newProcess(Main.runExtractionControl, "Add extraction")

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
        self.newProcess(Main.runPlotControl, "Add plot")

    def saveDict(self, dictionary, file):
        for key in sorted(dictionary):
            file.write(str(dictionary[key].get())+" ")
        file.write("\n")

    def saveFile(self):
        file = tkFileDialog.asksaveasfile()
        if file is not None:
            self.saveDict(self.background_textboxes, file)
            self.saveDict(self.test_textboxes, file)
            self.saveDict(self.test_vars, file)
            self.saveDict(self.record_textboxes, file)
            for i in range(len(self.target_textboxes[1:])):
                for key in sorted(self.target_textboxes[1:][i]):
                    file.write(str(self.target_textboxes[1:][i][key].get())+" ")
                file.write(str(self.disable_vars[1:][i].get()))
                file.write("\n")
            file.close()

    def askLoadFile(self):
        file = tkFileDialog.askopenfile()
        self.loadFile(file)

    def updateDict(self, dictionary, file, set):
        for key, value in zip(sorted(dictionary), file.readline().split()):
            set(dictionary[key], value)

    def updateVar(self, var, value):
        var.set(value)

    def disableTargets(self):
        for i in range(self.target_notebook.tab_count+1):
            self.target_notebook.disableButtonChange(self.target_textboxes[i], self.disable_vars[i], self.target_color_buttons[i])

    def loadFile(self, file):
        if file is not None:
            self.updateDict(self.background_textboxes, file, MyWindows.updateTextbox)
            MyWindows.changeButtonColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])
            self.updateDict(self.test_textboxes, file, MyWindows.updateTextbox)
            self.updateDict(self.test_vars, file, self.updateVar)
            self.updateDict(self.record_textboxes, file, MyWindows.updateTextbox)
            if self.target_notebook.tab_count != 0:
                self.target_notebook.select(1)
                while self.target_notebook.tab_count > 0:
                    self.removeTarget(self.target_textboxes.index(self.target_textboxes[-1]))
            for line in file:
                self.target_notebook.addTab()
                values = line.split()
                for key, value in zip(sorted(self.target_textboxes[-1]), values):
                    MyWindows.updateTextbox(self.target_textboxes[-1][key], value)
                for key in self.target_color_buttons[-1]:
                    MyWindows.changeButtonColor(self.target_color_buttons[-1][key], self.target_textboxes[-1][key])
                self.updateVar(self.disable_vars[-1], values[-1])
            self.disableTargets()
