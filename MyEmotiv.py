__author__ = 'Anti'
import emokit.emotiv
import gevent


class myEmotiv(emokit.emotiv.Emotiv):
    def __init__(self, connection):
        self.connection = connection
        self.devices = []
        self.serialNum = None
        emokit.emotiv.Emotiv.__init__(self)

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
                    self.cleanUp()
                    return
                continue
        while True:
            try:
                packet = self.packets.get(True, 1)
                # print packet
                self.connection.send(packet)
            except:
                ""
            if self.connection.poll():
                message = self.connection.recv()
                if message == "Stop":
                    break
            # packet = self.dequeue()
            # print packet
            # self.connection.send(packet)
        self.connection.close()
        self.cleanUp()