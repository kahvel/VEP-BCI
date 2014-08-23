__author__ = 'Anti'


if __name__ == "__main__":
    from main_window import MainWindow
    MainWindow.MainWindow()


def runPostOffice(connection):
    import PostOffice
    PostOffice.PostOffice(connection)


def runPlotControl(connection, args):
    from control_windows import PlotControlWindow
    PlotControlWindow.Window(connection, args)


def runEmotiv(connection, args):
    import MyEmotiv
    MyEmotiv.myEmotiv(connection, args)


def runPsychopy(connection, args):
    import TargetsWindow
    TargetsWindow.TargetsWindow(connection, args)


def runExtractionControl(connection, args):
    from control_windows import ExtractionControlWindow
    ExtractionControlWindow.Window(connection, args)


def runGame(connection, args):
    import Game
    Game.Game(connection)