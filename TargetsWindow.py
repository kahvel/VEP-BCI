__author__ = 'Anti'

from psychopy import visual, core, logging, event
import constants as c

# To get rid of psychopy avbin.dll error, copy avbin.dll to C:\Windows\SysWOW64


class Target(object):
    def __init__(self, options, test_color, window):
        self.standby_target = False
        self.color1 = options[c.TARGET_COLOR1]
        self.color0 = options[c.TARGET_COLOR0]
        self.test_color = test_color
        self.current_target = False
        self.detected_target = False
        self.detected_counter = 0
        self.detected_length = 3
        self.rect = self.getRect(window, options, self.color1)
        # self.fixation = visual.GratingStim(window, size=1, pos=[int(options["x"]), int(options["y"])], sf=0, rgb=1)
        # self.fixation.setAutoDraw(True)
        self.current_target_signs = self.getSigns(window, options, self.test_color)
        self.detected_target_signs = self.getSigns(window, options, "#00ff00")
        self.freq = float(options[c.DATA_FREQ])
        self.sequence = str(options[c.TARGET_SEQUENCE])

    def getRect(self, window, options, color):
        return visual.Rect(
            window,
            width=options[c.TARGET_WIDTH],
            height=options[c.TARGET_HEIGHT],
            pos=(options[c.TARGET_X], options[c.TARGET_Y]),
            autoLog=False,
            fillColor=color
        )

    def getTriangle(self, window, options, color, x, y, ori=0):
        return visual.Polygon(
            window,
            edges=3,
            radius=10,
            fillColor=color,
            ori=ori,
            pos=(
                options[c.TARGET_X]+(options[c.TARGET_WIDTH]/2 + 20)*x,
                options[c.TARGET_Y]+(options[c.TARGET_HEIGHT]/2 + 20)*y
            )
        )

    def getSigns(self, window, options, color):
        return (
            self.getTriangle(window, options, color, 0, 1, 60),
            self.getTriangle(window, options, color, 1, 0, 30),
            self.getTriangle(window, options, color, 0, -1),
            self.getTriangle(window, options, color, -1, 0, -30)
        )

    def setCurrent(self, value):
        self.current_target = value

    def detected(self):
        self.detected_target = True

    def setStandbyTarget(self, value):
        self.standby_target = value

    def drawRect(self, color, standby):
        self.rect.setFillColor(color, colorSpace="rgb")
        self.rect.setLineColor(color, colorSpace="rgb")
        if not standby or self.standby_target:
            self.rect.draw()

    def drawTriangles(self, standby, triangles):
        if not standby:
            for triangle in triangles:
                triangle.draw()

    def drawDetectedSigns(self, standby):
        self.drawTriangles(standby, self.detected_target_signs)
        if self.detected_counter < self.detected_length:
            self.detected_counter = 0
            self.detected_target = False
        else:
            self.detected_counter += 1

    def generator(self):
        while True:
            for state in self.sequence:
                standby = yield
                if self.detected_target:
                    self.drawDetectedSigns(standby)
                elif self.current_target:
                    self.drawTriangles(standby, self.current_target_signs)
                if state == "1":
                    self.drawRect(self.color1, standby)
                    # self.fixation.draw()
                elif state == "0":
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
        self.window = self.getWindow(options[c.DATA_BACKGROUND])
        self.monitor_frequency = self.getMonitorFreq(options[c.DATA_BACKGROUND])
        self.targets = self.getTargets(options[c.DATA_TARGETS], options[c.DATA_TEST][c.TEST_COLOR], self.window)
        self.generators = self.getGenerators(self.targets)
        self.setStandbyTarget(options[c.DATA_TEST][c.TEST_STANDBY])
        return c.SUCCESS_MESSAGE

    def exit(self):
        self.connection.close()
        self.closeWindow()
        core.quit()

    def closeWindow(self):
        if self.window is not None:
            self.window.close()

    def updateWindow(self):
        if self.window is not None:
            self.window.flip()

    def getMonitorFreq(self, background_data):
        return background_data[c.WINDOW_FREQ]

    def getWindow(self, background_data):
        self.closeWindow()
        return visual.Window(
            [background_data[c.WINDOW_WIDTH], background_data[c.WINDOW_HEIGHT]],
            units="pix",
            color=background_data[c.WINDOW_COLOR]
        )

    def getTargets(self, targets_data, test_color, window):
        return [Target(data, test_color, window) for data in targets_data]

    def setupGenerator(self, generator):
        generator.send(None)
        return generator

    def getGenerators(self, targets):
        return [self.setupGenerator(target.generator()) for target in targets]

    def setStandbyTarget(self, standby):
        if standby != c.TEST_NONE:
            self.targets[standby-1].setStandbyTarget(True)

    def setCurrentTarget(self, target):
        if self.prev_current is not None:
            self.prev_current.setCurrent(False)
        target.setCurrent(True)
        self.prev_current = target

    def setTargetDetected(self, target):
        target.detected()

    def start(self, standby=False):
        while True:
            self.updateWindow()
            message = self.connection.receiveMessageInstant()
            if message is not None:
                if isinstance(message, bool):
                    standby = message
                    continue
                elif isinstance(message, basestring):
                    return message
                for i in range(len(self.targets)):
                    if message == self.targets[i].freq and isinstance(message, float):
                        self.setTargetDetected(self.targets[i])
                        break
                    elif message == i+1 and isinstance(message, int):
                        self.setCurrentTarget(self.targets[i])
                        break
            for i in range(len(self.targets)):
                self.generators[i].send(standby)
