from notebooks import Notebook

__author__ = 'Anti'

from main_window import MyWindows
from notebooks import TargetNotebook, ExtractionNotebook, PlotNotebook
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
        MyWindows.TkWindow.__init__(self, "VEP-BCI", 310, 500)
        default_file_name = "default.txt"
        self.start_button = None
        self.background_textboxes = {}
        self.background_color_buttons = {}
        self.frequency_textbox = None

        self.test_vars = {name: Tkinter.IntVar() for name in ["Random", "Standby"]}
        self.test_textboxes = {}
        self.record_textboxes = {}
        self.vep_type_var = Tkinter.StringVar()
        self.seed_textbox = None

        self.monitor_names = [win32api.GetMonitorInfo(monitor[0])["Device"] for monitor in win32api.EnumDisplayMonitors()]
        self.current_monitor = Tkinter.StringVar(value=self.monitor_names[0])

        self.main_notebook = ttk.Notebook(self)  # Has to be defined before inner notebooks
        self.target_notebook = TargetNotebook.TargetNotebook(self.main_notebook)
        self.extraction_notebook = ExtractionNotebook.ExctractionNotebook(self.main_notebook)
        self.plot_notebook = PlotNotebook.PlotNotebook(self.main_notebook)

        self.initNotebook(self.main_notebook)
        self.target_notebook.setFrequencyTextbox(self.frequency_textbox)
        self.loadValues(default_file_name)
        self.target_notebook.changeAllFreqs()
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
        MyWindows.newButtonFrame(frame, ["Save", "Load", "Exit"], [self.saveFile, self.askLoadFile, self.exit]).grid(row=0, column=1)
        return frame

    def loadValues(self, default_file_name):
        try:
            file = open(default_file_name)
            self.loadFile(file)
        except IOError:
            self.target_notebook.loadDefaultNotebook()
            self.extraction_notebook.loadDefaultNotebook()
            self.plot_notebook.loadDefaultNotebook()
            self.background_textboxes["Width"].insert(0, 800)
            self.background_textboxes["Height"].insert(0, 600)
            self.background_textboxes["Color"].insert(0, "#000000")
            MyWindows.validateColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])
            self.test_textboxes["Length"].insert(0, 128*30)
            self.test_textboxes["Min"].insert(0, 128*2)
            self.test_textboxes["Max"].insert(0, 128*4)
            self.record_textboxes["Length"].insert(0, 128*8)
            self.vep_type_var.set("removeListElement")
            #self.vepTypeChange()

    def windowFrame(self, parent):
        window_frame = Tkinter.Frame(parent)
        self.background_textboxes["Width"] = MyWindows.newTextBox(window_frame, "Width", allow_zero=False)
        self.background_textboxes["Height"] = MyWindows.newTextBox(window_frame, "Height", 2, allow_zero=False)
        self.background_textboxes["Color"], self.background_color_buttons["Color"] = MyWindows.newColorButton(window_frame, "Color", 4)
        self.frequency_textbox = MyWindows.newTextBox(window_frame, "Freq", 2, 1)
        Tkinter.OptionMenu(window_frame, self.current_monitor, *self.monitor_names, command=lambda a:
                           self.changeMonitor(a, self.frequency_textbox)).grid(row=1, column=0, columnspan=2)
        self.changeMonitor(self.monitor_names[0], self.frequency_textbox)
        return window_frame

    # def targetFrame(self, parent):
    #     frame = Tkinter.Frame(parent)
    #     Tkinter.Button(frame, text="- ").grid(row=0, column=0)
    #     Tkinter.Button(frame, text="+").grid(row=0, column=1)
    #     Tkinter.Radiobutton(frame, text="removeListElement-VEP", variable=self.vep_type_var, value="removeListElement", command=self.vepTypeChange).grid(row=0, column=2)
    #     Tkinter.Radiobutton(frame, text="c-VEP", variable=self.vep_type_var, value="c", command=self.vepTypeChange).grid(row=0, column=3)
    #     self.seed_textbox = MyWindows.newTextBox(frame, "Seed", 4, 0, 10)
    #     self.targetNotebookFrame(frame).grid(row=1, columnspan=6)
    #     return frame

    def vepTypeChange(self):
        if self.vep_type_var.get() == "removeListElement":
            self.seed_textbox.config(state="readonly")
        else:
            self.seed_textbox.config(state=Tkinter.NORMAL)

    def recordFrame(self, parent):
        frame = Tkinter.Frame(parent)
        MyWindows.newButtonFrame(frame, ["Neutral", "Target", "Threshold"], [self.recordNeutral, self.recordTarget, self.calculateThreshold]).grid()
        self.record_textboxes["Length"] = MyWindows.newTextBox(frame, "Length", 3, allow_zero=False)
        return frame

    def testFrame(self, parent):
        frame = Tkinter.Frame(parent)
        self.test_textboxes["Length"] = MyWindows.newTextBox(frame, "Length", allow_zero=False)
        self.test_textboxes["Min"] = MyWindows.newTextBox(frame, "Min", 2, allow_zero=False)
        self.test_textboxes["Max"] = MyWindows.newTextBox(frame, "Max", 4, allow_zero=False)
        self.test_vars["Random"] = MyWindows.newCheckbox(frame, "Random", row=1)[0]
        self.test_vars["Standby"] = MyWindows.newCheckbox(frame, "Standby", row=1, column=2)[0]
        MyWindows.newButtonFrame(frame, ["Targets", "Plots", "Extraction"], [self.targetsWindow, self.plotWindow, self.extraction]).grid(columnspan=3)
        return frame

    def resultsFrame(self, parent):
        frame = Tkinter.Frame(parent)
        MyWindows.newButtonFrame(frame, ["Show", "Reset"], [self.showResults, self.resetResults]).grid()
        return frame

    def gameFrame(self, parent):
        frame = Tkinter.Frame(parent)
        MyWindows.newButtonFrame(frame, ["Game"], [self.game]).pack()
        return frame

    def initNotebook(self, notebook):
        notebook.add(self.windowFrame(self), text="Window")
        # frequency_textbox gets value from windowFrame and it is needed in TargetNotebook
        notebook.add(self.target_notebook, text="Targets")
        notebook.add(self.extraction_notebook, text="Extraction")
        notebook.add(self.plot_notebook, text="Plot")
        notebook.add(self.recordFrame(self), text="Record")
        notebook.add(self.testFrame(self), text="Test")
        notebook.add(self.resultsFrame(self), text="Results")
        notebook.pack()

    def changeMonitor(self, monitor, textbox):
        self.frequency_textbox.config(state=Tkinter.NORMAL)
        MyWindows.updateTextbox(textbox, getattr(win32api.EnumDisplaySettings(monitor, win32con.ENUM_CURRENT_SETTINGS), "DisplayFrequency"))
        self.frequency_textbox.config(state="readonly")
        self.target_notebook.changeAllFreqs()

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
        print("Exiting main window")
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
            print("Choose target")
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

    def saveFile(self):
        file = tkFileDialog.asksaveasfile()
        if file is not None:
            MyWindows.saveDict(self.background_textboxes, file)
            MyWindows.saveDict(self.test_textboxes, file)
            MyWindows.saveDict(self.test_vars, file)
            MyWindows.saveDict(self.record_textboxes, file)
            self.target_notebook.save(file)
            self.extraction_notebook.save(file)
            self.plot_notebook.save(file)
            file.close()

    def askLoadFile(self):
        file = tkFileDialog.askopenfile()
        self.loadFile(file)

    def loadFile(self, file):
        if file is not None:
            MyWindows.updateDict(self.background_textboxes, file.readline().split(), MyWindows.updateTextbox)
            MyWindows.validateColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])
            MyWindows.updateDict(self.test_textboxes, file.readline().split(), MyWindows.updateTextbox)
            MyWindows.updateDict(self.test_vars, file.readline().split(), MyWindows.updateVar)
            MyWindows.updateDict(self.record_textboxes, file.readline().split(), MyWindows.updateTextbox)
            self.target_notebook.load(file)
            self.extraction_notebook.load(file)
            self.plot_notebook.load(file)
            file.close()
