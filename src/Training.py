import Switchable


class EEG(Switchable.Switchable):
    def __init__(self):
        Switchable.Switchable.__init__(self)
        self.signal = []

    def addPacket(self, packet):
        self.signal.append(packet)

    def save(self):
        return str(self.signal)

    def load(self, file_content):
        self.signal = eval(file_content)


class NormalEEG(EEG):
    def __init__(self):
        EEG.__init__(self)
        self.expected_targets = []

    def new_target(self, target, time):
        self.expected_targets.append((target, time))

    def save(self):
        return EEG.save(self) + ";" + str(self.expected_targets)

    def load(self, file_content):
        split_content = file_content.split(";")
        EEG.load(self, split_content[0])
        self.expected_targets = eval(self.expected_targets)


class NeutralEEG(EEG):
    def __init__(self):
        EEG.__init__(self)


class Training(object):
    def __init__(self):
        self.normal_eeg = NormalEEG()
        self.neutral_eeg = NeutralEEG()

    def collect_packet(self, packet):
        if self.normal_eeg.enabled:
            self.normal_eeg.addPacket(packet)
        if self.neutral_eeg.enabled:
            self.neutral_eeg.addPacket(packet)

    def collect_expected_target(self, expected_target, message_counter):
        if self.normal_eeg.enabled:
            self.normal_eeg.new_target(message_counter, expected_target)

    def save_eeg(self):
        return self.normal_eeg.save() + ";;" + self.neutral_eeg.save()

    def load_eeg(self, file_content):
        split_content = file_content.split(";;")
        self.normal_eeg.load(split_content[0])
        self.neutral_eeg.load(split_content[1])
