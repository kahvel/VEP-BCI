__author__ = 'Anti'

if __name__ == "__main__":
    import MainWindow
    MainWindow.MainWindow()


def runPostOffice(connection):
    import PostOffice
    PostOffice.PostOffice(connection)

def runPlotControl(connection, args):
    import PlotControlWindow
    PlotControlWindow.Window(connection, args[0])

def runEmotiv(connection, args):
    import MyEmotiv
    MyEmotiv.myEmotiv(connection)

def runPsychopy(connection, args):
    import TargetsWindow
    TargetsWindow.TargetsWindow(connection, args[0])

def runPSIdentification(connection, args):
    import ExtractionControlWindow
    ExtractionControlWindow.Window(connection, args[0])