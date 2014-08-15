__author__ = 'Anti'

from main_window import MyWindows, ColorWindow
import Tkinter
import tkFileDialog
import multiprocessing
import multiprocessing.reduction
import Main


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "Main Menu", 310, 500)
        self.sensor_names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
        self.start_button = None
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
        self.initElements()
        self.connection, post_office_to_main = multiprocessing.Pipe()
        multiprocessing.Process(target=Main.runPostOffice, args=(post_office_to_main,)).start()
        self.newProcess(Main.runEmotiv, "Add emotiv")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.mainloop()

    def initTitleFrame(self, title):
        windowtitleframe = Tkinter.Frame(self)
        Tkinter.Label(windowtitleframe, text=title).grid(column=0, row=0, padx=5, pady=5)
        return windowtitleframe
        
    def initWindowFrame(self):
        window_frame = Tkinter.Frame(self)
        MyWindows.newTextBox(window_frame, "Width:", 0, 0, self.background_textboxes)
        MyWindows.newTextBox(window_frame, "Height:", 2, 0, self.background_textboxes)
        MyWindows.newColorButton(4, 0, self.backgroundColor, window_frame,
                             "Color", self.background_textboxes, self.background_color_buttons)
        MyWindows.newTextBox(window_frame, "Freq:", 0, 1, self.background_textboxes)
        self.background_textboxes["Width"].insert(0, 800)
        self.background_textboxes["Height"].insert(0, 600)
        self.background_textboxes["Color"].insert(0, "#000000")
        self.background_textboxes["Freq"].insert(0, 60)
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
        MyWindows.newColorButton(4, 2, self.targetColor, frame, "Color2",
                                 self.target_textboxes, self.target_color_buttons)
        MyWindows.newTextBox(frame, "x:", 0, 2, self.target_textboxes)
        MyWindows.newTextBox(frame, "y:", 2, 2, self.target_textboxes)
        self.loadValues(0)
        for key in self.target_color_buttons:
            MyWindows.changeButtonColor(self.target_color_buttons[key], self.target_textboxes[key])
        return frame

    def initButtonFrame(self, button_names, commands, start_column=0):
        frame = Tkinter.Frame()
        for i in range(len(button_names)):
            Tkinter.Button(frame, text=button_names[i],
                           command=lambda i=i: commands[i]()).grid(column=start_column+i, row=0, padx=5, pady=5)
        return frame

    def initElements(self):
        window_title_frame = self.initTitleFrame("Window")
        window_frame = self.initWindowFrame()
        target_title_frame = self.initTitleFrame("Targets")
        radiobutton_frame = self.initRadiobuttonFrame()
        target_frame = self.initTargetFrame()
        button_frame = self.initButtonFrame(["Targets", "Plots", "Extraction"],
                                            [self.targetsWindow, self.plotWindow, self.extraction])
        button_frame2 = self.initButtonFrame(["Save", "Load", "Exit"],
                                             [self.saveFile, self.loadFile, self.exit], 1)
        self.start_button = Tkinter.Button(button_frame2, text="Start", command=lambda: self.start())
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        record_frame = self.initButtonFrame(["Neutral", "Target"],
                                            [self.recordNeutral, self.recordTarget], 2)
        Tkinter.Label(record_frame, text="Record").grid(column=0, row=0, padx=5, pady=5)
        window_title_frame.pack()
        window_frame.pack()
        target_title_frame.pack()
        radiobutton_frame.pack()
        target_frame.pack()
        record_frame.pack()
        button_frame.pack()
        button_frame2.pack()

    def exit(self):
        print "Exiting main window"
        self.connection.send("Exit")
        self.destroy()

    def extraction(self):
        self.newProcess(Main.runPSIdentification, "Add extraction", self.sensor_names)

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

    def getRecordedSignals(self):
        signals = []
        for i in range(1, len(self.targets)):
            if int(self.targets[i]["Disable"]) == 0:
                signals.append(self.target_signal[i])
        signals.append(self.neutral_signal)
        return signals

    def getBackgroundData(self):
        self.saveValues(self.current_radio_button.get())
        bk = {}
        for key in self.background_textboxes:
            bk[key] = self.background_textboxes[key].get()
        return bk

    def recordTarget(self):
        if self.current_radio_button.get() == 0:
            print "Choose target"
        else:
            self.connection.send("Record target")
            # self.connection.send(self.getEnabledTargets())
            self.connection.send(self.getBackgroundData())
            self.connection.send([self.targets[self.current_radio_button.get()]])
            self.connection.send(512)
            while not self.connection.poll(0.1):
                self.update()
            self.target_signal[self.current_radio_button.get()] = self.connection.recv()

    def recordNeutral(self):
        self.connection.send("Record neutral")
        self.connection.send(512)  # length
        while not self.connection.poll(0.1):
            self.update()
        self.neutral_signal = self.connection.recv()

    def start(self):
        self.saveValues(self.current_radio_button.get())
        self.start_button.configure(text="Stop", command=lambda: self.stop())
        self.connection.send("Start")
        self.connection.send(self.getBackgroundData())
        self.connection.send(self.getEnabledTargets())
        self.connection.send(self.getChosenFreq())
        self.connection.send(self.getRecordedSignals())

    def stop(self):
        self.start_button.configure(text="Start", command=lambda: self.start())
        self.connection.send("Stop")

    def newProcess(self, func, message, *args):
        new_to_post_office, post_office_to_new = multiprocessing.Pipe()
        p = multiprocessing.Process(target=func, args=(new_to_post_office, args))
        p.start()
        self.connection.send(message)
        reduced = multiprocessing.reduction.reduce_connection(post_office_to_new)
        self.connection.send(reduced)

    def targetsWindow(self):
        self.newProcess(Main.runPsychopy, "Add psychopy", self.getBackgroundData())

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