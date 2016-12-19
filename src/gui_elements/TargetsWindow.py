from psychopy import visual, core, logging

from PIL import Image
import io
import time

import constants as c

# To get rid of psychopy avbin.dll error, copy avbin.dll to C:\Windows\SysWOW64


class TargetHandler(object):
    def __init__(self, id, options, test_color, window):
        self.standby_target = False
        self.current_target = False
        self.detected_target = False
        self.detected_counter = 0
        self.detected_length = 3
        self.target = self.getTargetWrapper(window, options)
        self.fixation = visual.GratingStim(window, size=1, pos=[options[c.TARGET_X], options[c.TARGET_Y]], sf=0, rgb=1)
        self.fixation.setAutoDraw(True)
        self.current_target_signs = self.getSigns(window, options, test_color)
        self.detected_target_signs = self.getSigns(window, options, "#00ff00", 40)
        self.freq = options[c.DATA_FREQ]
        self.sequence = options[c.TARGET_SEQUENCE]
        self.id = id

    def getTargetWrapper(self, window, options):
        size = (options[c.TARGET_WIDTH], options[c.TARGET_HEIGHT])
        position = (options[c.TARGET_X], options[c.TARGET_Y])
        colors = (options[c.TARGET_COLOR0], options[c.TARGET_COLOR1])
        return self.getTarget(window, size, position, colors)

    def getTarget(self, window, size, position, colors):
        raise NotImplementedError("getTarget not implemented!")

    def getTriangle(self, window, options, color, x, y, ori=0, offset=20):
        return visual.Polygon(
            window,
            edges=3,
            radius=10,
            fillColor=color,
            ori=ori,
            pos=(
                options[c.TARGET_X]+(options[c.TARGET_WIDTH]/2 + offset)*x,
                options[c.TARGET_Y]+(options[c.TARGET_HEIGHT]/2 + offset)*y
            )
        )

    def getSigns(self, window, options, color, offset=20):
        return (
            self.getTriangle(window, options, color, 0, 1, 60, offset),
            self.getTriangle(window, options, color, 1, 0, 30, offset),
            self.getTriangle(window, options, color, 0, -1, 0, offset),
            self.getTriangle(window, options, color, -1, 0, -30, offset)
        )

    def setCurrent(self, value):
        self.current_target = value

    def setDetected(self, value):
        self.detected_target = value

    def setStandbyTarget(self, value):
        self.standby_target = value

    def drawTarget(self, color_index, standby):
        self.target.setFillColor(color_index)
        self.target.setLineColor(color_index)
        if not standby or self.standby_target:
            self.target.draw()

    def drawTriangles(self, standby, triangles):
        if not standby:
            for triangle in triangles:
                triangle.draw()
                # triangle.autoDraw = self.detected_target

    def drawDetectedSigns(self, standby):
        self.drawTriangles(standby, self.detected_target_signs)

    def generator(self):
        while True:
            for state in self.sequence:
                standby = yield
                if self.detected_target:
                    self.drawTriangles(standby, self.detected_target_signs)
                if self.current_target:
                    self.drawTriangles(standby, self.current_target_signs)
                self.drawTarget(int(state), standby)


# class ColorHandler(object):
#     def __init__(self, colors, current_color_index):
#         self.colors = colors
#         self.current_color_index = current_color_index
#         self.color_count = len(colors)
#
#     def nextColorIndex(self):
#         if self.current_color_index == self.color_count - 1:
#             return 0
#         else:
#             return self.current_color_index + 1
#
#     def nextColor(self):
#         self.current_color_index = self.nextColorIndex()
#         return self.colors[self.current_color_index]


class Rectangle(object):
    def __init__(self, window, size, position, colors, current_color_index):
        self.color_space = "rgb"
        self.colors = colors
        self.rectangle = visual.Rect(
            window,
            width=size[0],
            height=size[1],
            pos=position,
            autoLog=False,
            fillColor=colors[current_color_index]
        )

    def setFillColor(self, color_index):
        self.rectangle.setFillColor(self.colors[color_index], colorSpace=self.color_space)

    def setLineColor(self, color_index):
        self.rectangle.setLineColor(self.colors[color_index], colorSpace=self.color_space)

    def draw(self):
        self.rectangle.draw()


class Target(object):
    def __init__(self):
        self.objects = []

    def setFillColor(self, color_index):
        for object in self.objects:
            object.setFillColor(color_index)

    def setLineColor(self, color_index):
        for object in self.objects:
            object.setLineColor(color_index)

    def draw(self):
        for object in self.objects:
            object.draw()


class RectangleTarget(Target):
    def __init__(self, window, size, position, colors):
        Target.__init__(self)
        self.objects = [Rectangle(window, size, position, colors, 1)]


class CheckerboardTarget(Target):
    def __init__(self, window, size, position, colors, rectangles_in_row):
        Target.__init__(self)
        self.objects = self.getRectangles(window, size, position, colors, rectangles_in_row)

    def getRectangles(self, window, size, position, colors, rectangles_in_row):
        rectangle_size = self.getRectangleSize(size, rectangles_in_row)
        up_left_rectangle_position = self.getUpLeftRectanglePosition(rectangle_size, position, rectangles_in_row)
        return self.makeRectangles(window, colors, rectangle_size, rectangles_in_row, up_left_rectangle_position)

    def makeRectangles(self, window, colors, rectangle_size, rectangles_in_row, up_left_rectangle_position):
        return [self.makeRectangle(row, column, window, colors, rectangle_size, up_left_rectangle_position)
                for row in range(rectangles_in_row) for column in range(rectangles_in_row)]

    def makeRectangle(self, row, column, window, colors, rectangle_size, up_left_rectangle_position):
        current_rectangle_position = self.getCurrentRectanglePosition(up_left_rectangle_position, row, column, rectangle_size)
        return Rectangle(
            window, rectangle_size, current_rectangle_position,
            self.shiftColors(colors, row, column), 0
        )

    def shiftColors(self, colors, row, column):
        return colors if row % 2 == column % 2 else (colors[1:] + (colors[0],))

    def getUpLeftRectanglePosition(self, rectangle_size, position, rectangles_in_row):
        rectangles_to_up_left = (rectangles_in_row - 1) / 2.0
        up_left_rectangle_x = position[0] - rectangles_to_up_left * rectangle_size[0]
        up_left_rectangle_y = position[1] - rectangles_to_up_left * rectangle_size[1]
        return up_left_rectangle_x, up_left_rectangle_y

    def getRectangleSize(self, size, rectangles_in_row):
        rectangle_width = float(size[0])/rectangles_in_row
        rectangle_height = float(size[1])/rectangles_in_row
        return rectangle_width, rectangle_height

    def getCurrentRectanglePosition(self, up_left_rectangle_position, row, column, rectangle_size):
        current_rectangle_x = up_left_rectangle_position[0] + row * rectangle_size[0]
        current_rectangle_y = up_left_rectangle_position[1] + column * rectangle_size[1]
        return current_rectangle_x, current_rectangle_y


class RectangleTargetHandler(TargetHandler):
    def getTarget(self, window, size, position, colors):
        return RectangleTarget(window, size, position, colors)


class CheckerboardTargetHandler(TargetHandler):
    def getTarget(self, window, size, position, colors):
        return CheckerboardTarget(window, size, position, colors, 3)


class TargetsWindow(object):
    def __init__(self, connection):
        logging.console.setLevel(logging.ERROR )
        self.connection = connection
        """ @type : connections.ConnectionProcessEnd.PsychopyConnection """
        self.targets = None
        self.generators = None
        self.window = None
        self.monitor_frequency = None
        self.prev_current = None
        self.prev_detected = None
        self.video_stream = None
        self.flip_time = None
        # clock = core.Clock()
        #self.window._refreshThreshold = 1/60
        #self.window.setRecordFrameIntervals(True)
        self.connection.waitMessages(self.start, self.exit, self.updateWindow, self.setup)

    def setup(self):
        options = self.connection.receiveMessageBlock()
        self.window = self.getWindow(options[c.DATA_BACKGROUND])
        self.monitor_frequency = self.getMonitorFreq(options[c.DATA_BACKGROUND])
        self.targets = self.getTargets(options[c.DATA_TARGETS], options[c.DATA_TEST][c.TEST_TAB_COLOR], self.window)
        self.generators = self.getGenerators(self.targets)
        self.setStandbyTarget(options[c.DATA_TEST][c.TEST_TAB_STANDBY])
        self.video_stream = self.getVideoStreamImage(self.window, options[c.DATA_ROBOT])
        return c.SETUP_SUCCEEDED_MESSAGE

    def getVideoStreamImage(self, window, options):
        if options[c.ROBOT_STREAM] and not options[c.DISABLE]:
            image = visual.ImageStim(window, pos=(options[c.STREAM_X], options[c.STREAM_Y]), size=(options[c.STREAM_WIDTH], options[c.STREAM_HEIGHT]))
            image.autoDraw = True
            return image

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

    def getTargets(self, targets_options, test_color, window):
        return [self.chooseTarget(key, options, test_color, window) for key, options in targets_options.items()]

    def chooseTarget(self, key, options, test_color, window):
        if options[c.TARGET_TYPE] == c.CHECKERBOARD_TARGET:
            return CheckerboardTargetHandler(key, options, test_color, window)
        elif options[c.TARGET_TYPE] == c.RECTANGLE_TARGET:
            return RectangleTargetHandler(key, options, test_color, window)
        else:
            raise ValueError("Invalid target type value!")

    def setupGenerator(self, generator):
        generator.send(None)
        return generator

    def getGenerators(self, targets):
        return [self.setupGenerator(target.generator()) for target in targets]

    def setStandbyTarget(self, standby):
        if standby != c.TEST_TARGET_NONE:
            self.targets[standby-1].setStandbyTarget(True)

    def setCurrentTarget(self, target):
        if self.prev_current is not None:
            self.prev_current.setCurrent(False)
        target.setCurrent(True)
        self.prev_current = target

    def setTargetDetected(self, target):
        if self.prev_detected is not None:
            self.prev_detected.setDetected(False)
        target.setDetected(True)
        self.prev_detected = target

    def updateStream(self, bytes):
        if self.video_stream is not None:
            image = Image.open(io.BytesIO(bytes))
            self.video_stream.setImage(image)

    def start(self, standby=False):
        while True:
            self.updateWindow()
            message = self.connection.receiveMessageInstant()
            if message is not None:
                if isinstance(message, bool):
                    standby = message
                    continue
                elif isinstance(message, basestring):
                    if len(message) < 10:
                        return message
                    else:
                        self.updateStream(message)
                else:
                    for target in self.targets:
                        if message == target.freq and isinstance(message, float):
                            self.setTargetDetected(target)
                            break
                        elif message == target.id and isinstance(message, int):
                            self.setCurrentTarget(target)
                            break
            for i in range(len(self.targets)):
                self.generators[i].send(standby)
