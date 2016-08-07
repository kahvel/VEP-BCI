from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
from gui_elements.widgets.frames import Frame
from gui_elements.widgets import Textboxes, OptionMenu
import constants as c
import math


class TargetsNotebookTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, getMonitorFreq, deleteTab, getEnabledTabs, getCurrentTab, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.TARGETS_NOTEBOOK_TAB, **kwargs)
        self.getEnabledTabs = getEnabledTabs
        self.getCurrentTab = getCurrentTab
        self.addChildWidgets((
            TargetsNotebookTabFrame(self, 0, 0, getMonitorFreq, **kwargs),
            self.getDisableDeleteFrame(1, 0, deleteTab)
        ))

    def disable(self, disabler):  # Updates TargetChoosingMenus
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.disable(self, disabler)
        self.sendEventToRoot(lambda x: x.targetDisabledEvent(self.getEnabledTabs(), self.getCurrentTab()))

    def enable(self, enabler):  # Updates TargetChoosingMenus
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.enable(self, enabler)
        self.sendEventToRoot(lambda x: x.targetEnabledEvent(self.getEnabledTabs(), self.getCurrentTab()))


class TargetsNotebookTabFrame(Frame.Frame):
    def __init__(self, parent, row, column, getMonitorFreq, **kwargs):
        Frame.Frame.__init__(self, parent, c.TARGET_FRAME, row, column, **kwargs)
        self.getMonitorFreq = getMonitorFreq
        validate = lambda: self.changeFreq()
        increase = lambda: self.changeFreq(increase=True)
        decrease = lambda: self.changeFreq(decrease=True)
        self.addChildWidgets((
            Textboxes.PlusMinusTextboxFrame(self, c.TARGET_FREQ,   0, 0, increase, decrease, command=validate),
            OptionMenu.OptionMenu          (self, c.TARGET_TYPE,   0, 4, c.TARGET_TYPE_NAMES),
            Textboxes.SequenceTextbox      (self, c.TARGET_SEQUENCE, 1, 0, allow_zero=True, command=self.sequenceChanged, width=35, columnspan=4, label_columnspan=2),
            Textboxes.LabelTextbox         (self, c.TARGET_WIDTH,  2, 0, command=int, default_value=150),
            Textboxes.LabelTextbox         (self, c.TARGET_HEIGHT, 2, 2, command=int, default_value=150),
            Textboxes.ColorTextboxFrame    (self, c.TARGET_COLOR1, 2, 4, default_value="#ffffff"),
            Textboxes.LabelTextbox         (self, c.TARGET_X,      3, 0, command=int, allow_negative=True, allow_zero=True),
            Textboxes.LabelTextbox         (self, c.TARGET_Y,      3, 2, command=int, allow_negative=True, allow_zero=True),
            Textboxes.ColorTextboxFrame    (self, c.TARGET_COLOR0, 3, 4, default_value="#000000")
        ))

    def getTargetFreq(self):
        return float(self.getFrequencyTextbox().getValue())

    def setTargetFreq(self, value):
        self.getFrequencyTextbox().setValue(value)

    def getFrequencyTextbox(self):
        return self.widgets_dict[c.TARGET_FREQ].widgets_dict[c.TEXTBOX]

    def getSequenceTextbox(self):
        return self.widgets_dict[c.TARGET_SEQUENCE]

    def setSequence(self, value):
        self.getSequenceTextbox().setValue(value)

    def calculateSequence(self, freq_on, freq_off):
        return ("1"*freq_on)+("0"*freq_off)

    def getSequence(self):
        return self.getSequenceTextbox().getValue()

    def getStateChangeCount(self, sequence):
        state_change_count = 0
        prev = sequence[-1]
        for c in sequence:
            if c != prev:
                state_change_count += 1.0
                prev = c
        return state_change_count

    def freqFromSequence(self, sequence):
        return self.getStateChangeCount(sequence)/(2*len(sequence)/self.getMonitorFreq())

    def sequenceChanged(self, sequence):
        if sequence.count("0") == len(sequence) or sequence.count("1") == len(sequence):
            self.setTargetFreq(self.getMonitorFreq())
            return True
        elif sequence.count("0")+sequence.count("1") != len(sequence):
            return False
        else:
            self.setTargetFreq(self.freqFromSequence(sequence))
            return True

    def calculateOnOffFreq(self, increase=False, decrease=False):
        target_freq = self.getTargetFreq()
        monitor_freq = self.getMonitorFreq()
        freq_on = math.floor(monitor_freq/target_freq/2.0)
        freq_off = math.ceil(monitor_freq/target_freq/2.0)
        if freq_on < freq_off:
            freq_on += decrease
            freq_off -= increase
        else:
            freq_off += decrease
            freq_on -= increase
        return int(freq_on), int(freq_off)

    def calculateNewFreq(self, freq_on, freq_off):
        return self.getMonitorFreq()/(freq_off+freq_on)

    def monitorFrequencyChangedEvent(self):
        self.changeFreq()

    def changeFreq(self, increase=False, decrease=False):
        freq_on, freq_off = self.calculateOnOffFreq(increase, decrease)
        if freq_off+freq_on != 0:
            new_freq = self.calculateNewFreq(freq_on, freq_off)
            new_sequence = self.calculateSequence(freq_on, freq_off)
            sequence = self.getSequence()
            current_freq = self.freqFromSequence(sequence) if sequence != "" else None
            if increase or decrease or current_freq != self.getTargetFreq():
                self.setTargetFreq(new_freq)
                self.setSequence(new_sequence)
            return True
        else:
            return False
