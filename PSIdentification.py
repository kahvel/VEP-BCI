__author__ = 'Anti'
import numpy as np
from scipy import signal


class PSIdentification(object):
    def __init__(self, ps_to_main, ps_to_emo):
        self.ps_to_emo = ps_to_emo
        self.ps_to_main = ps_to_main
        self.packet_count = 640
        self.freq_points = [10]
        self.freq_indexes = []
        self.channel_count = 2
        self.sensor_names = ["O1", "O2"]
        self.myMainloop()

    def myMainloop(self):
        while True:
            while not self.ps_to_main.poll(1):
                pass
            message = self.ps_to_main.recv()
            if message == "Start":
                print "Starting PS"
                message = self.run()
            if message == "Stop":
                print "PS stopped"
            if message == "Exit":
                print "Exiting PS"
                break

    def recvPacket(self):
        while True:
            if self.ps_to_main.poll():
                message = self.ps_to_main.recv()
                return message
            if self.ps_to_emo.poll(0.1):
                return self.ps_to_emo.recv()

    # def sendPacket(self, packet):
    #     for i in range(self.channel_count):
    #         self.generators[0].send(packet.sensors[self.sensor_names[i]]["value"])

    def run(self):
        coordinate_generator = self.gen(self.packet_count)
        coordinate_generator.send(None)
        for freq in self.freq_points:
            self.freq_indexes.append(freq*self.packet_count/128)
        while True:
            for i in range(self.packet_count):
                packet = self.recvPacket()
                if isinstance(packet, basestring):
                    return packet
                for i in range(self.channel_count):
                    coordinates = coordinate_generator.send(packet.sensors[self.sensor_names[i]]["value"])
            print coordinates[self.freq_indexes[0]]*2/(coordinates[self.freq_indexes[0]-1]+coordinates[self.freq_indexes[0]+1])
            coordinate_generator.next()

    def gen(self, packet_count):
        average = [0 for _ in range(packet_count/2+1)]
        coordinates = []
        for _ in range(self.channel_count):
            coordinates.append([0 for _ in range(packet_count)])
        while True:
            for i in range(packet_count):
                for j in range(self.channel_count):
                    y = yield
                    coordinates[j][i] = y
            ffts = []
            for i in range(self.channel_count):
                ffts.append(np.abs(np.fft.rfft(signal.detrend(coordinates[i]))))
            for i in range(len(ffts[0])):
                sum = 0
                for j in range(self.channel_count):
                    sum += ffts[j][i]
                average[i] = sum/self.channel_count
            yield np.log10(average)