__author__ = 'Anti'

import MyWindows
import Tkinter


class ChildWindow(MyWindows.ToplevelWindow):
    def __init__(self, title, width, height, parent, column, row):
        MyWindows.ToplevelWindow.__init__(self, title, width, height)
        parent_location = parent.geometry().split("+")
        parent_size = parent_location[0].split("x")
        self.geometry("+"+str(int(parent_location[1])+int(int(parent_size[0])/2)-width/2)+"+"
                             +str(int(parent_location[2])+int(int(parent_size[1])/2)-height/2))
        buttonframe = Tkinter.Frame(self)
        Tkinter.Button(buttonframe, text="Choose", command=lambda:self.choose()).grid(column=column, row=row, padx=5, pady=5)
        Tkinter.Button(buttonframe, text="Cancel", command=lambda:self.exit()).grid(column=column+1, row=row, padx=5, pady=5)
        buttonframe.grid(column=0, row=5)


class ColorWindow(ChildWindow):
    def __init__(self, parent, title):
        ChildWindow.__init__(self, title, 125, 250, parent, 0, 5)
        self.scales = []
        self.title = title
        self.canvas = Tkinter.Canvas(self, width=50, height=50)
        self.canvas.grid(column=0, row=4)
        self.initElements()

    def initElements(self):
        self.scales.append(Tkinter.Scale(self, from_=0, to=255, orient=Tkinter.HORIZONTAL, command=lambda x: self.newColor()))
        self.scales.append(Tkinter.Scale(self, from_=0, to=255, orient=Tkinter.HORIZONTAL, command=lambda x: self.newColor()))
        self.scales.append(Tkinter.Scale(self, from_=0, to=255, orient=Tkinter.HORIZONTAL, command=lambda x: self.newColor()))
        for i in range(len(self.scales)):
            self.scales[i].grid(column=0, row=i)

    def getColor(self):
        return "#%02x%02x%02x" % (self.scales[0].get(), self.scales[1].get(), self.scales[2].get())

    def newColor(self):
        self.canvas.configure(background=self.getColor())


class TargetColorWindow(ColorWindow):
    def __init__(self, parent, textbox, title, target, button):
        ColorWindow.__init__(self, parent, title)
        self.target = target
        self.textbox = textbox
        self.button = button

    def choose(self):
        self.textbox.delete(0, Tkinter.END)
        self.textbox.insert(0, self.getColor())
        self.target[self.title] = self.getColor()
        MyWindows.changeButtonColor(self.button, self.textbox)
        self.exit()


class BackgroundColorWindow(ColorWindow):
    def __init__(self, parent, textbox, title, button):
        ColorWindow.__init__(self, parent, title)
        self.textbox = textbox
        self.button = button

    def choose(self):
        self.textbox.delete(0, Tkinter.END)
        self.textbox.insert(0, self.getColor())
        MyWindows.changeButtonColor(self.button, self.textbox)
        self.exit()