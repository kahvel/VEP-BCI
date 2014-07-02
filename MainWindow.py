__author__ = 'Anti'

from Tkinter import *
import TargetsWindow
import MyWindows
import PlotWindow
import MyEmotiv
import FFTWindow
import tkFileDialog


class MainWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "Main Menu", 310, 400)
        self.buttons = []
        self.radiobuttons = []
        self.target_textboxes = {}
        self.background_textboxes = {}
        self.targets = []
        self.initial = {"Height": 100,
                    "Width": 100,
                    "x": 10,
                    "y": 10,
                    "Freq": 10,
                    "Color1": "#000000",
                    "Color2": "#ffffff"}
        self.targets.append(self.initial)
        self.targets.append(self.initial.copy())
        self.target_color_buttons = {}
        self.background_color_buttons = {}
        self.plot_window = None
        self.fft_window = None
        self.average_fft_window = None
        self.average_plot_window = None
        self.initElements()
        self.myEmotiv = MyEmotiv.myEmotiv()
        self.mainloop()

    def initElements(self):

        windowtitleframe = Frame(self)
        Label(windowtitleframe, text="Window").grid(column=0, row=0, padx=5, pady=5)

        self.windowframe = Frame(self)
        MyWindows.newTextBox(self.windowframe, "Width:", 0, 0, self.background_textboxes)
        MyWindows.newTextBox(self.windowframe, "Height:", 2, 0, self.background_textboxes)
        MyWindows.newColorButton(4, 0, self.backgroundColor, self.windowframe,
                             "Color", self.background_textboxes, self.background_color_buttons)

        self.background_textboxes["Width"].insert(0, 800)
        self.background_textboxes["Height"].insert(0, 600)
        self.background_textboxes["Color"].insert(0, "#eeeeee")

        targettitleframe = Frame(self)
        self.radiobuttonframe = Frame(self)

        self.current_radio_button = IntVar()
        self.previous_radio_button = 0

        Label(targettitleframe, text="Targets").grid(column=0, row=0, padx=5, pady=5)

        targetbuttonframe = Frame(self)

        Button(targetbuttonframe, text="Add", command=lambda:self.addTarget()).grid(column=1, row=0, padx=5, pady=5)
        Button(targetbuttonframe, text="Remove", command=lambda:self.removeTarget()).grid(column=2, row=0, padx=5, pady=5)


        self.radiobuttons.append(Radiobutton(self.radiobuttonframe, text="All", variable=self.current_radio_button,
                                             value=0, command=lambda:self.radioButtonChange()))
        self.radiobuttons[0].grid(column=0, row=0)
        self.radiobuttons.append(Radiobutton(self.radiobuttonframe, text="1", variable=self.current_radio_button,
                                             value=1, command=lambda:self.radioButtonChange()))
        self.radiobuttons[1].grid(column=1, row=0)
        self.radiobuttons[0].select()

        targetframe = Frame(self)

        self.newTarget(targetframe)
        self.loadValues(0)
        for key in self.target_color_buttons:
            MyWindows.changeButtonColor(self.target_color_buttons[key], self.target_textboxes[key])
        MyWindows.changeButtonColor(self.background_color_buttons["Color"], self.background_textboxes["Color"])

        buttonframe = Frame(self)

        self.buttons.append(Button(buttonframe, text="Targets", command=lambda: self.targetsWindow()))
        self.buttons.append(Button(buttonframe, text="Plot", command=lambda: self.plot()))
        self.buttons.append(Button(buttonframe, text="Avg", command=lambda: self.avgPlot()))
        self.buttons.append(Button(buttonframe, text="FFT", command=lambda: self.fft()))
        self.buttons.append(Button(buttonframe, text="Avg", command=lambda: self.avgFft()))
        self.buttons.append(Button(buttonframe, text="Start", command=lambda: self.run()))
        self.buttons.append(Button(buttonframe, text="Load", command=lambda: self.loadFile()))
        self.buttons.append(Button(buttonframe, text="Save", command=lambda: self.saveFile()))
        self.buttons.append(Button(buttonframe, text="Exit", command=lambda: self.exit()))

        for i in range(5):
            self.buttons[i].grid(column=i, row=0, padx=5, pady=5)
        for i in range(5, len(self.buttons)):
            self.buttons[i].grid(column=i-5, row=1, padx=5, pady=5)

        windowtitleframe.grid(column=0, row=0)
        self.windowframe.grid(column=0, row=1)
        targettitleframe.grid(column=0, row=2)
        targetbuttonframe.grid(column=0, row=3)
        self.radiobuttonframe.grid(column=0, row=4)
        targetframe.grid(column=0, row=5)
        buttonframe.grid(column=0, row=6)

    def targetsWindow(self):
        self.saveValues(self.current_radio_button.get())
        TargetsWindow.TargetsWindow(self.background_textboxes, self.targets)

    def plot(self):
        self.plot_window = PlotWindow.PlotWindow()

    def avgFft(self):
        self.average_fft_window = FFTWindow.AverageFFTWindow()

    def avgPlot(self):
        self.average_plot_window = PlotWindow.AveragePlotWindow()

    def fft(self):
        self.fft_window = FFTWindow.FFTWindow()

    def run(self):
        self.myEmotiv.setFFT(self.fft_window)
        self.myEmotiv.setPlot(self.plot_window)
        self.myEmotiv.setAverageFFT(self.average_fft_window)
        self.myEmotiv.setAveragePlot(self.average_plot_window)
        self.myEmotiv.run()
        self.fft_window = None
        self.plot_window = None
        self.average_fft_window = None
        self.average_plot_window = None

    def loadValues(self, index):
        if index == 0:
            for key in self.target_textboxes:
                valid = False
                #value1 = None
                #value2 = None
                #exec("value1 = self.targets[0]."+key.lower())
                value1 = self.targets[0][key]
                for i in range(1, len(self.targets)):
                    #exec("value2 = self.targets[i]."+key.lower())
                    value2 = self.targets[i][key]
                    if value1 != value2:
                        valid = False
                        break
                    else:
                        valid = True
                self.target_textboxes[key].delete(0, END)
                if valid:
                    self.target_textboxes[key].insert(0, str(value1))

        else:
            for key in self.target_textboxes:
                self.target_textboxes[key].delete(0, END)
                #exec("self.textboxes[key].insert(0,str(self.targets[index]."+key.lower()+"))")
                self.target_textboxes[key].insert(0, str(self.targets[index][key]))
        for key in self.target_color_buttons:
            MyWindows.changeButtonColor(self.target_color_buttons[key], self.target_textboxes[key])

    def saveValues(self, index):
        if index == 0:
            for key in self.target_textboxes:
                if self.target_textboxes[key].get() != "":
                    for target in self.targets:
                        #exec("target."+key.lower()+"= self.textboxes[key].get()")
                        target[key] = self.target_textboxes[key].get()
        for key in self.target_textboxes:
            #exec("self.targets[index]."+key.lower()+"= self.textboxes[key].get()")
            self.targets[index][key] = self.target_textboxes[key].get()

    def radioButtonChange(self):
        self.saveValues(self.previous_radio_button)
        self.loadValues(self.current_radio_button.get())
        self.previous_radio_button = self.current_radio_button.get()

    def removeTarget(self):
        if len(self.radiobuttons) > 2:
            self.radiobuttons[len(self.radiobuttons)-1].grid_forget()
            del self.radiobuttons[-1]
            del self.targets[-1]

    def addTarget(self):
        if len(self.radiobuttons) < 7:
            self.radiobuttons.append(Radiobutton(self.radiobuttonframe, text=str(len(self.radiobuttons)),
                                                 variable=self.current_radio_button, value=len(self.radiobuttons),
                                                 command=lambda:self.radioButtonChange()))
            self.radiobuttons[len(self.radiobuttons)-1].grid(column=len(self.radiobuttons)-1, row=0)
            self.targets.append(self.initial.copy())
            self.defaultValues()


    def defaultValues(self):
        for key in self.targets[0]:
            value1 = None
            #exec("value1 = self.targets[0]."+key)
            value1 = self.targets[0][key]
            if value1 != "":
                #exec("self.targets[-1]."+key+"= value1")
                self.targets[-1][key] = value1

    def newTarget(self, frame):
        MyWindows.newTextBox(frame, "Width:", 0, 0, self.target_textboxes)
        MyWindows.newTextBox(frame, "Height:", 2, 0, self.target_textboxes)
        MyWindows.newColorButton(4, 0, self.targetColor, frame, "Color1", self.target_textboxes, self.target_color_buttons)
        MyWindows.newColorButton(4, 1, self.targetColor, frame, "Color2", self.target_textboxes, self.target_color_buttons)
        MyWindows.newTextBox(frame, "x:", 0, 1, self.target_textboxes)
        MyWindows.newTextBox(frame, "y:", 2, 1, self.target_textboxes)
        MyWindows.newTextBox(frame, "Freq:", 0, 2, self.target_textboxes)

    def saveFile(self):
        self.saveValues(self.current_radio_button.get())
        file = tkFileDialog.asksaveasfile()
        if file is not None:
            for key in sorted(self.background_textboxes):
                file.write(self.background_textboxes[key].get()+" ")
            file.write("\n")
            for target in self.targets:
                for key in sorted(target):
                    #exec("file.write(str(target."+key+")+' ')")
                    file.write(str(target[key]+" "))
                file.write("\n")
            file.close()
        #SaveWindow(self.targets, self, self.background_textboxes)

    def loadFile(self):
        # LoadWindow(self.targets, self, self.background_textboxes)
        file = tkFileDialog.askopenfile()
        if file is not None:
            j = 0
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
                    #exec("target."+key+"=values[i]")
                    target[key] = values[i]
                    i += 1
                j += 1
            self.loadValues(self.current_radio_button.get())

    def targetColor(self, title):
        TargetColorWindow(self, self.target_textboxes[title], title, self.targets[self.current_radio_button.get()],
                          self.target_color_buttons[title])

    def backgroundColor(self, title):
        BackgroundColorWindow(self, self.background_textboxes[title], title, self.background_color_buttons[title])

class ChildWindow(MyWindows.ToplevelWindow):
    def __init__(self, title, width, height, parent, column, row):
        MyWindows.ToplevelWindow.__init__(self, title, width, height)
        parent_location = parent.geometry().split("+")
        parent_size = parent_location[0].split("x")
        self.geometry("+"+str(int(parent_location[1])+int(int(parent_size[0])/2)-width/2)+"+"
                             +str(int(parent_location[2])+int(int(parent_size[1])/2)-height/2))
        Button(self, text=title, command=lambda:self.function()).grid(column=column, row=row, padx=5, pady=5)
        Button(self, text="Cancel", command=lambda:self.exit()).grid(column=column+1, row=row, padx=5, pady=5)

class ColorWindow(ChildWindow):
    def __init__(self, parent, title):
        ChildWindow.__init__(self, title, 250, 250, parent, 0, 5)
        self.scales = []
        self.title = title
        self.canvas = Canvas(self, width=50, height=50)
        self.canvas.grid(column=0, row=4)
        self.initElements()

    def initElements(self):
        self.scales.append(Scale(self, from_=0, to=255, orient=HORIZONTAL, command=lambda x:self.newColor()))
        self.scales.append(Scale(self, from_=0, to=255, orient=HORIZONTAL, command=lambda x:self.newColor()))
        self.scales.append(Scale(self, from_=0, to=255, orient=HORIZONTAL, command=lambda x:self.newColor()))
        for i in range(len(self.scales)):
            self.scales[i].grid(column=0, row=i)

    def getColor(self):
        return "#%02x%02x%02x" % (self.scales[0].get(), self.scales[1].get(), self.scales[2].get())

    def newColor(self):
        self.canvas.configure(background=self.getColor())

class TargetColorWindow(ColorWindow):
    def __init__(self, parent, textbox, title, target, button):
        ColorWindow.__init__(self, parent, title)
        self.function = self.choose
        self.target = target
        self.textbox = textbox
        self.button = button
        #self.focus()

    def choose(self):
        self.textbox.delete(0, END)
        self.textbox.insert(0, self.getColor())
        #exec("self.target."+self.title.lower()+"=self.getColor()")
        self.target[self.title] = self.getColor()
        MyWindows.changeButtonColor(self.button, self.textbox)
        self.exit()

class BackgroundColorWindow(ColorWindow):
    def __init__(self, parent, textbox, title, button):
        ColorWindow.__init__(self, parent, title)
        self.function = self.choose
        self.textbox = textbox
        self.button = button
        #self.focus()

    def choose(self):
        self.textbox.delete(0, END)
        self.textbox.insert(0, self.getColor())
        MyWindows.changeButtonColor(self.button, self.textbox)
        self.exit()

# class LoadSaveWindow(ChildWindow):
#     def __init__(self, title, parent, targets, column, row):
#         ChildWindow.__init__(self, title, 160, 100, parent, column, row)
#
#         self.targets = targets
#         #self.text = title
#         self.textbox = None
#         self.file_name = None
#         self.initElements()
#
#     def initElements(self):
#         self.textbox = newTextBox(self, "File name", 0, 0, 10)
#
# class LoadWindow(LoadSaveWindow):
#     def __init__(self, targets, parent, background_textboxes):
#         LoadSaveWindow.__init__(self, "Load", parent, targets, 0, 1)
#         self.function = self.load
#         self.background_textboxes = background_textboxes
#         self.focus()
#
#     def load(self):
#         self.file_name = self.textbox.get() # is it valid?
#         file = open(self.file_name, "r")
#         j = 0
#         line = file.readline()
#         values = line.split()
#         k = 0
#         for key in sorted(self.background_textboxes):
#             self.background_textboxes[key].delete(0, END)
#             self.background_textboxes[key].insert(0, values[k])
#             k += 1
#         for line in file:
#             values = line.split()
#             target = self.targets[j]
#             i = 0
#             for key in sorted(target.__dict__):
#                 exec("target."+key+"=values[i]")
#                 i += 1
#             j += 1
#         self.exit()
#
#
# class SaveWindow(LoadSaveWindow):
#     def __init__(self, targets, parent, background_textboxes):
#         LoadSaveWindow.__init__(self, "Save", parent, targets, 0, 1)
#         self.function = self.save
#         self.background_textboxes = background_textboxes
#         self.focus()
#
#     def save(self):
#         self.file_name = self.textbox.get() # is it valid?
#         file = open(self.file_name, "w")
#         for key in sorted(self.background_textboxes):
#             file.write(self.background_textboxes[key].get()+" ")
#         file.write("\n")
#         for target in self.targets:
#             for key in sorted(target.__dict__):
#                 exec("file.write(str(target."+key+")+' ')")
#             file.write("\n")
#         file.close()
#         self.exit()