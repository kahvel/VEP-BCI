

class EEG(object):
    def __init__(self):
        self.packets = []
        self.expected_targets = []

    def save(self):
        return str(self.packets) + ";" + str(self.expected_targets)

    def load(self, file_content):
        split_content = file_content.split(";")
        self.packets = eval(split_content[0])
        self.expected_targets = eval(split_content[1])

    def add_packet(self, packet):
        self.packets.append(packet)

    def new_target(self, target, time):
        self.expected_targets.append((target, time))


class Training(object):
    def __init__(self):
        self.eeg = EEG()
        self.enabled = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def collect_packet(self, packet):
        if self.enabled:
            self.eeg.add_packet(packet)

    def collect_expected_target(self, expected_target, message_counter):
        if self.enabled:
            self.eeg.new_target(message_counter, expected_target)

    def save_eeg(self):
        return self.eeg.save()

    def load_eeg(self, file_content):
        self.eeg.load(file_content)
