__author__ = 'Anti'

import AbstractWidget
import Tkinter


class Frame(AbstractWidget.Widget):
    def __init__(self, name, row, column, columnspan=1, padx=5, pady=5):
        AbstractWidget.Widget.__init__(self, name, row, column, columnspan, padx, pady)
        self.widgets_list = []
        self.widgets_dict = {}

    def addChildWidgets(self, child_widgets):
        for widget in child_widgets:
            self.widgets_list.append(widget)
            self.widgets_dict[widget.name] = widget

    def createWidget(self, parent):
        widget = Tkinter.Frame(parent)
        self.createChildWidgets(widget)
        return widget

    def createChildWidgets(self, parent):
        for child in self.widgets_list:
            child.create(parent)

    def enable(self, enabler):
        for child in self.widgets_list:
            child.enable(enabler)

    def disable(self, disabler):
        for child in self.widgets_list:
            child.disable(disabler)

    def changeState(self, changer):
        for child in self.widgets_list:
            child.changeState(changer)

    def loadDefaultValue(self):
        for child in self.widgets_list:
            child.loadDefaultValue()

    def conditionalDisabling(self, variable, widgets, value):
        for widget in widgets:
            if variable.get() == value:
                widget.enable(self.name)
            else:
                widget.disable(self.name)


class NotebookFrame(Frame):
    def __init__(self, name, row, column, columnspan, padx, pady):
        Frame.__init__(self, name, row, column, columnspan, padx, pady)
