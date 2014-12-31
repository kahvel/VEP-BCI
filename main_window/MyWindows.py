__author__ = 'Anti'

import Tkinter
import tkColorChooser


sensor_names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
headset_freq = 128


class AbstractWindow(object):
    def __init__(self, title, width, height, color="#eeeeee"):
        self.window_width = width
        self.window_height = height
        self.name = title
        self.title(title)
        self.resizable(0, 0)
        self.configure(background=color)

    def exit(self):
        self.destroy()


class TkWindow(AbstractWindow, Tkinter.Tk):
    def __init__(self, title, width, height, color="#eeeeee"):
        Tkinter.Tk.__init__(self)
        AbstractWindow.__init__(self, title, width, height, color)


class ToplevelWindow(AbstractWindow, Tkinter.Toplevel):
    def __init__(self, title, width, height, color="#eeeeee"):
        Tkinter.Toplevel.__init__(self)
        AbstractWindow.__init__(self, title, width, height, color)


def changeButtonColor(button, textbox):
    try:
        button.configure(background=textbox.get())
    except:
        button.configure(background="#eeeeee")
        return False
    return True


def saveColor(button, textbox):
    previous = textbox.get()
    textbox.delete(0, Tkinter.END)
    textbox.insert(0, tkColorChooser.askcolor(previous)[1])
    changeButtonColor(button, textbox)


def newColorButton(frame, name, column=0, row=0):
    button = Tkinter.Button(frame, text=name)
    button.grid(column=column, row=row, padx=5, pady=5)
    textbox = Tkinter.Entry(frame, width=7, validate="focusout", validatecommand=lambda: changeButtonColor(button, textbox))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    button.config(command=lambda: saveColor(button, textbox))
    return textbox, button


def newTextBox(frame, text, column=0, row=0, width=5, validatecommand=None):
    Tkinter.Label(frame, text=text+":").grid(column=column, row=row, padx=5, pady=5)
    if validatecommand is None:
        textbox = Tkinter.Entry(frame, width=width)
    else:
        textbox = Tkinter.Entry(frame, width=width, validate="focusout", validatecommand=lambda: validatecommand(textbox))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    return textbox


def newCheckbox(frame, text, column=0, row=0, columnspan=2, padx=5, pady=5):
    var = Tkinter.IntVar()
    button = Tkinter.Checkbutton(frame, text=text, variable=var)
    button.grid(column=column, row=row, padx=padx, pady=pady, columnspan=columnspan)
    return var, button


def updateTextbox(textbox, value):
    textbox.delete(0, Tkinter.END)
    textbox.insert(0, value)


def updateVar(var, value):
    var.set(value)


def initButtonFrame(frame, button_names, commands, column=0, row=0):
    buttons = {}
    for i in range(len(button_names)):
        buttons[button_names[i]] = (Tkinter.Button(frame, text=button_names[i],command=commands[i]))
        buttons[button_names[i]].grid(column=column+i, row=row, padx=5, pady=5)
    return buttons
