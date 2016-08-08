from gui_elements.widgets.frames import Frame
from gui_elements.widgets import Checkbutton


class AddingCheckbuttonsFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, initial_tabs, buttons_in_row=7, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, **kwargs)
        self.disabled_tabs = []
        self.buttons_in_row = buttons_in_row
        self.target_notebook_widgets = None

    def loadDefaultValue(self):
        """
        Assume that by default there is one tab and it is not disabled.
        :return:
        """
        Frame.Frame.loadDefaultValue(self)
        self.evokeGetTargetNotebookWidgetsEvent()
        for widget in self.target_notebook_widgets:
            self.addButton(widget.disabled)

    def evokeGetTargetNotebookWidgetsEvent(self):
        self.sendEventToAll(lambda x: x.getTargetNotebookWidgetsEvent())

    def sendTargetNotebookWidgetsEvent(self, target_notebook_widgets):
        self.target_notebook_widgets = target_notebook_widgets

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
