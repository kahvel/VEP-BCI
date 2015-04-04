__author__ = 'Anti'

from main_window import MyWindows
from frames import MainFrame
import tkFileDialog
import multiprocessing
import multiprocessing.reduction
import Main


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "VEP-BCI", 310, 500)
        default_file_name = "default.txt"
        self.start_button = None

        self.main_frame = MainFrame.MainFrame(self,
            # (
                self.start,
                self.askSaveFile,
                self.askLoadFile,
                self.exit
            # ),
            # (
            #     self.showResults,
            #     self.resetResults
            # ),
            # (
            #     self.addGame,
            # ),
            # (
            #     self.calculateThreshold,
            # ),
            # (
            #     self.addE
            # )
        )
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

    def addExtraction(self):
        self.newProcess(Main.runExtractionControl, "Add extraction")

    def removeDisabledData(self, data, filter_function, frame_key):
        result = []
        for key in range(len(data)):
            if key != 0:
                if not self.disabled(data[key]):
                    result.append(filter_function(data[key], frame_key))
        return result

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

    def filterTargetData(self, target_data, key):
        result = self.filterColoredData(target_data[key], ("PlusMinusTextboxFrame",))
        result["Freq"] = self.getPlusMinusValue(target_data[key])
        return result

    def getTargetData(self, data):
        return self.removeDisabledData(data, self.filterTargetData, "TargetFrame")

    def getBackgroundData(self, window_data):
        return self.filterColoredData(window_data, ("Monitor", "Refresh"))

    def getEnabledData(self, data):
        return [key for key in data if data[key] != 0]

    def getOptions(self, data, key):
        return {
            "Sensors": self.getEnabledData(data["SensorsFrame"]),
            "Options": self.filterData(data["OptionsFrame"], ("Window",)),
            "Methods": self.getEnabledData(data[key])
        }

    def getPlotData(self, data):
        return self.removeDisabledData(data, self.getOptions, "PlotTabButtonFrame")

    def getExtractionData(self, data):
        return self.removeDisabledData(data, self.getOptions, "ExtractionTabButtonFrame")

    def getData(self, all_data):
        target_data = self.getTargetData(all_data["Targets"])
        return {
            "Background": self.getBackgroundData(all_data["Window"]),
            "Targets": target_data,
            "Freqs": self.getFrequencies(target_data),
            "Plots": self.getPlotData(all_data["Plot"]),
            "Extraction": self.getExtractionData(all_data["Extraction"])
        }

    def start(self):
        not_validated = self.main_frame.getNotValidated()
        if len(not_validated) != 0:
            print(not_validated)
        else:
            self.main_frame.widgets_dict["BottomFrame"].widgets_dict["Start"].widget.configure(text="Stop", command=self.stop)
            self.connection.send("Start")
            self.connection.send(self.getData(self.main_frame.getValue()["MainNotebook"]))

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

    def recordTarget(self):
        length = int(self.textboxes["Record"]["Length"].get())
        if self.current_radio_button.get() == 0:
            print("Choose target")
        else:
            self.connection.send("Record target")
            # self.connection.send(self.removeDisabledData())
            self.connection.send(self.getBackgroundData())
            self.connection.send([self.targets[self.current_radio_button.get()]])
            self.connection.send(length)
            self.connection.send(self.current_radio_button.get())

    def recordNeutral(self):
        self.connection.send("Record neutral")
        self.connection.send(int(self.textboxes["Record"]["Length"].get()))
        self.connection.send(self.current_radio_button.get())
