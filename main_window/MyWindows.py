__author__ = 'Anti'

import Tkinter
import tkColorChooser


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


def saveColor(color_buttons, textboxes, name):
    if name in textboxes:
        previous = textboxes[name].get()
        textboxes[name].delete(0, Tkinter.END)
        textboxes[name].insert(0, tkColorChooser.askcolor(previous)[1])
        changeButtonColor(color_buttons[name], textboxes[name])


def newColorButton(column, row, frame, name, textboxes, color_buttons):
    color_buttons[name] = Tkinter.Button(frame, text=name, command=lambda: saveColor(color_buttons, textboxes, name))
    color_buttons[name].grid(column=column, row=row, padx=5, pady=5)
    textbox = Tkinter.Entry(frame, width=7, validate="focusout", validatecommand=lambda: changeButtonColor(color_buttons[name], textboxes[name]))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    return textbox


def newTextBox(frame, text, column, row, width=5, validatecommand=None):
    Tkinter.Label(frame, text=text+":").grid(column=column, row=row, padx=5, pady=5)
    if validatecommand is None:
        textbox = Tkinter.Entry(frame, width=width)
    else:
        textbox = Tkinter.Entry(frame, width=width, validate="focusout", validatecommand=lambda: validatecommand(textbox))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    return textbox