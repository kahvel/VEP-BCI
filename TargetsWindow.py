__author__ = 'Anti'
from psychopy import visual, core, logging, event


class Target:
    def __init__(self, target, window, monitor_frequency):
        self.rect = visual.Rect(window, width=int(target["Width"]), height=int(target["Height"]),
                                pos=(int(target["x"]), int(target["y"])), autoLog=False, fillColor=target["Color1"])
        self.freq = float(target["Freq"])
        self.sequence = "01"
        monitor_frequency = int(monitor_frequency)
        self.freq_on = int(monitor_frequency/self.freq//2)
        self.freq_off = int(monitor_frequency/self.freq/2.0+0.5)
        print "Frequency is " + str(float(monitor_frequency)/(self.freq_off+self.freq_on))

    def generator(self):
        while True:
            for c in self.sequence:
                for _ in range(self.freq_on):
                    yield
                    if c == "1":
                        self.rect.draw()
                for _ in range(self.freq_off):
                    yield


class TargetsWindow:
    def __init__(self, main_connection):
        logging.console.setLevel(logging.WARNING)
        self.generators = []
        self.window = None
        self.monitor_frequency = None
        # clock = core.Clock()
        #self.window._refreshThreshold = 1/60
        #self.window.setRecordFrameIntervals(True)
        #self.run()

    def setWindow(self, background_data):
        self.window = visual.Window([int(background_data["Width"]),
                                     int(background_data["Height"])],
                                    units="pix", color=background_data["Color"])
        self.monitor_frequency = background_data["Freq"]

    def setTargets(self, targets):
        for target in targets[1:]:
            rect = Target(target, self.window, self.monitor_frequency)
            self.generators.append(rect.generator())
            self.generators[-1].send(None)

    def run(self):
        while True:
            for generator in self.generators:
                generator.send(None)
            self.window.flip()
            if len(event.getKeys()) > 0:
                break
            event.clearEvents()
        self.window.close()


