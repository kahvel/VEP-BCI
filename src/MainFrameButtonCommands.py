import constants as c


class MainFrameButtonCommands(object):
    def __init__(self, main_window):
        self.commands = {
            c.BOTTOM_FRAME: (
                    main_window.start,
                    main_window.stop,
                    main_window.setup,
                    main_window.askSaveFile,
                    main_window.askLoadFile,
                    main_window.exit,
            ),
            c.TEST_TAB: (
                StoppedButtonCommand(main_window.showResults, main_window.isStopped),
                StoppedButtonCommand(main_window.resetResults, main_window.isStopped),
                StoppedButtonCommand(main_window.saveResults, main_window.isStopped),
            ),
            c.ROBOT_TAB: (
                lambda: main_window.connection.sendMessage(c.MOVE_FORWARD),
                lambda: main_window.connection.sendMessage(c.MOVE_BACKWARD),
                lambda: main_window.connection.sendMessage(c.MOVE_RIGHT),
                lambda: main_window.connection.sendMessage(c.MOVE_LEFT),
                lambda: main_window.connection.sendMessage(c.MOVE_STOP),
            ),
            c.TRAINING_TAB: (
                StoppedButtonCommand(main_window.saveEeg, main_window.isStopped),
                StoppedButtonCommand(main_window.loadEeg, main_window.isStopped),
                StoppedButtonCommand(main_window.resetEeg, main_window.isStopped),
            )
        }


class StoppedButtonCommand(object):
    def __init__(self, function, isStopped):
        self.function = function
        self.isStopped = isStopped

    def __call__(self, *args, **kwargs):
        if self.isStopped():
            self.function()
        else:
            print("This functionality can only be used if BCI is stopped")
