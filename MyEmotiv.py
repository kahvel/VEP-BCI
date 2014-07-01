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

    def setFft(self, fft_window):
        if fft_window is not None:
            self.fft_gen = fft_window.generator()
            self.fft_gen.send(None)
            self.fft_window = fft_window
            self.do_fft = True

    def setPlot(self, plot_window):
        if plot_window is not None:
            self.plot_gen = []
            for i in range(13):
                self.plot_gen.append(plot_window.test7(i*35,35))
                self.plot_gen[i].send(None)
            self.plot_gen.append(plot_window.test8(13*35,35))
            self.plot_gen[-1].send(None)
            self.plot_window = plot_window
            self.do_plot = True

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
        if self.fft_window is not None:
            self.fft_window.exit2()
        if self.plot_window is not None:
            self.plot_window.exit2()
        if self.plot_gen is not None:
            for gen in self.plot_gen:
                while True:
                    try:
                        gen.send(1)
                        print("Send")
                    except:
                        print("Empty")
                        break
        if self.fft_gen is not None:
            while True:
                try:
                    self.fft_gen.send(1)
                    print("Send")
                except:
                    print("Empty")
                    break
        if self.fft_window is not None:
            self.fft_window.destroy()
            self.fft_window = None
        if self.plot_window is not None:
            self.plot_window.destroy()
            self.plot_window = None
        self.do_fft = False
        self.do_plot = False
        self.closeDevices()
        print("CleanUp successful!")

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
                    counter += 1
                    print("No packet! " + str(counter))
                    if counter == 10:
                        print("Terminating!")
                        self.cleanUp()
                        return
                    continue
            if self.do_plot:
                for i in range(14):
                    if not self.plot_gen[i].send(packet.sensors[self.names[i]]["value"]):
                        self.do_plot = False
                        self.plot_window.destroy()
                        #self.plot_window = None
            if self.do_fft:
                if not self.fft_gen.send(packet.AF3[0]):
                    self.do_fft = False
                    self.fft_window.destroy()
                    #self.fft_window = None

            if not self.do_fft and not self.do_plot:
                self._goOn = False
                print("Nothing to do!")
                break
            #gevent.sleep(0)
        self.cleanUp()


