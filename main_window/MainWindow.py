__author__ = 'Anti'

from main_window import MyWindows
from notebooks import TargetNotebook, ExtractionNotebook, PlotNotebook, SameTabsNotebook
from frames import ExtractionPlotTabs, WindowTab, TargetsTab
import Tkinter
import tkFileDialog
import multiprocessing
import multiprocessing.reduction
import Main
import ttk
import math


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "VEP-BCI", 310, 500)
        default_file_name = "default.txt"
        self.start_button = None
        self.background_color_buttons = {}

        self.test_vars = {name: Tkinter.IntVar() for name in ["Random", "Standby"]}
        self.vep_type_var = Tkinter.StringVar()
        self.seed_textbox = None
        self.textboxes = {
            "Record": {},
            "Test": {},
            "Frequency": None
        }
        self.notebooks = {
            "Main": ttk.Notebook(self),
            "Target": TargetNotebook.TargetNotebook(self),
            "Extraction": ExtractionNotebook.ExctractionNotebook(self),
            "Plot": PlotNotebook.PlotNotebook(self)
        }
        validate_freq = lambda textbox, d: self.changeFreq(self.tabs["Window"].widgets_dict["Freq"], textbox, d)
        self.tabs = {
            "Window":     WindowTab.WindowTab(0, 0, 1, 0, 0),
            "Targets":    SameTabsNotebook.TargetNotebook(0, 0, 1, 0, 0, validate_freq),
            "Extraction": SameTabsNotebook.ExtractionNotebook(0, 0, 1, 0, 0),
            "Plot":       SameTabsNotebook.PlotNotebook(0, 0, 1, 0, 0)
        }
        for key in self.tabs:
            self.tabs[key].create(self.notebooks["Main"])

        self.validate_commands = {
            "Record": {
                "Length": lambda textbox: MyWindows.validateInt(textbox, False, False)
            },
            "Test": {
                "Min": lambda textbox: MyWindows.validateInt(textbox, False, False),
                "Max": lambda textbox: MyWindows.validateInt(textbox, False, False),
                "Length": lambda textbox: MyWindows.validateInt(textbox, False, False)
            }
        }
        self.initNotebook(self.notebooks["Main"])
        self.loadValues(default_file_name)
        self.initBottomFrame(self).pack()

        # self.neutral_signal = None
        # self.target_signal = [None for _ in range(self.tabs["Targets"].tab_count)]

        self.connection, post_office_to_main = multiprocessing.Pipe()
        multiprocessing.Process(target=Main.runPostOffice, args=(post_office_to_main,)).start()
        self.lock = multiprocessing.Lock()
        self.newProcess(Main.runEmotiv, "Add emotiv", self.lock)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.mainloop()

    def changeFreq(self, monitor_freq_textbox, target_freq_textbox, d):
        target_freq = float(target_freq_textbox.widget.get())
        monitor_freq = int(monitor_freq_textbox.widget.get())
        if target_freq > 0:
            freq_on = math.floor(monitor_freq/target_freq/2)
            freq_off = math.ceil(monitor_freq/target_freq/2)
            if freq_on+freq_off+d != 0:
                target_freq_textbox.updateValue(float(monitor_freq)/(freq_off+freq_on+d))

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
            self.tabs["Targets"].loadDefaultValue()
            self.tabs["Extraction"].loadDefaultValue()
            self.tabs["Plot"].loadDefaultValue()
            self.tabs["Window"].loadDefaultValue()
            self.textboxes["Test"]["Length"].insert(0, 128*30)
            self.textboxes["Test"]["Min"].insert(0, 128*2)
            self.textboxes["Test"]["Max"].insert(0, 128*4)
            self.textboxes["Record"]["Length"].insert(0, 128*8)
            self.vep_type_var.set("removeListElement")
            #self.vepTypeChange()

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
        self.textboxes["Record"]["Length"] = MyWindows.newTextBox(frame, "Length", self.validate_commands["Record"]["Length"], column=3)
        return frame

    def testFrame(self, parent):
        frame = Tkinter.Frame(parent)
        self.textboxes["Test"]["Length"] = MyWindows.newTextBox(frame, "Length", self.validate_commands["Test"]["Length"])
        self.textboxes["Test"]["Min"] = MyWindows.newTextBox(frame, "Min", self.validate_commands["Test"]["Min"], column=2)
        self.textboxes["Test"]["Max"] = MyWindows.newTextBox(frame, "Max", self.validate_commands["Test"]["Max"], column=4)
        self.test_vars["Random"] = MyWindows.newCheckbox(frame, "Random", row=1)[1]
        self.test_vars["Standby"] = MyWindows.newCheckbox(frame, "Standby", row=1, column=2)[1]
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
        notebook.add(self.tabs["Window"].widget, text="Window")
        # frequency_textbox gets value from windowFrame and it is needed in TargetNotebook
        notebook.add(self.tabs["Targets"].widget, text="Targets")
        notebook.add(self.tabs["Extraction"].widget, text="Extraction")
        notebook.add(self.tabs["Plot"].widget, text="Plot")
        notebook.add(self.recordFrame(self), text="Record")
        notebook.add(self.testFrame(self), text="Test")
        notebook.add(self.resultsFrame(self), text="Results")
        notebook.pack()

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
        for key in self.textboxes["Window"]:
            bk[key] = self.textboxes["Window"][key].get()
        return bk

    def recordTarget(self):
        length = int(self.textboxes["Record"]["Length"].get())
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
        self.connection.send(int(self.textboxes["Record"]["Length"].get()))
        self.connection.send(self.current_radio_button.get())

    def sendOptions(self):
        options = self.textboxes["Test"].update(self.test_vars)
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
            self.tabs["Window"].save(file)
            MyWindows.saveDict(self.textboxes["Test"], file)
            MyWindows.saveDict(self.test_vars, file)
            MyWindows.saveDict(self.textboxes["Record"], file)
            self.tabs["Targets"].save(file)
            self.tabs["Extraction"].save(file)
            self.tabs["Plot"].save(file)
            file.close()

    def askLoadFile(self):
        file = tkFileDialog.askopenfile()
        self.loadFile(file)

    def loadFile(self, file):
        if file is not None:
            self.tabs["Window"].load(file)
            MyWindows.updateDict(self.textboxes["Test"], file.readline().split(), MyWindows.updateTextbox)
            MyWindows.updateDict(self.test_vars, file.readline().split(), MyWindows.updateVar)
            MyWindows.updateDict(self.textboxes["Record"], file.readline().split(), MyWindows.updateTextbox)
            self.tabs["Targets"].load(file)
            self.tabs["Extraction"].load(file)
            self.tabs["Plot"].load(file)
            file.close()
