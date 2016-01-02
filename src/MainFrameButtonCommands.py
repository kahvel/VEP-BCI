import constants as c


class MainFrameButtonCommands(object):
    def __init__(self, main_window, bci_controller, training_controller):
        self.bci_controller = bci_controller
        self.training_controller = training_controller
        self.commands = {
            c.BOTTOM_FRAME: (
                    StoppedButtonCommand(bci_controller.start, training_controller.isStopped),
                    StoppedButtonCommand(bci_controller.stop, training_controller.isStopped),
                    StoppedButtonCommand(bci_controller.setup, training_controller.isStopped),
                    main_window.askSaveFile,
                    main_window.askLoadFile,
                    main_window.exit,
            ),
            c.TEST_TAB: (
                StoppedButtonCommand(main_window.showResults, self.isStopped),
                StoppedButtonCommand(main_window.resetResults, self.isStopped),
                StoppedButtonCommand(main_window.saveResults, self.isStopped),
            ),
            c.ROBOT_TAB: (
                lambda: main_window.connection.sendMessage(c.MOVE_FORWARD),
                lambda: main_window.connection.sendMessage(c.MOVE_BACKWARD),
                lambda: main_window.connection.sendMessage(c.MOVE_RIGHT),
                lambda: main_window.connection.sendMessage(c.MOVE_LEFT),
                lambda: main_window.connection.sendMessage(c.MOVE_STOP),
            ),
            c.TRAINING_TAB: (
                StoppedButtonCommand(main_window.saveEeg, self.isStopped),
                StoppedButtonCommand(main_window.loadEeg, self.isStopped),
                StoppedButtonCommand(main_window.resetEeg, self.isStopped),
                {
                    c.TRAIN_FRAME: (
                        StoppedButtonCommand(training_controller.start, bci_controller.isStopped),
                        StoppedButtonCommand(training_controller.stop, bci_controller.isStopped),
                        StoppedButtonCommand(training_controller.setup, bci_controller.isStopped),
                    )
                }
            )
        }

    def isStopped(self):
        return self.bci_controller.isStopped() and self.training_controller.isStopped()


class StoppedButtonCommand(object):
    def __init__(self, function, isStopped):
        self.function = function
        self.isStopped = isStopped

    def __call__(self, *args, **kwargs):
        if self.isStopped():
            self.function(*args)
        else:
            print("This functionality can only be used if BCI is stopped")
