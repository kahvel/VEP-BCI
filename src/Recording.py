import Switchable
import ListByTrials
import constants as c

import csv


class RecordingListByTrials(Switchable.Switchable, ListByTrials.ListByTrials):
    def __init__(self):
        Switchable.Switchable.__init__(self)
        ListByTrials.ListByTrials.__init__(self)

    def trialEnded(self, *args):
        if self.enabled:
            ListByTrials.ListByTrials.trialEnded(self, *args)

    def start(self, *args):
        if self.enabled:
            ListByTrials.ListByTrials.start(self, *args)

    def save(self, file_name):

        open(self.changeFileName(file_name), "w").write(str(self.list))

    def load(self, file_name):
        self.list = eval(open(self.changeFileName(file_name)))

    def changeFileName(self, file_name):
        raise NotImplementedError("changeFileName not implemented!")

    def getTrialCollection(self, target_freqs):
        return []

    def add(self, data):
        if self.enabled:
            self.current_data.append(data)


class EEG(RecordingListByTrials):
    def __init__(self):
        RecordingListByTrials.__init__(self)

    def save(self, file_name):
        with open(self.changeFileName(file_name), "w") as csv_file:
            writer = csv.DictWriter(csv_file, c.SENSORS)
            writer.writeheader()
            writer.writerows(self.list)

    def changeFileName(self, file_name):
        return file_name[:-4] + "_eeg"


class ExpectedTargets(RecordingListByTrials):
    def __init__(self):
        RecordingListByTrials.__init__(self)

    def save(self, file_name):
        with open(self.changeFileName(file_name), "w") as csv_file:
            writer = csv.DictWriter(csv_file, c.SENSORS)
            writer.writeheader()
            writer.writerows(self.list)

    def changeFileName(self, file_name):
        return file_name[:-4] + "_targets"


class Frequencies(RecordingListByTrials):
    def __init__(self):
        RecordingListByTrials.__init__(self)

    def changeFileName(self, file_name):
        return file_name[:-4] + "_frequencies"


class Recording(object):
    def __init__(self):
        self.normal_eeg = EEG()
        self.expected_targets = ExpectedTargets()
        self.target_frequencies = Frequencies()

    def start(self, target_freqs):
        self.normal_eeg.start()
        self.expected_targets.start()
        self.target_frequencies.start(target_freqs)

    def reset(self):
        self.normal_eeg.reset()
        self.expected_targets.reset()

    def disableRecording(self):
        self.normal_eeg.disable()
        self.expected_targets.disable()

    def enableNormal(self):
        self.normal_eeg.enable()
        self.expected_targets.enable()

    def enableNeutral(self):
        self.normal_eeg.disable()
        self.expected_targets.disable()

    def trialEnded(self):
        self.normal_eeg.trialEnded()
        self.expected_targets.trialEnded()

    def collectPacket(self, packet, expected_target):
        self.normal_eeg.add(packet)
        self.expected_targets.add(expected_target)

    def saveEeg(self, file_name):
        self.normal_eeg.save(file_name)
        self.expected_targets.save(file_name)

    def loadEeg(self, file_name):
        self.normal_eeg.load(file_name)
        self.expected_targets.load(file_name)
