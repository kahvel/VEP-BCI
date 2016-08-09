import Tkinter

from gui_elements.widgets import AbstractWidget
from messaging.gui_messaging import MessagingInterface


class AbstractFrame(AbstractWidget.Widget, MessagingInterface.FrameMessageHandler):
    def __init__(self, parent, name, row, column, **kwargs):
        AbstractWidget.Widget.__init__(self, parent, name, row, column, **kwargs)
        MessagingInterface.FrameMessageHandler.__init__(self, parent, [])
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
        widget.widget.destroy()

    def enable(self, enabler):
        AbstractWidget.Widget.enable(self, enabler)
        for child in self.widgets_list:
            child.enable(enabler)

    def disable(self, disabler):
        AbstractWidget.Widget.disable(self, disabler)
        for child in self.widgets_list:
            child.disable(disabler)

    def loadDefaultValue(self):
        AbstractWidget.Widget.loadDefaultValue(self)
        for child in self.widgets_list:
            child.loadDefaultValue()

    def conditionalDisabling(self, disabler, values_when_enabled, widgets):
        for widget in widgets:
            if disabler.variable.get() in values_when_enabled:
                widget.enable(disabler.name)
            else:
                widget.disable(disabler.name)

    def validate(self):
        return all(map(lambda x: x.validate(), self.widgets_list))

    def getNotValidated(self):
        if len(self.widgets_dict) != 0:
            return {key: self.widgets_dict[key].getNotValidated() for key in self.widgets_dict if not self.widgets_dict[key].validate()}
        else:
            return {index: self.widgets_list[index].getNotValidated() for index in range(len(self.widgets_list)) if not self.widgets_list[index].validate()}

    def getValue(self):
        if len(self.widgets_dict) != 0:
            return {key: widget.getValue() for key, widget in self.widgets_dict.items() if not widget.no_value}

    def disableWidget(self, path_to_widget, disabler="PostOffice"):
        if len(path_to_widget) > 1:
            self.widgets_dict[path_to_widget[0]].disableWidget(path_to_widget[1:], disabler)
        else:
            self.widgets_dict[path_to_widget[0]].disable(disabler)

    def enableWidget(self, path_to_widget, enabler="PostOffice"):
        if len(path_to_widget) > 1:
            self.widgets_dict[path_to_widget[0]].enableWidget(path_to_widget[1:], enabler)
        else:
            self.widgets_dict[path_to_widget[0]].enable(enabler)


class Frame(AbstractFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        AbstractFrame.__init__(self, parent, name, row, column, **kwargs)
        self.create(Tkinter.Frame(parent.widget))
