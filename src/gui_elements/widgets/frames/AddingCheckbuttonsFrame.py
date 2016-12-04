from gui_elements.widgets.frames import Frame
from gui_elements.widgets import Checkbutton

import Tkinter


class AddingCheckbuttonsFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, buttons_in_row=7, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)
        self.disabled_tabs = []
        self.buttons_in_row = buttons_in_row
        self.notebook_widgets = None

    def getNotebookWidgetsEvent(self):
        raise NotImplementedError("getNotebookWidgetsEvent not implemented!")

    def setWidgetsNotebook(self, notebook_widgets):
        self.notebook_widgets = notebook_widgets

    def addButton(self, disabled=False):
        self.disabled_tabs.append(disabled)
        self.addButtonGraphics(len(self.disabled_tabs), disabled, 1)

    def getButtonRow(self, button_index):
        return button_index // self.buttons_in_row

    def getButtonColumn(self, button_index):
        return button_index % self.buttons_in_row

    def getCheckbutton(self, button_name, button_index, state):
        row = self.getButtonRow(button_index)
        column = self.getButtonColumn(button_index)
        return Checkbutton.Checkbutton(self, button_name, row, column, default_value=state, padx=0, pady=0)

    def addButtonGraphics(self, option, disabled, state):
        new_widget = self.getCheckbutton(str(option), option-1, state)
        self.addChildWidgets((new_widget,))
        new_widget.loadDefaultValue()
        if disabled:
            new_widget.disable("TargetTab")

    def addButtonsGraphics(self, button_states):
        for i, disabled in enumerate(self.disabled_tabs):
            self.addButtonGraphics(i+1, disabled, button_states[i])

    def deleteAllButtonsGraphics(self):
        for i in range(len(self.widgets_list)-1, -1, -1):
            self.removeWidget(self.widgets_list[i])

    def getCheckbuttonStates(self, deleted_tab):
        states = []
        for i in range(len(self.widgets_list)):
            if i != deleted_tab:
                states.append(self.widgets_list[i].getValue())
        return states

    def deleteButtonGraphics(self, deleted_tab):
        button_states = self.getCheckbuttonStates(deleted_tab)
        self.deleteAllButtonsGraphics()
        self.addButtonsGraphics(button_states)

    def deleteButton(self, deleted_tab):
        del self.disabled_tabs[deleted_tab]
        self.deleteButtonGraphics(deleted_tab)

    def enableButton(self, current_tab):
        self.widgets_list[current_tab].enable("TargetTab")
        self.disabled_tabs[current_tab] = False

    def disableButton(self, current_tab):
        self.widgets_list[current_tab].disable("TargetTab")
        self.disabled_tabs[current_tab] = True

    def saveBciSettingsEvent(self, file):
        file.write(str(list(int(value) for value in self.disabled_tabs)).strip("[]") + "\n")
        Frame.Frame.saveBciSettingsEvent(self, file)

    def loadBciSettingsEvent(self, file):
        disabled_tabs = file.readline().strip("\n")
        disabled_tabs_str = disabled_tabs.split(", ") if disabled_tabs != "" else []
        self.disabled_tabs = list(int(value) for value in disabled_tabs_str)
        self.deleteAllButtonsGraphics()
        for i, disabled in enumerate(self.disabled_tabs):
            self.addButtonGraphics(i+1, disabled, 1)
        Frame.Frame.loadBciSettingsEvent(self, file)


class EventNotebookAddingCheckbuttonFrame(AddingCheckbuttonsFrame):
    def __init__(self, parent, name, row, column, buttons_in_row=7, **kwargs):
        AddingCheckbuttonsFrame.__init__(self, parent, name, row, column, buttons_in_row, **kwargs)

    def loadDefaultValue(self):
        Frame.Frame.loadDefaultValue(self)
        self.getNotebookWidgetsEvent()
        for widget in self.notebook_widgets[:-1]:
            self.addButton(widget.disabled)


class PlusTabNotebookAddingCheckbuttonFrame(AddingCheckbuttonsFrame):
    def __init__(self, parent, name, row, column, buttons_in_row=7, **kwargs):
        AddingCheckbuttonsFrame.__init__(self, parent, name, row, column, buttons_in_row, **kwargs)

    def loadDefaultValue(self):
        Frame.Frame.loadDefaultValue(self)
        self.getNotebookWidgetsEvent()
        for widget in self.notebook_widgets:
            self.addButton(widget.disabled)
