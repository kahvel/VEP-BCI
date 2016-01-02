import constants as c


class MainFrameButtonCommands(object):
    def __init__(self, main_window, bci_controller):
        self.commands = {
            c.BOTTOM_FRAME: (
                    bci_controller.start,
                    bci_controller.stop,
                    bci_controller.setup,
                    main_window.askSaveFile,
                    main_window.askLoadFile,
                    main_window.exit,
            ),
            c.TEST_TAB: (
                StoppedButtonCommand(main_window.showResults, bci_controller.isStopped),
                StoppedButtonCommand(main_window.resetResults, bci_controller.isStopped),
                StoppedButtonCommand(main_window.saveResults, bci_controller.isStopped),
            ),
            c.ROBOT_TAB: (
                lambda: main_window.connection.sendMessage(c.MOVE_FORWARD),
                lambda: main_window.connection.sendMessage(c.MOVE_BACKWARD),
                lambda: main_window.connection.sendMessage(c.MOVE_RIGHT),
                lambda: main_window.connection.sendMessage(c.MOVE_LEFT),
                lambda: main_window.connection.sendMessage(c.MOVE_STOP),
            ),
            c.TRAINING_TAB: (
                StoppedButtonCommand(main_window.saveEeg, bci_controller.isStopped),
                StoppedButtonCommand(main_window.loadEeg, bci_controller.isStopped),
                StoppedButtonCommand(main_window.resetEeg, bci_controller.isStopped),
            )
        }


class StoppedButtonCommand(object):
    def __init__(self, function, isStopped):
        self.function = function
        self.isStopped = isStopped

    def __call__(self, *args, **kwargs):
        if self.isStopped():
            self.function(*args)
        else:
            print("This functionality can only be used if BCI is stopped")
