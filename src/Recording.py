import Switchable
import ListByTrials


class RecordingListByTrials(Switchable.Switchable, ListByTrials.ListByTrials):
    def __init__(self):
        Switchable.Switchable.__init__(self)
        ListByTrials.ListByTrials.__init__(self)

    def trialEnded(self, *args):
        if self.enabled:
            ListByTrials.ListByTrials.trialEnded(*args)

    def start(self, *args):
        if self.enabled:
            ListByTrials.ListByTrials.start(*args)

    def save(self):
        return str(self.list)

    def load(self, file_content):
        self.list = eval(file_content)


class EEG(RecordingListByTrials):
    def __init__(self):
        RecordingListByTrials.__init__(self)

    def getTrialCollection(self, target_freqs):
        return {
            "target_freqs": target_freqs,
            "packets": []
        }

    def add(self, packet):
        if self.enabled:
            self.current_data["target_freqs"].append(packet)


class ExpectedTargets(RecordingListByTrials):
    def __init__(self):
        RecordingListByTrials.__init__(self)

    def getTrialCollection(self, *args):
        return []

    def add(self, target, time):
        if self.enabled:
            self.current_data.append((target, time))


class Recording(object):
    def __init__(self):
        self.normal_eeg = EEG()
        self.neutral_eeg = EEG()
        self.expected_targets = ExpectedTargets()

    def start(self, target_freqs):
        self.normal_eeg.start(target_freqs)
        self.neutral_eeg.start(target_freqs)
        self.expected_targets.start()

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

    def trialEnded(self):
        self.normal_eeg.trialEnded()
        self.expected_targets.trialEnded()
        self.neutral_eeg.trialEnded()

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
