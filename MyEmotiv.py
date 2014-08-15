__author__ = 'Anti'

import emokit.emotiv
from Crypto.Cipher import AES
from Crypto import Random


class myEmotiv(emokit.emotiv.Emotiv):
    def __init__(self, connection):
        self.connection = connection
        self.devices = []
        self.serialNum = None
        emokit.emotiv.Emotiv.__init__(self)
        self.cipher = None
        self.myMainloop()

    def myMainloop(self):
        while True:
            while not self.connection.poll(1):
                pass
            message = self.connection.recv()
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
        self.packets.put_nowait(''.join(map(chr, data[1:])))
        return True

    def cleanUp(self):
        self._goOn = False
        self.closeDevices()

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

    def run(self):
        # Clean up possible previous packets from the queue
        while True:
            try:
                self.packets.get(False)
            except:
                break

        # Make sure we get packets
        self.setup()
        if self.serialNum == None:
            print "USB not connected"
            return "Stop"
        self.setupCrypto(self.serialNum)
        try:
            task = self.packets.get(True, 1)
        except:
            print "Turn on headset"
            return "Stop"

        # Mainloop
        # send message to psychopy
        while True:
            try:
                data = self.cipher.decrypt(task[:16]) + self.cipher.decrypt(task[16:])
                packet = emokit.emotiv.EmotivPacket(data, self.sensors)
                task = self.packets.get(True, 0.01)
                self.connection.send(packet)
                # print "Emotiv " + str(packet)
                if self.packets.qsize() > 150:
                    print self.packets.qsize(), "packets in queue. Slow down!"
            except Exception, e:
                print "No packet", e
            if self.connection.poll():
                return self.connection.recv()