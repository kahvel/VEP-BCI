__author__ = 'Anti'

import ttk

from gui.widgets.frames import Frame


class Notebook(Frame.AbstractFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.AbstractFrame.__init__(self, name, row, column, **kwargs)
        self.create(ttk.Notebook(parent))

    def addChildWidgets(self, child_widgets):
        Frame.AbstractFrame.addChildWidgets(self, child_widgets)
        self.createChildWidgets()

    def createChildWidgets(self):
        for widget in self.widgets_list:
            self.widget.add(widget.widget, text=widget.name)
