__author__ = 'Anti'

if __name__ == "__main__":
    import MainWindow
    mainWindow = MainWindow.MainWindow()

def runPlotControl(connection, sensor_names):
    import PlotControlWindow
    PlotControlWindow.Window(connection, sensor_names)

def runEmotiv(connection):
    import MyEmotiv
    emo = MyEmotiv.myEmotiv(connection)
    emo.run()

def runPsychopy(connection, background_data, targets_data):
    import TargetsWindow
    win = TargetsWindow.TargetsWindow(connection)
    win.setWindow(background_data)
    win.setTargets(targets_data)
    win.run()