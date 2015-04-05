__author__ = 'Anti'

from psychopy import visual, core, logging, event
import constants as c

# To get rid of psychopy avbin.dll error, copy avbin.dll to C:\Windows\SysWOW64


class Target(object):
    def __init__(self, target, window, monitor_frequency):
        self.standby_target = False
        self.color = target["Color1"]
        self.rect = visual.Rect(window, width=int(target["Width"]), height=int(target["Height"]),
                                pos=(int(target["x"]), int(target["y"])), autoLog=False, fillColor=self.color)
        # self.fixation = visual.GratingStim(window, size=1, pos=[int(target["x"]), int(target["y"])], sf=0, rgb=1)
        # self.fixation.setAutoDraw(True)
        self.detected_rect = visual.Rect(window, width=10, height=10, fillColor="#00ff00",
                                         pos=(int(target["x"]), int(target["y"])+int(target["Width"])+20))
        self.current_rect = visual.Rect(window, width=10, height=10, fillColor="#00ff00",
                                        pos=(int(target["x"]), int(target["y"])-int(target["Height"])+20))
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
                        standby = yield
                        if not standby or self.standby_target:
                            self.rect.draw()
                        # self.fixation.draw()
                if c == "0":
                    for _ in range(self.freq_off):
                        yield


class TargetsWindow(object):
    def __init__(self, connection):
        logging.console.setLevel(logging.WARNING)
        self.connection = connection
        """ @type : Connection """
        self.targets = None
        self.generators = None
        # background_data = args[0]
        # self.lock = args[1]
        self.window = None
        self.monitor_frequency = None
        self.MyMainloop()
        # clock = core.Clock()
        #self.window._refreshThreshold = 1/60
        #self.window.setRecordFrameIntervals(True)

    def recvPacket(self):
        while True:
            self.updateWindow()
            if self.connection.poll():
                message = self.connection.recv()
                return message
            if len(event.getKeys()) > 0:
                return "Exit"

    def MyMainloop(self):
        while True:
            message = self.recvPacket()
            if message == c.START_MESSAGE:
                print("Starting targets")
                self.setBackground(self.connection.recv())
                self.setTargets(self.connection.recv())
                standby = self.connection.recv()
                # self.lock.acquire()
                message = self.run(standby)
                # self.lock.release()
            if message == c.STOP_MESSAGE:
                print("Targets stopped")
            if message == c.EXIT_MESSAGE:
                print("Exiting targets")
                break
        self.connection.send(c.CLOSE_MESSAGE)
        self.connection.close()
        self.window.close()

    def updateWindow(self):
        if self.window is not None:
            self.window.flip()

    def setBackground(self, background_data):
        self.window = visual.Window(
            [
                background_data[c.WINDOW_WIDTH],
                background_data[c.WINDOW_HEIGHT]
            ],
            units="pix",
            color=background_data[c.WINDOW_COLOR]
        )
        self.monitor_frequency = background_data[c.WINDOW_FREQ]

    def setFreq(self, background_data):  # NOT USING THIS
        # self.window.size = (int(background_data["Width"]), int(background_data["Height"]))
        # self.window.color = background_data["Color"]
        self.monitor_frequency = background_data[c.WINDOW_FREQ]

    def setTargets(self, targets):
        self.targets = []
        self.generators = []
        for target in targets:
            self.targets.append(Target(target, self.window, self.monitor_frequency))
            self.generators.append(self.targets[-1].generator())
            self.generators[-1].send(None)
        self.targets[-1].standby_target = True

    def run(self, standby):
        prev_rect = self.targets[0].current_rect
        while True:
            if self.connection.poll():
                message = self.connection.recv()
                if isinstance(message, bool):
                    standby = message
                    continue
                elif isinstance(message, basestring):
                    prev_rect.setAutoDraw(False)
                    return message
                for i in range(len(self.targets)):
                    if message == self.targets[i].freq and isinstance(message, float):
                        self.targets[i].detected_rect.draw()
                        break
                    elif message == i and isinstance(message, int):
                        prev_rect.setAutoDraw(False)
                        self.targets[i].current_rect.setAutoDraw(True)
                        prev_rect = self.targets[i].current_rect
                        break
            for i in range(len(self.targets)):
                self.generators[i].send(standby)
            self.window.flip()
            if len(event.getKeys()) > 0:
                return "Exit"
            event.clearEvents()
