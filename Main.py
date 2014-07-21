__author__ = 'Anti'

if __name__ == "__main__":
    import MainWindow
    MainWindow.MainWindow()


def runPlotControl(plot_to_main, plot_to_emo, args):
    import PlotControlWindow
    PlotControlWindow.Window(plot_to_main, plot_to_emo, args[0])

def runEmotiv(main_conn):
    import MyEmotiv
    MyEmotiv.myEmotiv(main_conn)

def runPsychopy(psy_to_main, psy_to_emo, args):
    import TargetsWindow
    TargetsWindow.TargetsWindow(psy_to_main, psy_to_emo, args[0], args[1])

def runPSIdentification(ps_to_main, ps_to_emo, args):
    import PSIdentification
    PSIdentification.PSIdentification(ps_to_main, ps_to_emo)