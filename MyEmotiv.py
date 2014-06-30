__author__ = 'Anti'
from emokit import emotiv
import gevent

class myEmotiv:
    def __init__(self):
        self.headset = emotiv.Emotiv()
        gevent.spawn(self.headset.setup)
        gevent.sleep(1)
        self.list = [[] for _ in range(14)]
        self.names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
        self.fft_gen = None
        self.do_fft = False
        self.plot_gen = None
        self.do_plot = False

    def setFft(self, fft_window):
        self.fft_gen = fft_window.generator()
        self.fft_gen.send(None)
        self.do_fft = True

    def setPlot(self, plot_window):
        self.plot_gen = []
        for i in range(13):
            self.plot_gen.append(plot_window.test7(i*35,35))
            self.plot_gen[i].send(None)
        self.plot_gen.append(plot_window.test8(13*35,35))
        self.plot_gen[-1].send(None)
        self.do_plot = True

    def run(self):
        # try:
            while True:
                packet = self.headset.dequeue()
                if self.do_plot:
                    for i in range(14):
                        if not self.plot_gen[i].send(packet.sensors[self.names[i]]["value"]):
                            self.do_plot = False
                if self.do_fft:
                    if not self.fft_gen.send(packet.AF3[0]):
                        self.do_fft = False

                if not self.do_fft and not self.do_plot:
                    break


                # self.list[0].append(packet.AF3[0])
                # self.list[1].append(packet.F7[0])
                # self.list[2].append(packet.F3[0])
                # self.list[3].append(packet.FC5[0])
                # self.list[4].append(packet.T7[0])
                # self.list[5].append(packet.P7[0])
                # self.list[6].append(packet.O1[0])
                # self.list[7].append(packet.O2[0])
                # self.list[8].append(packet.P8[0])
                # self.list[9].append(packet.T8[0])
                # self.list[10].append(packet.FC6[0])
                # self.list[11].append(packet.F4[0])
                # self.list[12].append(packet.F8[0])
                # self.list[13].append(packet.AF4[0])

                gevent.sleep(0)
        # except KeyboardInterrupt:
        #     self.headset.close()
        # finally:
        #     # for l in self.list:
        #     #     print(max(l), min(l), sum(l)/len(l))
        #     self.headset.close()
            for gen in self.plot_gen:
                while True:
                    try:
                        gen.send(1)
                        print("saadetud")
                    except:
                        print("tyhi")
                        break
            while True:
                try:
                    self.fft_gen.send(1)
                except:
                    break

