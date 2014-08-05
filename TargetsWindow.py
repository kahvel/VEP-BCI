__author__ = 'Anti'
from psychopy import visual, core, logging, event


class Target:
    def __init__(self, target, window, monitor_frequency):
        self.color = target["Color1"]
        self.rect = visual.Rect(window, width=int(target["Width"]), height=int(target["Height"]),
                                pos=(int(target["x"]), int(target["y"])), autoLog=False, fillColor=self.color)
        # self.fixation = visual.GratingStim(window, size=1, pos=[int(target["x"]), int(target["y"])], sf=0, rgb=1)
        # self.fixation.setAutoDraw(True)
        self.detection_color = "#00ff00"
        self.freq = float(target["Freq"])
        self.sequence = "01"
        monitor_frequency = int(monitor_frequency)
        self.freq_on = int(monitor_frequency/self.freq//2)
        self.freq_off = int(monitor_frequency/self.freq/2.0+0.5)
        print "Frequency: " + str(float(monitor_frequency)/(self.freq_off+self.freq_on)), self.freq_on, self.freq_off

    def generator(self):
        detected = False
        while True:
            for c in self.sequence:
                if c == "1":
                    for _ in range(self.freq_on):
                        freq = yield
                        if freq == self.freq:
                            detected = True
                        if detected:
                            self.rect.fillColor = self.detection_color
                        self.rect.draw()
                        # self.fixation.draw()
                detected = False
                self.rect.fillColor = self.color
                if c == "0":
                    for _ in range(self.freq_off):
                        freq = yield
                        if freq == self.freq:
                            detected = True


class TargetsWindow:
    def __init__(self, connection, background_data):
        logging.console.setLevel(logging.WARNING)
        self.connection = connection
        self.generators = []
        self.window = None
        self.monitor_frequency = None
        self.setWindow(background_data)
        self.MyMainloop()
        # clock = core.Clock()
        #self.window._refreshThreshold = 1/60
        #self.window.setRecordFrameIntervals(True)
        #self.run()

    def recvPacket(self):
        while True:
            self.window.flip()
            if self.connection.poll():
                message = self.connection.recv()
                return message
            if len(event.getKeys()) > 0:
                return "Exit"

    def MyMainloop(self):
        while True:
            message = self.recvPacket()
            if message == "Start":
                print "Starting targets"
                self.setTargets(self.connection.recv())
                message = self.run()
            if message == "Stop":
                print "Targets stopped"
            if message == "Exit":
                print "Exiting targets"
                break
        self.connection.send("Close")
        self.connection.close()
        self.window.close()

    def setWindow(self, background_data):
        self.window = visual.Window([int(background_data["Width"]),
                                     int(background_data["Height"])],
                                    units="pix", color=background_data["Color"])
        self.monitor_frequency = background_data["Freq"]

    def setTargets(self, targets):
        self.generators = []
        for target in targets:
            rect = Target(target, self.window, self.monitor_frequency)
            self.generators.append(rect.generator())
            self.generators[-1].send(None)

    def run(self):
        # while not self.connection.poll(0.1):  # Start emotiv and psychopy together
        #     self.window.flip()
        while True:
            freq = None
            if self.connection.poll():
                freq = self.connection.recv()
            if isinstance(freq, basestring):
                return freq
            for generator in self.generators:
                generator.send(freq)
            self.window.flip()
            if len(event.getKeys()) > 0:
                return "Exit"
            event.clearEvents()
