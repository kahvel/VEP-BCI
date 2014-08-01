__author__ = 'Anti'
import Tkinter
import SNRExtraction
import ControlWindow


class Window(ControlWindow.ControlWindow):
    def __init__(self, to_main, to_emotiv, sensor_names, to_targets):
        self.window_group_names = ["SNR"]
        self.window_names = ["SNR", "SumSNR"]
        self.button_names = ["", "Sum"]
        self.files = [SNRExtraction]
        ControlWindow.ControlWindow.__init__(self, "Plot control", 320, 370, sensor_names)
        self.to_emotiv = to_emotiv
        self.to_main = to_main
        self.to_targets = to_targets
        self.myMainloop()

    def myMainloop(self):
        while True:
            message = self.recvPacket(self.to_main)
            if message == "Start":
                print "Starting extraction"
                self.freq_points = self.to_main.recv()
                while self.to_emotiv.poll():
                    print self.to_emotiv.recv()
                message = self.start()
            if message == "Stop":
                print "Extraction stopped"
            if message == "Exit":
                print "Exiting extraction"
                break

    def reset(self, windows, key, sensor_names):
        window = windows[key]
        if window is not None:
            window.canvas.insert(Tkinter.END, "Starting\n")
            self.closeGenerators(window.generators)
            window.continue_generating = True
            window.setup(self.options_textboxes, self.variables, sensor_names, self.freq_points)

    def startPacketSending(self):
        while True:
            packet = self.recvPacket(self.to_emotiv)
            if isinstance(packet, basestring):
                return packet
            for group_name in self.window_group_names:
                for name in self.window_names:
                    if self.window_groups[group_name][name] is not None:
                        if self.window_groups[group_name][name].continue_generating:
                            extracted_freq = self.window_groups[group_name][name].sendPacket(packet)
                            if extracted_freq is not None:
                                self.to_targets.send(extracted_freq)


