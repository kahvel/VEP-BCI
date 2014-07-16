__author__ = 'Anti'
import emokit.emotiv
import gevent
from multiprocessing import reduction


class myEmotiv(emokit.emotiv.Emotiv):
    def __init__(self, main_conn):
        self.main_conn = main_conn
        self.connections = []
        self.devices = []
        self.serialNum = None
        emokit.emotiv.Emotiv.__init__(self)
        self.waitConnections()

    def waitConnections(self):
        while True:
            while not self.main_conn.poll(1):
                pass
            message = self.main_conn.recv()
            if message == "New pipe":
                print "Adding pipe"
                connection = reduction.rebuild_pipe_connection(*self.main_conn.recv()[1])
                self.connections.append(connection)
            if message == "Start":
                print "Starting emotiv"
                self.run()
            if message == "Stop":
                print "Stop emotiv"
                break


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
                self.connections[0].send(packet)
            except:
                ""
            if self.connections[0].poll():
                message = self.connections[0].recv()
                if message == "Stop":
                    break
            # packet = self.dequeue()
            # print packet
            # self.connection.send(packet)
        # self.connections[0].close()
        self.cleanUp()