__author__ = 'Anti'

import Tkinter
import ControlWindow
import SignalPlot
import FFTPlot


class Window(ControlWindow.ControlWindow):
    def __init__(self, connection, sensor_names):
        self.window_group_names = ["Signal", "FFT"]
        self.window_names = ["MultipleAverage", "SingleAverage", "MultipleRegular", "SingleRegular"]
        self.button_names = ["Avg", "Sum Avg", "", "Sum"]
        self.files = [SignalPlot, FFTPlot]
        ControlWindow.ControlWindow.__init__(self, "Plot control", 320, 370, sensor_names)
        self.connection = connection
        self.fft_reset_buttons = {}
        self.signal_reset_buttons = {}
        button_frame = Tkinter.Frame(self)
        self.signal_reset_buttons["MultipleAverage"] = Tkinter.Button(button_frame, text="Reset avg signal", command=lambda: self.reset(self.window_groups["Signal"], "MultipleAverage", self.chosen_sensor_names))
        self.signal_reset_buttons["SingleAverage"] = Tkinter.Button(button_frame, text="Reset sum avg signal", command=lambda: self.reset(self.window_groups["Signal"], "SingleAverage", self.chosen_sensor_names))
        self.fft_reset_buttons["MultipleAverage"] = Tkinter.Button(button_frame, text="Reset avg FFT", command=lambda: self.reset(self.window_groups["FFT"], "MultipleAverage", self.chosen_sensor_names))
        self.fft_reset_buttons["SingleAverage"] = Tkinter.Button(button_frame, text="Reset sum avg FFT", command=lambda: self.reset(self.window_groups["FFT"], "SingleAverage", self.chosen_sensor_names))
        for i in range(2):
            self.signal_reset_buttons[self.window_names[i]].grid(column=i % 2, row=i//2, padx=5, pady=5)
            self.fft_reset_buttons[self.window_names[i]].grid(column=i % 2, row=i//2+1, padx=5, pady=5)
        button_frame.pack()
        self.myMainloop()