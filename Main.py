__author__ = 'Anti'
# import multiprocessing

if __name__ == "__main__":
    import MainWindow
    mainWindow = MainWindow.MainWindow()
# elif __name__ == "__parents_main__":
#     if multiprocessing.current_process().name == "Emotiv-process":
#         import MyEmotiv
#         emo = MyEmotiv.myEmotiv()
#         emo.run()


def runPlotControl(connection, sensor_names):
    import asd
    asd.Window(connection, sensor_names)

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