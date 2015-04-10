__author__ = 'Anti'

import emokit.emotiv
from Crypto.Cipher import AES
from Crypto import Random
import constants as c
import Queue


class myEmotiv(object):
    def __init__(self, connection):
        # self.lock = args[0]
        # self.lock.acquire()
        self.connection = connection
        """ @type : ConnectionProcessEnd.Connection """
        self.devices = []
        self.serialNum = None
        self.packets = Queue.Queue()
        self.cipher = None
        self.sensors = {
            'F3': {'value': 0, 'quality': 0},
            'FC6': {'value': 0, 'quality': 0},
            'P7': {'value': 0, 'quality': 0},
            'T8': {'value': 0, 'quality': 0},
            'F7': {'value': 0, 'quality': 0},
            'F8': {'value': 0, 'quality': 0},
            'T7': {'value': 0, 'quality': 0},
            'P8': {'value': 0, 'quality': 0},
            'AF4': {'value': 0, 'quality': 0},
            'F4': {'value': 0, 'quality': 0},
            'AF3': {'value': 0, 'quality': 0},
            'O2': {'value': 0, 'quality': 0},
            'O1': {'value': 0, 'quality': 0},
            'FC5': {'value': 0, 'quality': 0},
            'X': {'value': 0, 'quality': 0},
            'Y': {'value': 0, 'quality': 0},
            'Unknown': {'value': 0, 'quality': 0}
        }
        self.connection.waitMessages(self.start, self.cleanUp, lambda: None, self.connectionSetup)

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
        for i in range(len(self.devices)-1, -1, -1):
            self.devices[i].close()
            del self.devices[i]

    def handler(self, data):
        assert data[0] == 0
        self.packets.put_nowait(''.join(map(chr, data[1:])))
        return True

    def cleanUp(self):
        self.closeDevices()
        self.connection.closeConnection()

    def setupCrypto(self, sn):
        type = 0 # feature[5]
        type &= 0xF
        type = 0
        # I believe type == True is for the Dev headset, I'm not using that. That's the point of this library in the first place I thought.
        k = ['\0'] * 16
        k[0] = sn[-1]
        k[1] = '\0'
        k[2] = sn[-2]
        if type:
            k[3] = 'H'
            k[4] = sn[-1]
            k[5] = '\0'
            k[6] = sn[-2]
            k[7] = 'T'
            k[8] = sn[-3]
            k[9] = '\x10'
            k[10] = sn[-4]
            k[11] = 'B'
        else:
            k[3] = 'T'
            k[4] = sn[-3]
            k[5] = '\x10'
            k[6] = sn[-4]
            k[7] = 'B'
            k[8] = sn[-1]
            k[9] = '\0'
            k[10] = sn[-2]
            k[11] = 'H'
        k[12] = sn[-3]
        k[13] = '\0'
        k[14] = sn[-4]
        k[15] = 'P'
        # It doesn't make sense to have more than one greenlet handling this as data needs to be in order anyhow. I guess you could assign an ID or something
        # to each packet but that seems like a waste also or is it? The ID might be useful if your using multiple headsets or usb sticks.
        key = ''.join(k)
        iv = Random.new().read(AES.block_size)
        self.cipher = AES.new(key, AES.MODE_ECB, iv)

    def connectionSetup(self):
        # Clean up possible previous packets from the queue
        while True:
            try:
                self.packets.get(False)
            except:
                break
        return c.SUCCESS_MESSAGE

    def start(self):
        self.setupWin()
        if self.serialNum is None:
            print("Emotiv USB receiver not found")
            self.closeDevices()
            return c.FAIL_MESSAGE
        self.setupCrypto(self.serialNum)
        # try:
        #     task = self.packets.get(True, 0.1)
        # except:
        #     print "Turn on headset"
        #     return "Stop"

        # Mainloop
        # self.lock.release()  # synchronising with psychopy
        while True:
            try:
                task = self.packets.get(True, 0.01)
                data = self.cipher.decrypt(task[:16]) + self.cipher.decrypt(task[16:])
                packet = emokit.emotiv.EmotivPacket(data, self.sensors)
                self.connection.sendMessage(packet)
                # print "Emotiv " + str(packet)
                if self.packets.qsize() > 6:
                    print(str(self.packets.qsize()) + " packets in queue.")
            except Queue.Empty:
                pass
                #print("No packet")
            message = self.connection.receiveMessageInstant()
            if message is not None:
                self.closeDevices()
                return message