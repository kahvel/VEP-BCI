__author__ = 'Anti'

from Tkinter import *
import MyWindows
import tkFileDialog
import multiprocessing
from multiprocessing import reduction
import Main
import ColorWindow


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
        self.disable_checkbox_var = IntVar()
        # self.n_targets = 6
        for _ in range(7):
            self.targets.append(self.initial_target.copy())
        self.targets[0]["Disable"] = self.targets[1]["Disable"] = 0
        self.target_color_buttons = {}
        self.background_color_buttons = {}
        self.current_radio_button = IntVar()
        self.previous_radio_button = 0
        self.initElements()
        self.main_to_plot = []
        self.main_to_psychopy = []
        self.main_to_detection = []
        self.main_to_emo, emo_to_main = multiprocessing.Pipe()
        self.detection_to_psychopy, self.psychopy_to_detection = multiprocessing.Pipe()
        multiprocessing.Process(target=Main.runEmotiv, args=(emo_to_main,)).start()
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.mainloop()

    def initTitleFrame(self, title):
        windowtitleframe = Frame(self)
        Label(windowtitleframe, text=title).grid(column=0, row=0, padx=5, pady=5)
        return windowtitleframe
        
    def initWindowFrame(self):
        window_frame = Frame(self)
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
        radiobutton_frame = Frame(self)
        radiobuttons.append(Radiobutton(radiobutton_frame, text="All", variable=self.current_radio_button,
                                             value=0, command=lambda:self.radioButtonChange()))
        radiobuttons[0].grid(column=0, row=0)
        radiobuttons[0].select()
        for i in range(1, 7):
            radiobuttons.append(Radiobutton(radiobutton_frame, text=i, variable=self.current_radio_button,
                                                 value=i, command=lambda:self.radioButtonChange()))
            radiobuttons[i].grid(column=i, row=0)
        return radiobutton_frame

    def initTargetFrame(self):
        frame = Frame(self)
        MyWindows.newFreqTextBox(frame, "Freq:", 0, 0, self.target_textboxes)
        disable_checkbox = Checkbutton(frame, text="Disable", variable=self.disable_checkbox_var, command=lambda: self.disableButtonChange())
        disable_checkbox.grid(row=0, column=2, padx=5, pady=5, columnspan=2)
        MyWindows.newTextBox(frame, "Width:", 0, 1, self.target_textboxes)
        MyWindows.newTextBox(frame, "Height:", 2, 1, self.target_textboxes)
        MyWindows.newColorButton(4, 1, self.targetColor, frame, "Color1", self.target_textboxes, self.target_color_buttons)
        MyWindows.newColorButton(4, 2, self.targetColor, frame, "Color2", self.target_textboxes, self.target_color_buttons)
        MyWindows.newTextBox(frame, "x:", 0, 2, self.target_textboxes)
        MyWindows.newTextBox(frame, "y:", 2, 2, self.target_textboxes)
        self.loadValues(0)
        for key in self.target_color_buttons:
            MyWindows.changeButtonColor(self.target_color_buttons[key], self.target_textboxes[key])
        return frame

    def initButtonFrame(self, button_names, commands, start_column=0):
        frame=Frame()
        for i in range(len(button_names)):
            Button(frame, text=button_names[i], command=lambda i=i: commands[i]()).grid(column=start_column+i, row=0, padx=5, pady=5)
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
        self.start_button = Button(button_frame2, text="Start", command=lambda: self.start())
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        record_frame = self.initButtonFrame(["Neutral", "Target"],
                                            [self.recordNeutral, self.recordTarget], 2)
        Label(record_frame, text="Record").grid(column=0, row=0, padx=5, pady=5)
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
        self.sendMessage(self.main_to_detection, "Exit", "PS")
        self.sendMessage(self.main_to_psychopy, "Exit", "psychopy")
        self.sendMessage(self.main_to_plot, "Exit", "plot")
        self.main_to_emo.send("Exit")
        self.destroy()

    def extraction(self):
        self.main_to_detection.append(self.newProcess(Main.runPSIdentification, "New pipe", self.sensor_names, self.detection_to_psychopy))

    def getEnabledTargets(self):
        targets = []
        for target in self.targets[1:]:
            if target["Disable"] == 0:
                targets.append(target)
        return targets

    def getChosenFreq(self):
        freq = []
        for i in range(1, len(self.targets)):
            freq.append(float(self.targets[i]["Freq"]))
        return freq

    def start(self):
        self.saveValues(self.current_radio_button.get())
        self.start_button.configure(text="Stop", command=lambda: self.stop())
        self.sendMessage(self.main_to_plot, "Start", "plot")
        self.sendMessage(self.main_to_psychopy, "Start", "psychopy")
        targets = self.getEnabledTargets()
        self.sendMessage(self.main_to_psychopy, targets, "psychopy")
        freq = self.getChosenFreq()
        self.sendMessage(self.main_to_detection, "Start", "Ps")
        self.sendMessage(self.main_to_detection, freq, "Ps")
        self.main_to_emo.send("Start")

    def sendMessage(self, connections, message, name):
        for i in range(len(connections)-1, -1, -1):
            if connections[i].poll():
                print "Main to " + name + " closed"
                connections[i].close()
                del connections[i]
            else:
                connections[i].send(message)

    def stop(self):
        self.start_button.configure(text="Start", command=lambda: self.start())
        self.sendMessage(self.main_to_plot, "Stop", "plot")
        self.sendMessage(self.main_to_psychopy, "Stop", "psychopy")
        self.sendMessage(self.main_to_detection, "Stop", "PS")
        self.main_to_emo.send("Stop")

    def newProcess(self, func, message, *args):
        main_to_new, new_to_main = multiprocessing.Pipe()
        emo_to_new, new_to_emo = multiprocessing.Pipe()
        p = multiprocessing.Process(target=func, args=(new_to_main, new_to_emo, args))
        p.start()
        self.main_to_emo.send(message)
        reduced = reduction.reduce_connection(emo_to_new)
        self.main_to_emo.send(reduced)
        return main_to_new

    def targetsWindow(self):
        self.saveValues(self.current_radio_button.get())
        bk = {}
        for key in self.background_textboxes:
            bk[key] = self.background_textboxes[key].get()
        self.main_to_psychopy.append(self.newProcess(Main.runPsychopy, "Psychopy", bk, self.psychopy_to_detection))

    def plotWindow(self):
        self.main_to_plot.append(self.newProcess(Main.runPlotControl, "New pipe", self.sensor_names))

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
                self.target_textboxes[key].delete(0, END)
                if valid:
                    self.target_textboxes[key].insert(0, str(self.targets[0][key]))
        else:
            for key in self.target_textboxes:
                self.target_textboxes[key].delete(0, END)
                self.target_textboxes[key].insert(0, str(self.targets[index][key]))
        for key in self.target_color_buttons:
            MyWindows.changeButtonColor(self.target_color_buttons[key], self.target_textboxes[key])
        self.disable_checkbox_var.set(self.targets[index]["Disable"])

    def saveValues(self, index):
        MyWindows.validateFreq(self.target_textboxes["Freq"])
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
            self.target_textboxes[key].config(state=NORMAL)
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
                self.target_textboxes[key].config(state=NORMAL)

        # if self.current_radio_button.get() == 0:
        #     value = self.targets[0]
        #     if self.all_disable:
        #         for i in range(1, len(self.targets)):
        #             self.targets[i]["Disable"] = value
        #     # self.disable_prev_value = value

    def recordTarget(self):
        self.sendMessage(self.main_to_psychopy, "Start", "psychopy")
        targets = self.getEnabledTargets()
        self.sendMessage(self.main_to_psychopy, targets, "psychopy")
        self.main_to_emo.send("Start")

    def recordNeutral(self):
        pass

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
            j = 1
            line = file.readline()
            values = line.split()
            k = 0
            for key in sorted(self.background_textboxes):
                self.background_textboxes[key].delete(0, END)
                self.background_textboxes[key].insert(0, values[k])
                k += 1
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