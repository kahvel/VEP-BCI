__author__ = 'Anti'

if __name__ == "__main__":
    import MainWindow
    MainWindow.MainWindow()


def runPlotControl(plot_to_main, plot_to_emo, sensor_names):
    import PlotControlWindow
    PlotControlWindow.Window(plot_to_main, plot_to_emo, sensor_names)

def runEmotiv(main_conn):
    import MyEmotiv
    MyEmotiv.myEmotiv(main_conn)

def runPsychopy(psy_to_main, background_data, targets_data):
    import TargetsWindow
    win = TargetsWindow.TargetsWindow(psy_to_main)
    win.setWindow(background_data)
    win.setTargets(targets_data)
    win.run()

def runPSIdentification(ps_to_main, ps_to_emo, asd):
    import PSIdentification
    PSIdentification.PSIdentification(ps_to_main, ps_to_emo)