__author__ = 'Anti'

from widgets import Textboxes
from frames import Frame, DisableDeleteNotebookTab
import constants as c
import math


class TargetsTab(DisableDeleteNotebookTab.DisableDeleteNotebookTab):
    def __init__(self, parent, getMonitorFreq, **kwargs):
        DisableDeleteNotebookTab.DisableDeleteNotebookTab.__init__(self, parent, c.TARGETS_TAB_TAB, **kwargs)
        self.addChildWidgets((
            TargetFrame(self.widget, 0, 0, getMonitorFreq, **kwargs),
            self.getDisableDeleteFrame(1, 0, delete_tab=kwargs["delete_tab"])
        ))

    def changeFreq(self):
        self.widgets_dict[c.TARGET_FRAME].changeFreq()


class TargetFrame(Frame.Frame):
    def __init__(self, parent, row, column, getMonitorFreq, **kwargs):
        Frame.Frame.__init__(self, parent, c.TARGET_FRAME, row, column, **kwargs)
        self.getMonitorFreq = getMonitorFreq
        self.loading_default_value = True
        validate = lambda: self.changeFreq()
        increase = lambda: self.changeFreq(increase=True)
        decrease = lambda: self.changeFreq(decrease=True)
        self.addChildWidgets((
            Textboxes.PlusMinusTextboxFrame(self.widget, c.TARGET_FREQ,   0, 0, increase, decrease, command=validate),
            Textboxes.SequenceTextbox      (self.widget, c.TARGET_SEQUENCE, 1, 0, allow_zero=True, command=self.sequenceChanged, width=35, columnspan=4),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_WIDTH,  2, 0, command=int, default_value=150),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_HEIGHT, 2, 2, command=int, default_value=150),
            Textboxes.ColorTextboxFrame    (self.widget, c.TARGET_COLOR1, c.TARGET_COLOR1_FRAME, 2, 4, default_value="#ffffff"),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_X,      3, 0, command=int, allow_negative=True, allow_zero=True),
            Textboxes.LabelTextbox         (self.widget, c.TARGET_Y,      3, 2, command=int, allow_negative=True, allow_zero=True),
            Textboxes.ColorTextboxFrame    (self.widget, c.TARGET_COLOR0, c.TARGET_COLOR2_FRAME, 3, 4, default_value="#000000")
        ))

    def getTargetFreq(self):
        return float(self.getFrequencyTextbox().getValue())

    def setTargetFreq(self, value):
        self.getFrequencyTextbox().setValue(value)

    def getFrequencyTextbox(self):
        return self.widgets_dict[c.PLUS_MINUS_TEXTOX_FRAME].widgets_dict[c.TARGET_FREQ]

    def getSequenceTextbox(self):
        return self.widgets_dict[c.TARGET_SEQUENCE]

    def setSequence(self, freq_on, freq_off):
        self.getSequenceTextbox().setValue(self.calculateSequence(freq_on, freq_off))

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

    def sequenceChanged(self, sequence):
        if sequence.count("0") == len(sequence) or sequence.count("1") == len(sequence):
            self.setTargetFreq(self.getMonitorFreq())
            return True
        elif sequence.count("0")+sequence.count("1") != len(sequence):
            return False
        else:
            self.setTargetFreq(self.getStateChangeCount(sequence)/(2*len(sequence)/self.getMonitorFreq()))
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

    def changeFreq(self, increase=False, decrease=False):
        freq_on, freq_off = self.calculateOnOffFreq(increase, decrease)
        if freq_off+freq_on != 0:
            self.setTargetFreq(self.calculateNewFreq(freq_on, freq_off))
            self.setSequence(freq_on, freq_off)
            self.loading_default_value = False
            return True
        else:
            return False
