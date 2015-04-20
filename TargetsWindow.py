__author__ = 'Anti'

from psychopy import visual, core, logging, event
import constants as c

# To get rid of psychopy avbin.dll error, copy avbin.dll to C:\Windows\SysWOW64


class Target(object):
    def __init__(self, target, window, monitor_frequency):
        self.standby_target = False
        self.color = target[c.TARGET_COLOR1]
        self.rect = visual.Rect(
            window,
            width=target[c.TARGET_WIDTH],
            height=target[c.TARGET_HEIGHT],
            pos=(target[c.TARGET_X], target[c.TARGET_Y]),
            autoLog=False,
            fillColor=self.color
        )
        # self.fixation = visual.GratingStim(window, size=1, pos=[int(target["x"]), int(target["y"])], sf=0, rgb=1)
        # self.fixation.setAutoDraw(True)
        self.detected_rect = visual.Rect(
            window,
            width=10,
            height=10,
            fillColor="#00ff00",
            pos=(target[c.TARGET_X], target[c.TARGET_Y]+target[c.TARGET_WIDTH]+20)
        )
        self.current_rect = visual.Rect(
            window,
            width=10,
            height=10,
            fillColor="#00ff00",
            pos=(target["x"], target["y"]-target["Height"]+20)
        )
        self.freq = float(target[c.DATA_FREQ])
        self.sequence = "01"
        monitor_frequency = int(monitor_frequency)
        self.freq_on = int(monitor_frequency/self.freq//2)
        self.freq_off = int(monitor_frequency/self.freq/2.0+0.5)
        print("Frequency: " + str(float(monitor_frequency)/(self.freq_off+self.freq_on)), str(self.freq_on), self.freq_off)

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
        logging.console.setLevel(logging.ERROR )
        self.connection = connection
        """ @type : ConnectionProcessEnd.PsychopyConnection """
        self.targets = None
        self.generators = None
        # self.lock = args[1]
        self.window = None
        self.monitor_frequency = None
        # clock = core.Clock()
        #self.window._refreshThreshold = 1/60
        #self.window.setRecordFrameIntervals(True)
        self.connection.waitMessages(self.start, self.exit, self.updateWindow, self.setup)

    def setup(self):
        background_data, targets_data, standby = self.connection.receiveOptions()
        self.setBackground(background_data)
        self.setTargets(targets_data)
        return c.SUCCESS_MESSAGE

    def exit(self):
        self.connection.closeConnection()
        self.closeWindow()
        core.quit()

    def closeWindow(self):
        if self.window is not None:
            self.window.close()

    def updateWindow(self):
        if self.window is not None:
            self.window.flip()

    def setBackground(self, background_data):
        self.closeWindow()
        self.window = visual.Window(
            [
                background_data[c.WINDOW_WIDTH],
                background_data[c.WINDOW_HEIGHT]
            ],
            units="pix",
            color=background_data[c.WINDOW_COLOR]
        )
        self.monitor_frequency = background_data[c.WINDOW_FREQ]

    def setTargets(self, targets):
        self.targets = []
        self.generators = []
        for target in targets:
            self.targets.append(Target(target, self.window, self.monitor_frequency))
            self.generators.append(self.targets[-1].generator())
            self.generators[-1].send(None)
        self.targets[-1].standby_target = True

    def start(self, standby=False):
        prev_rect = self.targets[0].current_rect
        while True:
            self.updateWindow()
            message = self.connection.receiveMessageInstant()
            if message is not None and message != "None":
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
                    elif message == i+1 and isinstance(message, int):
                        prev_rect.setAutoDraw(False)
                        self.targets[i].current_rect.setAutoDraw(True)
                        prev_rect = self.targets[i].current_rect
                        break
            for i in range(len(self.targets)):
                self.generators[i].send(standby)
