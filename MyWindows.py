__author__ = 'Anti'

import Tkinter


class TkWindow(Tkinter.Tk):

    def __init__(self, title, width, height, color="#eeeeee"):
        Tkinter.Tk.__init__(self)
        self.title(title)
        self.geometry(str(width)+"x"+str(height))
        self.resizable(0,0)
        self.configure(background=color)

        #self.protocol("WM_DELETE_WINDOW", self.exit)

    def exit(self):
        self.destroy() #quit siia

    def focus(self):
        #self.focus_set() # not working. Load crashes...
        #self.grab_set()
        #self.transient(parent)
        self.wait_window(self)

class ToplevelWindow(Tkinter.Toplevel):

    def __init__(self, title, width, height, color="#eeeeee"):
        Tkinter.Toplevel.__init__(self)
        self.title(title)
        self.geometry(str(width)+"x"+str(height))
        self.resizable(0,0)
        self.configure(background=color)
        #self.protocol("WM_DELETE_WINDOW", self.iconify)


    def setProtocol(self, name, function):
        self.protocol(name, function)
    def a(self):
        print "jou"

    def exit(self):
        self.destroy()

    def focus(self):
        #self.focus_set() # not working. Load crashes...
        #self.grab_set()
        #self.transient(parent)
        self.wait_window(self)

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