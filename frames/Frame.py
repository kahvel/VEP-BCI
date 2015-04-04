__author__ = 'Anti'

from widgets import AbstractWidget
import Tkinter


class AbstractFrame(AbstractWidget.Widget):
    def __init__(self, parent, name, row, column, **kwargs):
        AbstractWidget.Widget.__init__(self, name, row, column, **kwargs)
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

    def enable(self, enabler):
        for child in self.widgets_list:
            child.enable(enabler)

    def disable(self, disabler):
        for child in self.widgets_list:
            child.disable(disabler)

    def loadDefaultValue(self):
        for child in self.widgets_list:
            child.loadDefaultValue()

    def conditionalDisabling(self, disabler, value, widgets):
        for widget in widgets:
            if disabler.variable.get() == value:
                widget.enable(disabler.name)
            else:
                widget.disable(disabler.name)

    def save(self, file):
        for widget in self.widgets_list:
            widget.save(file)

    def load(self, file):
        for widget in self.widgets_list:
            widget.load(file)

    def validate(self):
        return all(map(lambda x: x.validate(), self.widgets_list))

    def getNotValidated(self):
        if len(self.widgets_dict) != 0:
            return {key: self.widgets_dict[key].getNotValidated() for key in self.widgets_dict if not self.widgets_dict[key].validate()}
        else:
            return {index: self.widgets_list[index].getNotValidated() for index in range(len(self.widgets_list)) if not self.widgets_list[index].validate()}

    def getValue(self):
        if len(self.widgets_dict) != 0:
            return {key: self.widgets_dict[key].getValue() for key in self.widgets_dict}
        else:
            return {index: self.widgets_list[index].getValue() for index in range(len(self.widgets_list))}


class Frame(AbstractFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        AbstractFrame.__init__(self, parent, name, row, column, **kwargs)
        self.create(Tkinter.Frame(parent))
