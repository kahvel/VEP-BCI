__author__ = 'Anti'
import numpy as np
from scipy import signal
import MyWindows
import Tkinter
import Identification


class PSIdentification(MyWindows.TkWindow):
    def __init__(self, ps_to_main, ps_to_emo, sensor_names):
        MyWindows.TkWindow.__init__(self, "Power spectrum identification", 320, 320)
        self.ps_to_emo = ps_to_emo
        self.ps_to_main = ps_to_main
        self.packet_count = 128
        self.sensor_names = sensor_names

        self.buttons = {}
        self.windows = {}
        self.checkbox_values = []
        self.garbage = []
        self.button_names = ["PS", "PS2"]
        checkboxframe = Tkinter.Frame(self)
        for i in range(len(self.sensor_names)):
            self.checkbox_values.append(Tkinter.IntVar())
            box = Tkinter.Checkbutton(checkboxframe, text=self.sensor_names[i], variable=self.checkbox_values[i])
            box.grid(column=i % 7, row=i//7)

        buttonframe = Tkinter.Frame(self)
        self.buttons["PS"] = Tkinter.Button(buttonframe, text="PS", command=lambda: self.set("PS"))
        self.buttons["PS2"] = Tkinter.Button(buttonframe, text="PS2", command=lambda: self.set("PS2"))
        for i in range(len(self.button_names)):
            self.buttons[self.button_names[i]].grid(column=i % 4, row=i//4, padx=5, pady=5)

        checkboxframe.grid(column=0, row=0)
        buttonframe.grid(column=0, row=1)
        self.exitFlag = False
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.myMainloop()

    def set(self, key):
        self.windows[key] = getattr(Identification, key)()
        self.windows[key].protocol("WM_DELETE_WINDOW", lambda: self.closeWindow(self.windows, key))

    def closeWindow(self, windows, key):
        windows[key].continue_generating = False
        self.garbage.extend(windows[key].generators)
        windows[key].destroy()
        windows[key] = None

    def exit(self):
        self.exitFlag = True

    def myMainloop(self):
        while True:
            message = self.recvPacket(self.ps_to_main)
            if message == "Start":
                print "Starting PS"
                self.freq_points = self.ps_to_main.recv()
                for generator in self.garbage:
                    generator.close()
                self.garbage = []
                message = self.start()
            if message == "Stop":
                print "PS stopped"
            if message == "Exit":
                print "Exiting PS"
                break

    def recvPacket(self, connection):
        while True:
            self.update()
            if self.ps_to_main.poll():
                message = self.ps_to_main.recv()
                return message
            if self.exitFlag:
                return "Exit"
            if connection.poll(0.1):
                return connection.recv()

    def reset(self, windows, key, checkbox_values):
        window = windows[key]
        if window is not None:
            # window.canvas.delete("all")
            window.canvas.insert(Tkinter.INSERT, "Starting ")
            self.garbage.extend(window.generators)
            window.continue_generating = True
            window.setup(checkbox_values, self.sensor_names, self.freq_points)

    def start(self):
        for key in self.windows:
            if self.windows[key] is not None:
                self.reset(self.windows, key, self.checkbox_values)

        while True:
            packet = self.recvPacket(self.ps_to_emo)
            if isinstance(packet, basestring):
                return packet
            for key in self.windows:
                if self.windows[key] is not None:
                    if self.windows[key].continue_generating:
                        self.windows[key].sendPacket(packet)


