__author__ = 'Anti'

from psychopy import visual, core, logging, event
import constants as c

# To get rid of psychopy avbin.dll error, copy avbin.dll to C:\Windows\SysWOW64


class Target(object):
    def __init__(self, target, test_color, window):
        self.standby_target = False
        self.color1 = target[c.TARGET_COLOR1]
        self.color0 = target[c.TARGET_COLOR0]
        self.test_color = test_color
        self.current_target = False
        self.rect = visual.Rect(
            window,
            width=target[c.TARGET_WIDTH],
            height=target[c.TARGET_HEIGHT],
            pos=(target[c.TARGET_X], target[c.TARGET_Y]),
            autoLog=False,
            fillColor=self.color1
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
        self.sequence = str(target[c.TARGET_SEQUENCE])

    def setCurrent(self, value):
        self.current_target = value

    def drawRect(self, color, standby):
        self.rect.setFillColor(color, colorSpace="rgb")
        self.rect.setLineColor(color, colorSpace="rgb")
        if not standby or self.standby_target:
            self.rect.draw()

    def generator(self):
        while True:
            for state in self.sequence:
                standby = yield
                if state == "1":
                    self.drawRect(self.test_color if self.current_target else self.color1, standby)
                    # self.fixation.draw()
                if state == "0":
                    self.drawRect(self.color0, standby)


class TargetsWindow(object):
    def __init__(self, connection):
        logging.console.setLevel(logging.ERROR )
        self.connection = connection
        """ @type : ConnectionProcessEnd.PsychopyConnection """
        self.targets = None
        self.generators = None
        self.window = None
        self.monitor_frequency = None
        self.prev_current = None
        # clock = core.Clock()
        #self.window._refreshThreshold = 1/60
        #self.window.setRecordFrameIntervals(True)
        self.connection.waitMessages(self.start, self.exit, self.updateWindow, self.setup)

    def setup(self):
        options = self.connection.receiveOptions()
        self.setBackground(options[c.DATA_BACKGROUND])
        self.setTargets(options[c.DATA_TARGETS], options[c.DATA_TEST][c.TEST_COLOR])
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

    def setTargets(self, targets, test_color):
        self.targets = []
        self.generators = []
        for target in targets:
            self.targets.append(Target(target, test_color, self.window))
            self.generators.append(self.targets[-1].generator())
            self.generators[-1].send(None)
        self.targets[-1].standby_target = True

    def setCurrentTarget(self, target):
        if self.prev_current is not None:
            self.prev_current.setCurrent(False)
        target.setCurrent(True)
        self.prev_current = target

    def start(self, standby=False):
        while True:
            self.updateWindow()
            message = self.connection.receiveMessageInstant()
            if message is not None:
                if isinstance(message, bool):
                    standby = message
                    continue
                elif isinstance(message, basestring):
                    # prev_rect.setAutoDraw(False)
                    return message
                for i in range(len(self.targets)):
                    if message == self.targets[i].freq and isinstance(message, float):
                        self.targets[i].detected_rect.draw()
                        break
                    elif message == i+1 and isinstance(message, int):
                        self.setCurrentTarget(self.targets[i])
                        break
            for i in range(len(self.targets)):
                self.generators[i].send(standby)
