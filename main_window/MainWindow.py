__author__ = 'Anti'

from main_window import MyWindows
from frames import MainFrame
import Tkinter
import tkFileDialog
import multiprocessing
import multiprocessing.reduction
import Main


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "VEP-BCI", 310, 500)
        default_file_name = "default.txt"
        self.start_button = None

        self.vep_type_var = Tkinter.StringVar()
        self.seed_textbox = None

        self.main_frame = MainFrame.MainFrame(self.start, self.askSaveFile, self.askLoadFile, self.exit)
        self.main_frame.create(self)
        self.loadValues(default_file_name)

        # self.neutral_signal = None
        # self.target_signal = [None for _ in range(self.tabs["Targets"].tab_count)]

        self.connection, post_office_to_main = multiprocessing.Pipe()
        multiprocessing.Process(target=Main.runPostOffice, args=(post_office_to_main,)).start()
        self.lock = multiprocessing.Lock()
        self.newProcess(Main.runEmotiv, "Add emotiv", self.lock)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.mainloop()

    def loadValues(self, default_file_name):
        try:
            self.main_frame.load(open(default_file_name))
        except IOError:
            self.main_frame.loadDefaultValue()

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

    def getEnabledTargets(self, targets_data):
        targets = []
        for key in range(len(targets_data)):
            if key != 0:
                if not self.disabled(targets_data[key]):
                    targets.append(self.filterTargetData(targets_data[key]["TargetFrame"]))
        return targets

    def getFrequencies(self, enabled_targets):
        frequencies = []
        for i in range(len(enabled_targets)):
            frequencies.append(float(enabled_targets[i]["Freq"]))
        return frequencies

    def disabled(self, data):
        return data["DisableDeleteFrame"]["Disable"] == 1

    def getColor(self, data):
        return data["ColorTextboxFrame"]["Textbox"]

    def filterData(self, data, filter):
        return {key: float(data[key]) for key in data if key not in filter}

    def filterColoredData(self, data, filter):
        result = self.filterData(data, filter+("ColorTextboxFrame",))
        result["Color"] = self.getColor(data)
        return result

    def getPlusMinusValue(self, data):
        return data["PlusMinusTextboxFrame"]["Freq"]

    def filterTargetData(self, target_data):
        result = self.filterColoredData(target_data, ("PlusMinusTextboxFrame",))
        result["Freq"] = self.getPlusMinusValue(target_data)
        return result

    def getBackgroundData(self, window_data):
        return self.filterColoredData(window_data, ("Monitor", "Refresh"))

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

    def start(self):
        not_validated = self.main_frame.getNotValidated()
        if len(not_validated) != 0:
            print(not_validated)
        else:
            all_data = self.main_frame.getValue()["MainNotebook"]
            print(all_data)
            print(self.getBackgroundData(all_data["Window"]))
            print(self.getEnabledTargets(all_data["Targets"]))
            print(self.getFrequencies(self.getEnabledTargets(all_data["Targets"])))
            self.main_frame.widgets_dict["BottomFrame"].widgets_dict["Start"].widget.configure(text="Stop", command=self.stop)
            #self.connection.send(message)
            # self.connection.send((self.current_radio_button.get(),
            #                       self.getBackgroundData(),
            #                       self.getEnabledTargets(),
            #                       self.getChosenFreq()))

    def stop(self):
        self.main_frame.widgets_dict["BottomFrame"].widgets_dict["Start"].widget.configure(text="Start", command=self.start)
        # self.connection.send("Stop")

    def newProcess(self, func, message, *args):
        new_to_post_office, post_office_to_new = multiprocessing.Pipe()
        multiprocessing.Process(target=func, args=(new_to_post_office, args)).start()
        self.connection.send(message)
        self.connection.send(multiprocessing.reduction.reduce_connection(post_office_to_new))

    def targetsWindow(self):
        self.newProcess(Main.runPsychopy, "Add psychopy", self.getBackgroundData(), self.lock)

    def plotWindow(self):
        self.newProcess(Main.runPlotControl, "Add plot")

    def askSaveFile(self):
        self.saveFile(tkFileDialog.asksaveasfile())

    def saveFile(self, file):
        if file is not None:
            self.main_frame.save(file)
            file.close()

    def askLoadFile(self):
        self.loadFile(tkFileDialog.askopenfile())

    def loadFile(self, file):
        if file is not None:
            self.main_frame.load(file)
            file.close()
