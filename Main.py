__author__ = 'Anti'

if __name__ == "__main__":
    import MainWindow
    MainWindow.MainWindow()


def runPlotControl(main_conn, emo_conn, sensor_names):
    import PlotControlWindow
    PlotControlWindow.Window(main_conn, emo_conn, sensor_names)

def runEmotiv(main_conn):
    import MyEmotiv
    MyEmotiv.myEmotiv(main_conn)

def runPsychopy(connection, background_data, targets_data):
    import TargetsWindow
    win = TargetsWindow.TargetsWindow(connection)
    win.setWindow(background_data)
    win.setTargets(targets_data)
    win.run()