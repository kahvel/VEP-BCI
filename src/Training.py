import Switchable
import ListByTrials


class EEG(Switchable.Switchable, ListByTrials.ListByTrials):
    def __init__(self):
        Switchable.Switchable.__init__(self)
        ListByTrials.ListByTrials.__init__(self)

    def getTrialCollection(self, *args):
        return []

    def add(self, packet):
        if self.enabled:
            self.list[-1].append(packet)

    def save(self):
        return str(self.list)

    def load(self, file_content):
        self.list = eval(file_content)


class ExpectedTargets(Switchable.Switchable, ListByTrials.ListByTrials):
    def __init__(self):
        Switchable.Switchable.__init__(self)
        ListByTrials.ListByTrials.__init__(self)

    def getTrialCollection(self, *args):
        return []

    def add(self, target, time):
        if self.enabled:
            self.list.append((target, time))

    def save(self):
        return str(self.list)

    def load(self, file_content):
        self.list = eval(file_content)


class Training(object):
    def __init__(self):
        self.normal_eeg = EEG()
        self.neutral_eeg = EEG()
        self.expected_targets = ExpectedTargets()

    def setup(self):
        self.normal_eeg.setup()
        self.neutral_eeg.setup()
        self.expected_targets.setup()

    def reset(self):
        self.normal_eeg.reset()
        self.neutral_eeg.reset()
        self.expected_targets.reset()

    def disableRecording(self):
        self.normal_eeg.disable()
        self.expected_targets.disable()
        self.neutral_eeg.disable()

    def enableNormal(self):
        self.normal_eeg.enable()
        self.expected_targets.enable()
        self.neutral_eeg.disable()

    def enableNeutral(self):
        self.normal_eeg.disable()
        self.expected_targets.disable()
        self.neutral_eeg.enable()

    def collectPacket(self, packet):
        self.normal_eeg.add(packet)
        self.neutral_eeg.add(packet)

    def collectExpectedTarget(self, expected_target, message_counter):
        self.expected_targets.add(expected_target, message_counter)

    def saveEeg(self):
        return self.normal_eeg.save() + ";" + self.neutral_eeg.save() + ";" + self.expected_targets.save()

    def loadEeg(self, file_content):
        split_content = file_content.split(";")
        self.normal_eeg.load(split_content[0])
        self.neutral_eeg.load(split_content[1])
        self.expected_targets.load(split_content[2])
