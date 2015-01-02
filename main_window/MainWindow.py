__author__ = 'Anti'

from main_window import MyWindows
from notebooks import TargetNotebook, ExtractionNotebook, PlotNotebook
from widgets import Widget
from variables import Variable
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
        self.tabs = {
            "Window": WindowFrameTab(self.notebooks["Main"]),
            "Extraction": SameTabsNotebook(self.notebooks["Main"])
        }

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

        self.neutral_signal = None
        self.target_signal = [None for _ in range(self.notebooks["Target"].tab_count)]

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
            self.notebooks["Target"].loadDefaultNotebook()
            self.tabs["Extraction"].loadDefaultValues()
            self.notebooks["Plot"].loadDefaultNotebook()
            self.tabs["Window"].loadDefaultValues()
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
        notebook.add(self.tabs["Window"], text="Window")
        # frequency_textbox gets value from windowFrame and it is needed in TargetNotebook
        notebook.add(self.notebooks["Target"], text="Targets")
        notebook.add(self.tabs["Extraction"], text="Extraction")
        notebook.add(self.notebooks["Plot"], text="Plot")
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
            self.notebooks["Target"].save(file)
            self.tabs["Extraction"].save(file)
            self.notebooks["Plot"].save(file)
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
            self.notebooks["Target"].load(file)
            self.tabs["Extraction"].load(file)
            self.notebooks["Plot"].load(file)
            file.close()


class Tab(object):
    def __init__(self):
        self.frame_widgets = []

    def save(self, file):
        pass

    def load(self, values):
        pass

    def loadDefaultValues(self):
        pass

    def createFrame(self):
        pass


class SameTabsNotebook(ttk.Notebook, Tab):
    def __init__(self, parent):
        ttk.Notebook.__init__(self, parent)
        Tab.__init__(self)
        self.tabs = []
        self.tab_count = 0
        self.default_tab_count = 1
        self.bind("<<NotebookTabChanged>>", self.tabChangedEvent)
        self.createFrame()

    def tabChangedEvent(self, event):
        if event.widget.index("current") == self.tab_count+1:
            self.addTab()

    def createFrame(self):
        self.addInitialTabs()

    def addInitialTabs(self):
        self.addPlusTab()
        self.tab(self.tab_count, text="All")
        self.addPlusTab()

    def addPlusTab(self):
        self.tabs.append(ExtractionTab(self, self.deleteTab))
        self.add(self.tabs[-1], text="+")

    def loadDefaultValues(self):
        self.tabs[0].loadDefaultValues()  # Default values to All tab
        for _ in range(self.default_tab_count):
            self.addTab()

    def loadTab(self, tab_id, file):
        self.tabs[tab_id].load(file)

    def save(self, file):
        file.write(str(self.tab_count)+"\n")
        for tab_id in range(self.tab_count-1) :
            self.tabs[tab_id].save(file)

    def load(self, file):
        self.deleteAllTabs()
        tab_count = int(file.readline())
        self.loadTab(self.tab_count, file)  # Values to All tab
        for i in range(tab_count):
            self.addTab()
            self.loadTab(self.tab_count, file)

    def deleteAllTabs(self):
        if self.tab_count != 0:
            self.select(1)
            while self.tab_count > 0:
                self.deleteTab()

    def deleteTab(self, var=None):
        current = self.index("current")
        if current != 0:
            self.tab_count -= 1
            self.changeActiveTab(current)
            self.forget(current)

    def changeActiveTab(self, current):
        if current == self.tab_count+1:
            self.select(current-1)
        else:
            while current < self.tab_count+2:
                self.tab(current, text=self.tab(current, "text")-1)
                current += 1

    def addTab(self):
        self.tab_count += 1
        self.tabs[-1].loadDefaultValues()
        self.tab(self.tab_count, text=self.tab_count)
        self.addPlusTab()


class FrameTab(Tkinter.Frame, Tab):
    def __init__(self, parent):
        Tab.__init__(self)
        Tkinter.Frame.__init__(self, parent)
        self.buttons = {
            "Color": {},
            "Other": {}
        }
        self.menus = {}
        self.textboxes = {}
        self.variables = {}
        self.checkboxes = {}
        self.default_values = {
            "Textboxes": {},
            "Variables": {}
        }

    def getAllWidgets(self):
        return (widgets for widgets in self.frame_widgets)

    def createFrame(self):
        for frame_widgets in self.getAllWidgets():
            frame = Tkinter.Frame(self)
            for options in frame_widgets:
                if isinstance(options, Widget.Widget):
                    options.create(frame)
                    continue
                name = options[1][0]
                type = options[0]
                default_value = options[2]
                args = options[1]
                if type == "Textbox":
                    self.textboxes[name] = MyWindows.newTextBox(frame, *args)
                    self.default_values["Textboxes"][name] = default_value
                elif type == "Color":
                    self.textboxes[name], self.buttons["Color"][name] = MyWindows.newColorButton(frame, *args)
                    self.default_values["Textboxes"][name] = default_value
                elif type == "Menu":
                    self.menus[name], self.variables[name] = MyWindows.newOptionMenu(frame, *args[1:])  # First arg is name
                    self.default_values["Variables"][name] = default_value
                elif type == "Button":
                    self.buttons["Other"][name] = MyWindows.newButton(frame, *args)
                elif type == "Check":
                    self.checkboxes[name], self.variables[name] = MyWindows.newCheckbox(frame, *args)
                    self.default_values["Variables"][name] = default_value
                else:
                    print("Unknown type: "+type)
            frame.pack()

    def save(self, file):
        MyWindows.saveDict(self.textboxes, file)
        MyWindows.saveDict(self.variables, file)

    def load(self, file):
        MyWindows.updateDict(self.textboxes, file.readline().split(), MyWindows.updateTextbox)
        MyWindows.updateDict(self.variables, file.readline().split(), MyWindows.updateVar)

    def loadDefaultValues(self):
        for key in self.textboxes:
            MyWindows.updateTextbox(self.textboxes[key], self.default_values["Textboxes"][key])
        for key in self.buttons["Color"]:
            MyWindows.validateColor(self.textboxes[key], self.buttons["Color"][key])
        for key in self.menus:
            MyWindows.updateVar(self.variables[key], self.default_values["Variables"][key])
        for key in self.checkboxes:
            MyWindows.updateVar(self.variables[key], self.default_values["Variables"][key])


class ExtractionPlotTab(FrameTab):
    def __init__(self, parent, delete_tab):
        FrameTab.__init__(self, parent)
        self.disabled = None
        self.disabled_widgets = []
        #self.disable_window = lambda x: self.disableTextboxes(self.variables["Window"], ["Beta"],               "Kaiser")
        self.frame_widgets.append((
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "AF3", None, "disabled", Tkinter.BooleanVar(), 0, 0, 0, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "F7",  None, "disabled", Tkinter.BooleanVar(), 0, 0, 1, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "F3",  None, "disabled", Tkinter.BooleanVar(), 0, 0, 2, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "FC5", None, "disabled", Tkinter.BooleanVar(), 0, 0, 3, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "T7",  None, "disabled", Tkinter.BooleanVar(), 0, 0, 4, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "P7",  None, "disabled", Tkinter.BooleanVar(), 0, 0, 5, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "O1",  None, "disabled", Tkinter.BooleanVar(), 1, 0, 6, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "O2",  None, "disabled", Tkinter.BooleanVar(), 1, 1, 0, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "P8",  None, "disabled", Tkinter.BooleanVar(), 0, 1, 1, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "T8",  None, "disabled", Tkinter.BooleanVar(), 0, 1, 2, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "FC6", None, "disabled", Tkinter.BooleanVar(), 0, 1, 3, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "F4",  None, "disabled", Tkinter.BooleanVar(), 0, 1, 4, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "F8",  None, "disabled", Tkinter.BooleanVar(), 0, 1, 5, 1, 1, 0),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "AF4", None, "disabled", Tkinter.BooleanVar(), 0, 1, 6, 1, 1, 0)
        ))
        windows = ("None", "Hanning", "Hamming", "Blackman", "Kaiser", "Bartlett")
        w1 = Widget.Textbox("From",      float, False, True, 0, 3, 0, 1)
        w2 = Widget.Textbox("To",        float, False, True, 0, 3, 2, 1)
        w3 = Widget.Textbox("Taps",      int, False, True,   0, 3, 4, 1)
        self.disable_filter = lambda variable: self.disableTextboxes(variable, (w1, w2, w3), 1)
        self.frame_widgets.append((
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "Normalise", None, "disabled", Tkinter.BooleanVar(), 0, 0, 0, 2),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "Detrend",   None, "disabled", Tkinter.BooleanVar(), 0, 0, 2, 2),
            Widget.WidgetWithTkinterVariable(Tkinter.Checkbutton, "Filter",    self.disable_filter, "disabled", Tkinter.BooleanVar(), 0, 0, 4, 2),
            Widget.Textbox("Step",      int, False, False, 32, 1, 0, 1),
            Widget.Textbox("Length",    int, False, False, 512,1, 2, 1),
            w1,
            w2,
            w3,
            Widget.OptionMenu("Window", None, Tkinter.StringVar(), windows, windows[0], 4, 0, 2),
            Widget.Textbox("Beta",      int, False, True,   0, 4, 2, 1),
            Widget.Textbox("Break",     int, False, True,   0, 4, 4, 1),
        ))
        self.d1, self.d2 = Widget.SunkenButton("Disable", self.changeDisability, 0, 0, 1, 5, 5), Widget.Widget(Tkinter.Button, "Delete",  delete_tab, "disabled",  0, 1, 1, 5, 5)
        self.frame_widgets.append((
            self.d1, self.d2
        ))

    def save(self, file):
        FrameTab.save(self, file)
        file.write("Disable:"+str(int(self.disabled))+"\n")

    def load(self, file):
        FrameTab.load(self, file)
        #self.disable_filter()
        #self.disable_window(None)
        self.disabled = bool(int(file.readline().split(":")[1]))

    def loadDefaultValues(self):
        for frame in self.frame_widgets:
            for widget in frame:
                if isinstance(widget, Widget.Widget):
                    widget.loadDefaultValue()
        FrameTab.loadDefaultValues(self)
        #self.disable_filter()
        #self.disable_window(None)
        self.disabled = False

    def disableTextbox(self, widget):
        widget.widget.config(state="readonly")
        self.disabled_widgets.append(widget)

    def enableTextbox(self, widget):
        widget.widget.config(state=Tkinter.NORMAL)
        self.disabled_widgets.remove(widget)

    def disableTextboxes(self, variable, widgets, value):
        function = self.enableTextbox if variable.get() == value else self.disableTextbox
        for widget in widgets:
            function(widget)

    def changeDisability(self, var):
        for frame in self.frame_widgets:
            for widget in frame:
                if widget != self.d1 and widget != self.d2:
                    if widget not in self.disabled_widgets:
                        if var.get():
                            widget.enable()
                        else:
                            print(widget)
                            widget.disable()



class ExtractionTab(ExtractionPlotTab):
    def __init__(self, parent, delete_tab):
        ExtractionPlotTab.__init__(self, parent, delete_tab)
        # self.frame_widgets.insert(1, (
        #     ("Check", ("PSDA",     None, 0, 0, 1, 0, 0), 0),
        #     ("Check", ("Sum PSDA", None, 0, 1, 1, 0, 0), 0),
        #     ("Check", ("CCA",      None, 0, 2, 1, 0, 0), 0),
        #     ("Check", ("Both",     None, 1, 0, 1, 0, 0), 0),
        #     ("Check", ("Sum Both", None, 1, 1, 1, 0, 0), 0)
        # ))
        self.createFrame()


class WindowFrameTab(FrameTab):
    def __init__(self, parent):
        FrameTab.__init__(self, parent)
        monitor_names = self.getMonitorNames()
        self.frame_widgets.append(
            (
                ("Textbox", ("Width",   lambda textbox: MyWindows.validateInt(textbox, False, False),     0, 0, 1), 800),
                ("Textbox", ("Height",  lambda textbox: MyWindows.validateInt(textbox, False, False),     0, 2, 1), 600),
                ("Color",   ("Color",   lambda textbox, button: MyWindows.validateColor(textbox, button), 0, 4, 1), "#000000"),
                ("Menu",    ("Monitor", self.updateMonitorFreqTextbox,    1, 0, 2, monitor_names),    monitor_names[0]),
                ("Textbox", ("Freq",    lambda textbox: MyWindows.validateInt(textbox, False, False),     1, 2, 1), self.getMonitorFrequency(monitor_names[0])),
                ("Button",  ("Refresh", self.refreshMonitorNames,                                         1, 4, 1), None)
            )
        )
        self.createFrame()

    def getMonitorNames(self):
        return [win32api.GetMonitorInfo(monitor[0])["Device"] for monitor in win32api.EnumDisplayMonitors()]

    def getMonitorFrequency(self, monitor_name):
        return getattr(win32api.EnumDisplaySettings(monitor_name, win32con.ENUM_CURRENT_SETTINGS), "DisplayFrequency")

    def refreshMonitorNames(self):
        self.menus["Monitor"]["menu"].delete(0, Tkinter.END)
        for monitor_name in self.getMonitorNames():
            self.menus["Monitor"]["menu"].add_command(label=monitor_name, command=lambda x=monitor_name: (self.variables["Monitor"].set(x), self.updateMonitorFreqTextbox(x)))
        self.updateMonitorFreqTextbox(self.variables["Monitor"].get())
        MyWindows.validateInt(self.textboxes["Freq"], False, False)

    def updateMonitorFreqTextbox(self, monitor_name):
        monitor_names = self.getMonitorNames()
        if monitor_name not in monitor_names:
            MyWindows.updateVar(self.variables["Monitor"], monitor_names[0])
            self.refreshMonitorNames()
        else:
            MyWindows.updateTextbox(self.textboxes["Freq"], self.getMonitorFrequency(monitor_name))
        #self.notebooks["Target"].changeAllFreqs()
