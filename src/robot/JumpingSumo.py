import stream
import constants as c
import AbstractRobot


class JumpingSumo(AbstractRobot.AbstractRobot):
    def __init__(self, connection):
        self.controller = None
        AbstractRobot.AbstractRobot.__init__(self, connection)

    def getVideoStreamBytes(self):
        if self.controller is not None:
            return self.controller.get_pic()
        else:
            return None

    def handleMessage(self, command):
        if self.controller is not None:
            if command == c.MOVE_FORWARD:
                self.controller.move(10, block=False)
            elif command == c.MOVE_BACKWARD:
                self.controller.move(-10, block=False)
            elif command == c.MOVE_STOP:
                self.controller.move(0, block=False)
            elif command == c.MOVE_LEFT:
                self.controller.move(10, -10, block=False)
            elif command == c.MOVE_RIGHT:
                self.controller.move(10, 10, block=False)

    def setupVideoStream(self):
        try:
            self.controller = stream.SumoController()
            return c.SUCCESS_MESSAGE
        except stream.InitTimeoutException, e:
            print("Could not connect to Jumping Sumo. Is it switched on and computer connected to it?: " + str(e))
            return c.FAIL_MESSAGE
