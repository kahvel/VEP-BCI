__author__ = 'Anti'

import Tkinter


class AbstractWindow(object):
    def __init__(self, title, width, height, color="#eeeeee"):
        self.title(title)
        self.geometry(str(width)+"x"+str(height))
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


def newColorButton(column, row, function, frame, title, textboxes, color_buttons):
    color_buttons[title] = Tkinter.Button(frame, text=title, command=lambda:function(title))
    color_buttons[title].grid(column=column, row=row, padx=5, pady=5)
    textbox = Tkinter.Entry(frame, width=7, validate="focusout",
                    validatecommand=lambda: changeButtonColor(color_buttons[title], textboxes[title]))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    textboxes[title] = textbox


def newTextBox(frame, text, column, row, textboxes, width=5):
    Tkinter.Label(frame, text=text).grid(column=column, row=row, padx=5, pady=5)
    textbox = Tkinter.Entry(frame, width=width)
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    textboxes[text[:-1]] = textbox


def newFreqTextBox(frame, text, column, row, textboxes, width=5):
    Tkinter.Label(frame, text=text).grid(column=column, row=row, padx=5, pady=5)
    textbox = Tkinter.Entry(frame, width=width, validate="focusout", validatecommand=lambda: validateFreq(textbox))
    textbox.grid(column=column+1, row=row, padx=5, pady=5)
    textboxes[text[:-1]] = textbox


def validateFreq(textbox):
    freq = float(textbox.get())
    freq_on = int(60/freq//2)
    freq_off = int(60/freq/2.0+0.5)
    textbox.delete(0, Tkinter.END)
    textbox.insert(0, float(60)/(freq_off+freq_on))
    return True