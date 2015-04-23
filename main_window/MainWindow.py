__author__ = 'Anti'

from main_window import MyWindows
from frames import MainFrame
import tkFileDialog
import constants as c


class MainWindow(MyWindows.TkWindow):
    def __init__(self, connection):
        MyWindows.TkWindow.__init__(self, "VEP-BCI", 310, 500)
        self.start_button = None

        self.main_frame = MainFrame.MainFrame(self,
            # (
                self.start,
                self.setup,
                self.askSaveFile,
                self.askLoadFile,
                self.exit
            # ),
            # (
            #     self.showResults,
            #     self.resetResults
            # ),
            # (
            #     self.calculateThreshold,
            # ),
        )
        self.loadValues(c.DEFAULT_FILE)

        # self.neutral_signal = None
        # self.target_signal = [None for _ in range(self.tabs["Targets"].tab_count)]

        self.connection = connection
        """ @type : ConnectionProcessEnd.MainConnection """
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

    def calculateThreshold(self):
        self.connection.send("Threshold")
        self.connection.send(self.getChosenFreq())

    def removeDisabledData(self, data, filter_function, frame_key):
        result = []
        for key in range(len(data)):
            if not self.disabled(data[key]):
                result.append(filter_function(data[key], frame_key))
        return result

    def getFrequencies(self, enabled_targets):
        frequencies = []
        for i in range(len(enabled_targets)):
            frequencies.append(float(enabled_targets[i][c.DATA_FREQ]))
        return frequencies

    def disabled(self, data):
        return data[c.DISABLE_DELETE_FRAME][c.DISABLE] == 1

    def toFloat(self, value):  # Try to convert to float. If fails, return value itself.
        try:
            return float(value)
        except ValueError:
            return value

    def toInt(self, value):  # Try to convert to int. If fails, try to convert to float.
        try:
            return int(value)
        except ValueError:
            return self.toFloat(value)

    def filterData(self, data, filter=tuple()):
        result = {}
        for key in data:
            if key not in filter:
                result[key] = self.toInt(data[key])
        return result

    def getPlusMinusValue(self, data):
        return float(data[c.PLUS_MINUS_TEXTOX_FRAME][c.TARGET_FREQ])

    def filterTargetData(self, target_data, key):
        result = self.filterData(
            target_data[key],
            (
                c.TARGET_COLOR1_FRAME,
                c.TARGET_COLOR2_FRAME,
                c.PLUS_MINUS_TEXTOX_FRAME
            )
        )
        result[c.TARGET_COLOR1] = target_data[key][c.TARGET_COLOR1_FRAME][c.TEXTBOX]
        result[c.TARGET_COLOR2] = target_data[key][c.TARGET_COLOR2_FRAME][c.TEXTBOX]
        result[c.DATA_FREQ] = self.getPlusMinusValue(target_data[key])
        return result

    def getTargetData(self, data):
        return self.removeDisabledData(data, self.filterTargetData, c.TARGET_FRAME)

    def getBackgroundData(self, data):
        result = self.filterData(
            data,
            (
                c.WINDOW_COLOR_FRAME,
                c.WINDOW_MONITOR,
                c.WINDOW_REFRESH
            )
        )
        result[c.WINDOW_COLOR] = data[c.WINDOW_COLOR_FRAME][c.TEXTBOX]
        return result

    def getEnabledData(self, data):
        return [key for key in data if data[key] != 0]

    def getOptions(self, data, key):
        return {
            c.DATA_SENSORS: self.getEnabledData(data[c.SENSORS_FRAME]),
            c.DATA_OPTIONS: self.filterData(data[c.OPTIONS_FRAME]),
            c.DATA_METHODS: self.getEnabledData(data[key])
        }

    def getPlotData(self, data):
        return self.removeDisabledData(data, self.getOptions, c.PLOT_TAB_BUTTON_FRAME)

    def getExtractionData(self, data):
        return self.removeDisabledData(data, self.getOptions, c.EXTRACTION_TAB_BUTTON_FRAME)

    def getData(self, all_data):
        target_data = self.getTargetData(all_data[c.TARGETS_NOTEBOOK])
        return {
            c.DATA_BACKGROUND: self.getBackgroundData(all_data[c.WINDOW_TAB]),
            c.DATA_TARGETS: target_data,
            c.DATA_FREQS: self.getFrequencies(target_data),
            c.DATA_PLOTS: self.getPlotData(all_data[c.PLOT_NOTEBOOK]),
            c.DATA_EXTRACTION: self.getExtractionData(all_data[c.EXTRACTION_NOTEBOOK]),
            c.DATA_TEST: self.getTestData(all_data[c.TEST_TAB])
        }

    def getTestData(self, data):
        return self.filterData(data)

    def exit(self):
        print("Exiting main window")
        self.connection.sendExitMessage()
        self.destroy()

    def setup(self):
        not_validated = self.main_frame.getNotValidated()
        if len(not_validated) != 0:
            print(not_validated)
        else:
            self.connection.sendSetupMessage()
            self.connection.sendMessage(self.getData(self.main_frame.getValue()[c.MAIN_NOTEBOOK]))

    def start(self):
        self.main_frame.widgets_dict[c.BOTTOM_FRAME].widgets_dict[c.START_BUTTON].widget.configure(text=c.STOP_BUTTON, command=self.stop)
        self.connection.sendStartMessage()

    def stop(self):
        self.main_frame.widgets_dict[c.BOTTOM_FRAME].widgets_dict[c.START_BUTTON].widget.configure(text=c.START_BUTTON, command=self.start)
        self.connection.sendStopMessage()

    # Save and Load

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

    # Recording (currently not working)

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
