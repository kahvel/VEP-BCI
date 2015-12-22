import Savable


class EEG(Savable.Savable, Savable.Loadable):
    def __init__(self):
        self.packets = []
        self.expected_targets = []

    def save(self, file):
        file.write(self.packets)
        file.write(";")
        file.write(self.expected_targets)

    def load(self, file):
        file_content = file.read().split(";")
        self.packets = eval(file_content[0])
        self.expected_targets = eval(file_content[1])

    def add_packet(self, packet):
        self.packets.append(packet)

    def new_target(self, target, time):
        self.expected_targets.append((target, time))


class Training(object):
    def __init__(self):
        self.eeg = EEG()

    def collect_packet(self, packet):
        self.eeg.add_packet(packet)

    def collect_expected_target(self, expected_target, message_counter):
        self.eeg.new_target(message_counter, expected_target)

    def save_eeg(self):
        self.eeg.askSaveFile()

    def load_eeg(self):
        self.eeg.askLoadFile()
