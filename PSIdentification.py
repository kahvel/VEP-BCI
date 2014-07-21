__author__ = 'Anti'
import numpy as np
from scipy import signal
import sklearn.cross_decomposition


class PSIdentification(object):
    def __init__(self, ps_to_main, ps_to_emo):
        self.ps_to_emo = ps_to_emo
        self.ps_to_main = ps_to_main
        self.packet_count = 128
        self.freq_points = []
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
                self.freq_points = self.ps_to_main.recv()
                self.freq_indexes = []
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

    def run(self):
        coordinate_generator = self.gen(self.packet_count)
        coordinate_generator.send(None)
        for freq in self.freq_points:
            self.freq_indexes.append(freq*self.packet_count/128)
        # print self.freq_points
        # print self.freq_indexes
        # print (np.fft.rfftfreq(256)*128)
        while True:
            for i in range(self.packet_count):
                packet = self.recvPacket()
                if isinstance(packet, basestring):
                    coordinate_generator.close()
                    return packet
                for i in range(self.channel_count):
                    coordinates = coordinate_generator.send(packet.sensors[self.sensor_names[i]]["value"])
            max = 0
            max_index = -1
            for i in range(len(self.freq_indexes)):
                ratio = coordinates[self.freq_indexes[i]]*2/(coordinates[self.freq_indexes[i]-1]+coordinates[self.freq_indexes[i]+1])
                if ratio > max:
                    max = ratio
                    max_index = i
                # print ratio,
            if max < 1:
                print "Ratio < 1",
            print self.freq_points[max_index]
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