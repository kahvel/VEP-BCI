__author__ = 'Anti'

import Tkinter
import ControlWindow
import SignalPlot
import FFTPlot


class Window(ControlWindow.ControlWindow):
    def __init__(self, to_main, to_emotiv, sensor_names):
        self.window_group_names = ["Signal", "FFT"]
        self.window_names = ["MultipleAverage", "SingleAverage", "MultipleRegular", "SingleRegular"]
        self.button_names = ["Avg", "Sum Avg", "", "Sum"]
        self.files = [SignalPlot, FFTPlot]
        ControlWindow.ControlWindow.__init__(self, "Plot control", 320, 370, sensor_names)
        self.to_main = to_main
        self.to_emotiv = to_emotiv
        self.fft_reset_buttons = {}
        self.signal_reset_buttons = {}
        button_frame = Tkinter.Frame(self)
        self.signal_reset_buttons["MultipleAverage"] = Tkinter.Button(button_frame, text="Reset avg signal", command=lambda: self.reset(self.signal_plot_windows, "MultipleAverage", self.chosen_sensor_names))
        self.signal_reset_buttons["SingleAverage"] = Tkinter.Button(button_frame, text="Reset sum avg signal", command=lambda: self.reset(self.signal_plot_windows, "SingleAverage", self.chosen_sensor_names))
        self.fft_reset_buttons["MultipleAverage"] = Tkinter.Button(button_frame, text="Reset avg FFT", command=lambda: self.reset(self.fft_plot_windows, "MultipleAverage", self.chosen_sensor_names))
        self.fft_reset_buttons["SingleAverage"] = Tkinter.Button(button_frame, text="Reset sum avg FFT", command=lambda: self.reset(self.fft_plot_windows, "SingleAverage", self.chosen_sensor_names))
        for i in range(2):
            self.signal_reset_buttons[self.window_names[i]].grid(column=i % 2, row=i//2, padx=5, pady=5)
            self.fft_reset_buttons[self.window_names[i]].grid(column=i % 2, row=i//2+1, padx=5, pady=5)
        button_frame.pack()
        self.myMainloop()

    def myMainloop(self):
        while True:
            message = self.recvPacket(self.to_main)
            if message == "Start":
                print "Starting plot"
                message = self.start()
                while self.to_emotiv.poll():
                    print self.to_emotiv.recv()
            if message == "Stop":
                print "Plot stopped"
            if message == "Exit":
                print "Exiting plot"
                break
        self.to_emotiv.send("Close")
        self.to_emotiv.close()
        self.to_main.send("Close")
        self.to_main.close()
        self.destroy()

    def reset(self, windows, key, sensor_names):
        window = windows[key]
        if window is not None:
            window.canvas.delete("all")
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options_textboxes, self.variables, sensor_names)

    def startPacketSending(self):
        while True:
            packet = self.recvPacket(self.to_emotiv)
            if isinstance(packet, basestring):
                return packet
            for group_name in self.window_group_names:
                for name in self.window_names:
                    if self.window_groups[group_name][name] is not None:
                        if self.window_groups[group_name][name].continue_generating:
                            self.window_groups[group_name][name].sendPacket(packet)