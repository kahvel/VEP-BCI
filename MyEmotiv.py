__author__ = 'Anti'
import emokit.emotiv
import gevent
from multiprocessing import reduction


class myEmotiv(emokit.emotiv.Emotiv):
    def __init__(self, emo_to_main):
        self.emo_to_main = emo_to_main
        self.emo_to_psychopy = []
        self.connections = []
        self.devices = []
        self.serialNum = None
        emokit.emotiv.Emotiv.__init__(self)
        self.myMainloop()

    def myMainloop(self):
        while True:
            while not self.emo_to_main.poll(1):
                pass
            message = self.emo_to_main.recv()
            if message == "New pipe":
                print "Adding pipe"
                connection = reduction.rebuild_pipe_connection(*self.emo_to_main.recv()[1])
                self.connections.append(connection)
            elif message == "Psychopy":
                print "Adding pipe"
                connection = reduction.rebuild_pipe_connection(*self.emo_to_main.recv()[1])
                self.emo_to_psychopy.append(connection)
            if message == "Start":
                print "Starting emotiv"
                message = self.run()
                self.cleanUp()
            if message == "Stop":
                print "Emotiv stopped"
            if message == "Exit":
                print "Exiting emotiv"
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
        print("Emotiv cleanup successful")

    def sendMessage(self, connections, message, name):
        for i in range(len(connections)-1, -1, -1):
            if connections[i].poll():
                print "Main to " + name + " closed"
                connections[i].close()
                del connections[i]
            else:
                 connections[i].send(message)

    def run(self):
        self._goOn = True
        self.setup()
        gevent.spawn(self.setupCrypto, self.serialNum)
        gevent.sleep(1)
        counter = 0
        while True:
            try:
                self.packets.get(True, 1)
                break
            except:
                # gevent.sleep(0)
                if self.emo_to_main.poll():
                    return self.emo_to_main.recv()
                counter += 1
                print("No packet " + str(counter))
                if counter == 10:
                    return "Stop"
        self.sendMessage(self.emo_to_psychopy, "Start", "Pscyhopy")
        while True:
            try:
                packet = self.packets.get(True, 1)
                for i in range(len(self.connections)-1, -1, -1):
                    if self.connections[i].poll():
                        print "Emo to plot closed"
                        self.connections[i].close()
                        del self.connections[i]
                    else:
                        self.connections[i].send(packet)
                # print packet
            except Exception, e:
                print "No packet"
            if self.emo_to_main.poll():
                return self.emo_to_main.recv()