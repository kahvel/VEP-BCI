import Switchable
import constants as c

import csv
import os


class DataAndExpectedTargets(Switchable.Switchable):
    def __init__(self):
        Switchable.Switchable.__init__(self)
        self.data = []
        self.expected_targets = []
        self.packet_number = []
        self.predicted_targets = []

    def add(self, data, expected_target, packet_number):
        if self.enabled:
            self.data.append(data)
            self.expected_targets.append(expected_target)
            self.packet_number.append(packet_number)

    def addPrediction(self, predicted_target):
        if self.enabled:
            self.predicted_targets.append(predicted_target)

    def getLength(self):
        return len(self.data)

    def combineData(self):
        combined_data = []
        for expected, packet, predicted in zip(self.expected_targets, self.packet_number, self.predicted_targets):
            combined_data.append({
                c.CSV_TRUE_LABEL: expected,
                c.CSV_PREDICTED_LABEL: predicted,
                c.CSV_PACKET_NUMBER: packet,
            })
        return combined_data

    def writeCsv(self, file_name, header, data):
        with open(file_name, "w") as csv_file:
            writer = csv.DictWriter(csv_file, header)
            writer.writeheader()
            writer.writerows(data)


class Eeg(DataAndExpectedTargets):
    def __init__(self):
        DataAndExpectedTargets.__init__(self)

    def getEegFilePath(self, directory):
        return os.path.join(directory, "eeg.csv")

    def getLabelsFilePath(self, directory):
        return os.path.join(directory, "eeg_labels.csv")

    def save(self, directory):
        self.writeCsv(self.getEegFilePath(directory), c.SENSORS, self.data)
        self.writeCsv(self.getLabelsFilePath(directory), c.CSV_LABEL_FILE_HEADER, self.combineData())

    def toInt(self, string):
        if string != "":
            return int(string)
        else:
            return None

    def getColumns(self, list_of_dicts):
        columns = {}
        for dict in list_of_dicts:
            for key in dict:
                if key in columns:
                    columns[key].append(self.toInt(dict[key]))
                else:
                    columns[key] = [self.toInt(dict[key])]
        return columns

    def getRows(self, list_of_dicts):
        rows = []
        for dict in list_of_dicts:
            rows.append({key: self.toInt(dict[key]) for key in dict})
        return rows

    def load(self, directory):
        with open(self.getEegFilePath(directory), "r") as csv_file:
            self.data = self.getRows(list(csv.DictReader(csv_file, c.SENSORS))[1:])
            print self.data
        with open(self.getLabelsFilePath(directory), "r") as csv_file:
            columns = self.getColumns(list(csv.DictReader(csv_file, c.CSV_LABEL_FILE_HEADER))[1:])
            self.expected_targets = columns[c.CSV_TRUE_LABEL]
            self.predicted_targets = columns[c.CSV_PREDICTED_LABEL]
            self.packet_number = columns[c.CSV_PACKET_NUMBER]


class Features(DataAndExpectedTargets):
    def __init__(self):
        DataAndExpectedTargets.__init__(self)

    def flattenData(self):
        for features in self.data:
            for tab in sorted(features.keys()):
                for



class Recording(object):
    def __init__(self, target_freqs, record_option):
        self.normal_eeg = Eeg()
        self.features = Features()
        self.target_frequencies = target_freqs
        self.setRecordingState(record_option)

    def setRecordingState(self, record_option):
        if record_option == c.TRAINING_RECORD_NORMAL:
            self.enableNormal()
        elif record_option == c.TRAINING_RECORD_NEUTRAL:
            self.enableNeutral()
        elif record_option == c.TRAINING_RECORD_DISABLED:
            self.disableRecording()
        else:
            raise Exception("Recording option menu in invalid state!")

    def disableRecording(self):
        self.normal_eeg.disable()

    def enableNormal(self):
        self.normal_eeg.enable()

    def enableNeutral(self):
        """
        Currently not implemented
        :return:
        """
        self.normal_eeg.disable()

    def collectPacket(self, packet, expected_target, packet_number):
        self.normal_eeg.add(packet, expected_target, packet_number)

    def collectFeatures(self, features, expected_target, packet_number):
        self.features.add(features, expected_target, packet_number)

    def getEeg(self):
        return self.normal_eeg

    def getFeatures(self):
        return self.features

    def getFrequencies(self):
        return self.target_frequencies

    def addPredictionToEeg(self, predicted_target):
        self.normal_eeg.addPrediction(predicted_target)

    def addPredictionToFeatures(self, predicted_target):
        self.features.addPrediction(predicted_target)
