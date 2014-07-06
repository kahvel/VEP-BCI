__author__ = 'Anti'
from psychopy import visual, core, logging, event


class Target:
    def __init__(self, target, window, monitor_frequency):
        self.rect = visual.Rect(window, width=int(target["Width"]), height=int(target["Height"]),
                                pos=(int(target["x"]), int(target["y"])), autoLog=False, fillColor=target["Color1"])
        self.freq = float(target["Freq"])
        self.sequence = "01"
        self.freq_on = int(int(monitor_frequency)/self.freq//2)
        self.freq_off = int(int(monitor_frequency)/self.freq/2.0+0.5)

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
    def __init__(self, background_textboxes, targets):
        self.window = visual.Window([int(background_textboxes["Width"].get()),
                                     int(background_textboxes["Height"].get())],
                                    units="pix", color=background_textboxes["Color"].get())
        self.monitor_frequency = background_textboxes["Freq"].get()
        #self.window._refreshThreshold = 1/60
        logging.console.setLevel(logging.WARNING)
        self.generators = []
        for target in targets[1:]:
            rect = Target(target, self.window, self.monitor_frequency)
            self.generators.append(rect.generator())
            self.generators[-1].send(None)
        clock = core.Clock()
        #self.window.setRecordFrameIntervals(True)
        self.run()

    def run(self):
        while True:
            for generator in self.generators:
                generator.send(None)
            self.window.flip()
            if len(event.getKeys()) > 0:
                break
            event.clearEvents()
        self.window.close()
        #core.quit()


