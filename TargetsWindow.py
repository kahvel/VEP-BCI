__author__ = 'Anti'

from psychopy import visual, core, logging, event


class Target(object):
    def __init__(self, target, window, monitor_frequency):
        self.color = target["Color1"]
        self.rect = visual.Rect(window, width=int(target["Width"]), height=int(target["Height"]),
                                pos=(int(target["x"]), int(target["y"])), autoLog=False, fillColor=self.color)
        self.fixation = visual.GratingStim(window, size=1, pos=[int(target["x"]), int(target["y"])], sf=0, rgb=1)
        self.fixation.setAutoDraw(True)
        self.detected_rect = visual.Rect(window, width=10, height=10, fillColor="#00ff00",
                                         pos=(int(target["x"]), int(target["y"])+int(target["Width"])+20))
        self.current_rect = visual.Rect(window, width=10, height=10, fillColor="#00ff00",
                                        pos=(int(target["x"]), int(target["y"])-int(target["Height"])+20))
        # self.detection_color = "#00ff00"
        self.freq = float(target["Freq"])
        self.sequence = "01"
        monitor_frequency = int(monitor_frequency)
        self.freq_on = int(monitor_frequency/self.freq//2)
        self.freq_off = int(monitor_frequency/self.freq/2.0+0.5)
        print "Frequency: " + str(float(monitor_frequency)/(self.freq_off+self.freq_on)), self.freq_on, self.freq_off

    def generator(self):
        while True:
            for c in self.sequence:
                if c == "1":
                    for _ in range(self.freq_on):
                        yield
                        self.rect.draw()
                        # self.fixation.draw()
                self.rect.fillColor = self.color
                if c == "0":
                    for _ in range(self.freq_off):
                        yield


class TargetsWindow(object):
    def __init__(self, connection, args):
        logging.console.setLevel(logging.WARNING)
        self.connection = connection
        self.targets = None
        self.generators = None
        background_data = args[0]
        self.lock = args[1]
        self.window = visual.Window([int(background_data["Width"]),
                                     int(background_data["Height"])],
                                    units="pix", color=background_data["Color"])
        self.monitor_frequency = background_data["Freq"]
        self.MyMainloop()
        # clock = core.Clock()
        #self.window._refreshThreshold = 1/60
        #self.window.setRecordFrameIntervals(True)

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
                self.setFreq(self.connection.recv())
                self.setTargets(self.connection.recv())
                self.lock.acquire()
                message = self.run()
                self.lock.release()
            if message == "Stop":
                print "Targets stopped"
            if message == "Exit":
                print "Exiting targets"
                break
        self.connection.send("Close")
        self.connection.close()
        self.window.close()

    def setFreq(self, background_data):
        # self.window.size = (int(background_data["Width"]), int(background_data["Height"]))
        # self.window.color = background_data["Color"]
        self.monitor_frequency = background_data["Freq"]

    def setTargets(self, targets):
        self.targets = []
        self.generators = []
        for target in targets:
            self.targets.append(Target(target, self.window, self.monitor_frequency))
            self.generators.append(self.targets[-1].generator())
            self.generators[-1].send(None)

    def run(self):
        prev_rect = self.targets[0].current_rect
        while True:
            freq = None
            if self.connection.poll():
                freq = self.connection.recv()
            if isinstance(freq, basestring):
                prev_rect.setAutoDraw(False)
                return freq
            for i in range(len(self.targets)):
                if freq == self.targets[i].freq and isinstance(freq, float):
                    self.targets[i].detected_rect.draw()
                elif freq == i and isinstance(i, int):
                    prev_rect.setAutoDraw(False)
                    self.targets[i].current_rect.setAutoDraw(True)
                    prev_rect = self.targets[i].current_rect
                self.generators[i].send(None)
            self.window.flip()
            if len(event.getKeys()) > 0:
                return "Exit"
            event.clearEvents()
