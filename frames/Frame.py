__author__ = 'Anti'

from widgets import AbstractWidget
import Tkinter


class Frame(AbstractWidget.Widget):
    def __init__(self, name, row, column, columnspan=1, padx=5, pady=5):
        AbstractWidget.Widget.__init__(self, name, row, column, columnspan, padx, pady)
        self.widgets_list = []
        self.widgets_dict = {}

    def addChildWidgets(self, child_widgets):
        for widget in child_widgets:
            self.addWidget(widget)

    def addWidget(self, widget):
        self.widgets_list.append(widget)
        self.widgets_dict[widget.name] = widget

    def removeWidget(self, widget):
        self.widgets_list.remove(widget)
        del self.widgets_dict[widget.name]

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

    def save(self, file):
        for widget in self.widgets_list:
            widget.save(file)

    def load(self, file):
        for widget in self.widgets_list:
            widget.load(file)
