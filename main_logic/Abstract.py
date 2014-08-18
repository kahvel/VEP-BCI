__author__ = 'Anti'


class Multiple(object):
    def getGenCount(self, channel_count):
        return channel_count

    def sendPacket(self, packet, generators, sensor_names):
        for i in range(len(sensor_names)):
            generators[i].send(float(packet.sensors[sensor_names[i]]["value"]))


class Single(object):
    def getGenCount(self, channel_count):
        return 1

    def sendPacket(self, packet, generators, sensor_names):
        for i in range(len(sensor_names)):
            generators[0].send(float(packet.sensors[sensor_names[i]]["value"]))