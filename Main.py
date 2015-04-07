__author__ = 'Anti'


if __name__ == "__main__":
    import PostOffice
    PostOffice.PostOffice()


def runMainWindow(connection):
    from main_window import MainWindow
    MainWindow.MainWindow(connection)


def runPlotControl(connection):
    # from control_windows import PlotControlWindow
    # PlotControlWindow.Window(connection)
    import Plot
    Plot.Plot(connection)


def runEmotiv(connection):
    import MyEmotiv
    MyEmotiv.myEmotiv(connection)


def runPsychopy(connection):
    import TargetsWindow
    TargetsWindow.TargetsWindow(connection)


def runExtractionControl(connection):
    # from control_windows import ExtractionControlWindow
    # ExtractionControlWindow.Window(connection)
    pass


def runGame(connection):
    # import Game
    # Game.Game(connection)
    pass
