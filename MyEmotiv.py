from gevent.queue import Queue

__author__ = 'Anti'
import emokit.emotiv
import gevent

class myEmotiv(emokit.emotiv.Emotiv):
    def __init__(self):
        self.devices = []
        self.serialNum = None
        emokit.emotiv.Emotiv.__init__(self)
        self.names = ["AF3", "F7", "F3", "FC5", "T7", "P7", "O1", "O2", "P8", "T8", "FC6", "F4", "F8", "AF4"]
        self.fft_gen = None
        self.fft_window = None
        self.do_fft = False
        self.plot_gen = None
        self.plot_window = None
        self.do_plot = False
        self.average_fft_gen = None
        self.average_fft_window = None
        self.do_average_fft = False
        self.average_plot_gen = None
        self.average_plot_window = None
        self.do_average_plot = False

    def setFFT(self, fft_window):
        if fft_window is not None:
            self.fft_gen = fft_window.generator()
            self.fft_gen.send(None)
            self.fft_window = fft_window
            self.do_fft = True

    def setPlot(self, plot_window):
        if plot_window is not None:
            self.plot_gen = []
            for i in range(14):
                self.plot_gen.append(plot_window.generator(i, 35))
                self.plot_gen[i].send(None)
            self.plot_window = plot_window
            self.do_plot = True

    def setAveragePlot(self, average_plot_window):
        if average_plot_window is not None:
            self.average_plot_gen = []
            for i in range(14):
                self.average_plot_gen.append(average_plot_window.generator(i, 35))
                self.average_plot_gen[i].send(None)
            self.average_plot_window = average_plot_window
            self.do_average_plot = True

    def setAverageFFT(self, average_fft_window):
        if average_fft_window is not None:
            self.average_fft_gen = average_fft_window.generator()
            self.average_fft_gen.send(None)
            self.average_fft_window = average_fft_window
            self.do_average_fft = True

    def setupWin(self):
        for device in emokit.emotiv.hid.find_all_hid_devices():
            if device.vendor_id != 0x21A1 and device.vendor_id != 0x1234:
                continue
            if device.product_name == 'Brain Waves':
                self.devices.append(device)
                device.open()
                self.serialNum = device.serial_number
                device.set_raw_data_handler(self.handler)
            elif device.product_name == 'EPOC BCI':
                self.devices.append(device)
                device.open()
                self.serialNum = device.serial_number
                device.set_raw_data_handler(self.handler)
            elif device.product_name == '00000000000':
                self.devices.append(device)
                device.open()
                self.serialNum = device.serial_number
                device.set_raw_data_handler(self.handler)
            elif device.product_name == 'Emotiv RAW DATA':
                self.devices.append(device)
                device.open()
                self.serialNum = device.serial_number
                device.set_raw_data_handler(self.handler)

    def closeDevices(self):
        for device in self.devices:
            device.close()

    def handler(self, data):
        assert data[0] == 0
        if self._goOn:
            emokit.emotiv.tasks.put_nowait(''.join(map(chr, data[1:])))
            self.packetsReceived += 1
            return True

    def cleanUp(self):
        self._goOn = False
        self.closeDevices()
        print("CleanUp successful!")

    def cleanUpAll(self):
        self.cleanUpFft()
        self.cleanUpPlot()
        self.cleanUpAvgFFT()
        self.cleanUpAvgPlot()
        self.cleanUp()

    def cleanUpPlot(self):
        if self.plot_window is not None:
            self.do_plot = False
            self.plot_window.destroy()
            self.plot_window = None
            for gen in self.plot_gen:
                while True:
                    try:
                        gen.send(1)
                        print("Send plot")
                    except:
                        print("Empty")
                        break

    def cleanUpAvgPlot(self):
        if self.average_plot_window is not None:
            self.do_average_plot = False
            self.average_plot_window.destroy()
            self.average_plot_window = None
            for gen in self.average_plot_gen:
                while True:
                    try:
                        gen.send(1)
                        print("Send plot")
                    except:
                        print("Empty")
                        break

    def cleanUpFft(self):
        if self.fft_window is not None:
            self.do_fft = False
            self.fft_window.destroy()
            self.fft_window = None
            while True:
                try:
                    self.fft_gen.send(1)
                    print("Send fft")
                except:
                    print("Empty")
                    break

    def cleanUpAvgFFT(self):
        if self.average_fft_window is not None:
            self.do_average_fft = False
            self.average_fft_window.destroy()
            self.average_fft_window = None
            while True:
                try:
                    self.average_fft_gen.send(1)
                    print("Send avg")
                except:
                    print("Empty")
                    break

    def run(self):
        self._goOn = True
        self.setup()
        gevent.spawn(self.setupCrypto, self.serialNum)
        gevent.sleep(1)
        while True:
            counter = 0
            while True:
                try:
                    packet = self.packets.get(True, 1)
                    break
                except:
                    # gevent.sleep(0)
                    counter += 1
                    print("No packet! " + str(counter))
                    if counter == 10:
                        print("Terminating!")
                        self.cleanUpAll()
                        return
                    continue
            if self.do_plot:
                for i in range(14):
                    if not self.plot_gen[i].send(packet.sensors[self.names[i]]["value"]):
                        self.cleanUpPlot()
                        break
            if self.do_average_plot:
                for i in range(14):
                    if not self.average_plot_gen[i].send(packet.sensors[self.names[i]]["value"]):
                        self.cleanUpPlot()
                        break
            if self.do_fft:
                if not self.fft_gen.send(packet.O2[0]):
                    self.cleanUpFft()
            if self.do_average_fft:
                if not self.average_fft_gen.send(packet.O2[0]):
                    self.cleanUpAvgFFT()
            if not self.do_fft and not self.do_plot and not self.do_average_fft and not self.do_average_plot:
                print("Nothing to do!")
                break
        self.cleanUp()