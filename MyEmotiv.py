__author__ = 'Anti'
import emokit.emotiv
import gevent


class AbstractPlot:
    def __init__(self):
        self.generator = None
        self.window = None
        self.do = False
        self.sensor_names = []
        self.plot_count = 0

    def setup(self, window):
        if window is not None:
            self.generator = []
            for i in range(self.plot_count):
                self.generator.append(window.generator(i, self.plot_count))
                self.generator[i].send(None)
            self.window = window
            self.do = True

    def cleanUp(self):
        if self.window is not None:
            self.do = False
            self.window.destroy()
            self.window = None
            for gen in self.generator:
                while True:
                    try:
                        gen.send(1)
                        print("Send")
                    except:
                        print("Empty")
                        break

    def sendPacket(self, packet):
        if self.do:
            for i in range(self.plot_count):
                if not self.generator[i].send(packet.sensors[self.sensor_names[i]]["value"]):
                    self.cleanUp()
                    break


class Plot(AbstractPlot):
    def __init__(self):
        AbstractPlot.__init__(self)

    def calculateAverage(self, packets):
        if self.do:
            averages = [0 for _ in range(self.plot_count)]
            for j in range(1, len(packets)+1):
                for i in range(self.plot_count):
                    averages[i] = (averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]) / j
            for i in range(self.plot_count):
                self.generator[i].send(averages[i])
            print(averages)

    def setSensorNames(self, checkbox_values, sensor_names):
        self.plot_count = 0
        self.sensor_names = []
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.plot_count += 1
                self.sensor_names.append(sensor_names[i])

class AveragePlot(AbstractPlot):
    def __init__(self):
        AbstractPlot.__init__(self)
        self.actual_plot_count = 0

    def setSensorNames(self, checkbox_values, sensor_names):
        self.plot_count = 1
        self.actual_plot_count = 0
        self.sensor_names = []
        for i in range(len(checkbox_values)):
            if checkbox_values[i].get() == 1:
                self.actual_plot_count += 1
                self.sensor_names.append(sensor_names[i])

    def calculateAverage(self, packets):
        if self.do:
            averages = [0 for _ in range(self.actual_plot_count)]
            for j in range(1, len(packets)+1):
                for i in range(self.actual_plot_count):
                    averages[i] = (averages[i] * (j - 1) + packets[j-1].sensors[self.sensor_names[i]]["value"]) / j
            self.generator[0].send(averages)
            print(averages)

class myEmotiv(emokit.emotiv.Emotiv):
    def __init__(self):
        self.devices = []
        self.serialNum = None
        emokit.emotiv.Emotiv.__init__(self)
        self.fft = Plot()
        self.signal = Plot()
        self.avg_fft = Plot()
        self.avg_mul_ffts = AveragePlot()
        self.avg_signal = Plot()
        self.avg_mul_signals = AveragePlot()

    def setFFT(self, fft_window, checkbox_values, sensor_names):
        self.fft.setSensorNames(checkbox_values, sensor_names)
        self.fft.setup(fft_window)

    def setPlot(self, plot_window, checkbox_values, sensor_names):
        self.signal.setSensorNames(checkbox_values, sensor_names)
        self.signal.setup(plot_window)

    def setAverage(self, average_window, checkbox_values, sensor_names):
        self.avg_mul_signals.setSensorNames(checkbox_values, sensor_names)
        self.avg_mul_signals.setup(average_window)

    def setAverageFFT2(self, average_window, checkbox_values, sensor_names):
        self.avg_mul_ffts.setSensorNames(checkbox_values, sensor_names)
        self.avg_mul_ffts.setup(average_window)

    def setAveragePlot(self, average_plot_window, checkbox_values, sensor_names):
        self.avg_signal.setSensorNames(checkbox_values, sensor_names)
        self.avg_signal.setup(average_plot_window)

    def setAverageFFT(self, average_fft_window, checkbox_values, sensor_names):
        self.avg_fft.setSensorNames(checkbox_values, sensor_names)
        self.avg_fft.setup(average_fft_window)

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
        self.avg_fft.cleanUp()
        self.avg_mul_ffts.cleanUp()
        self.fft.cleanUp()
        self.signal.cleanUp()
        self.avg_signal.cleanUp()
        self.avg_mul_signals.cleanUp()
        self.cleanUp()

    def run(self):
        self._goOn = True
        self.setup()
        gevent.spawn(self.setupCrypto, self.serialNum)
        gevent.sleep(1)
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

        if self.signal.do or self.avg_signal.do or self.avg_mul_signals.do:
            print("Calculating averages")
            packets = []
            for _ in range(1, 512):
                packet = self.dequeue()
                packets.append(packet)
            self.signal.calculateAverage(packets)
            self.avg_signal.calculateAverage(packets)
            self.avg_mul_signals.calculateAverage(packets)

        while True:
            packet = self.dequeue()
            self.signal.sendPacket(packet)
            self.avg_signal.sendPacket(packet)
            self.avg_mul_signals.sendPacket(packet)
            self.avg_mul_ffts.sendPacket(packet)
            self.fft.sendPacket(packet)
            self.avg_fft.sendPacket(packet)
            if not self.avg_fft.do and not self.fft.do and not self.avg_mul_ffts.do and not \
               self.avg_signal.do and not self.signal.do and not self.avg_mul_signals.do:
                print("Nothing to do!")
                break
        self.cleanUp()