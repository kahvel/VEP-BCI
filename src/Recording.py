from parsers import FeaturesParser
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

    def writeCsv(self, file_name, header, data):
        with open(file_name, "w") as csv_file:
            writer = csv.DictWriter(csv_file, header)
            writer.writeheader()
            writer.writerows(data)

    def getDataFilePath(self, directory):
        raise NotImplementedError("getDataFilePath not implemented!")

    def getLabelsFilePath(self, directory):
        raise NotImplementedError("getLabelsFilePath not implemented!")

    def getDataForSaving(self):
        raise NotImplementedError("getDataForSaving not implemented!")

    def getLabelsForSaving(self):
        combined_data = []
        for expected, packet, predicted in zip(self.expected_targets, self.packet_number, self.predicted_targets):
            combined_data.append({
                c.CSV_TRUE_LABEL: expected,
                c.CSV_PREDICTED_LABEL: predicted,
                c.CSV_PACKET_NUMBER: packet,
            })
        return combined_data

    def toInt(self, string):
        if string != "":
            return int(string)
        else:
            return None

    def toFloat(self, string):
        return float(string)

    def getColumns(self, list_of_dicts, function):
        columns = {}
        for dict in list_of_dicts:
            for key in dict:
                if key in columns:
                    columns[key].append(function(dict[key]))
                else:
                    columns[key] = [function(dict[key])]
        return columns

    def getColumnsAsIntegers(self, list_of_dicts):
        return self.getColumns(list_of_dicts, self.toInt)

    def getColumnsAsFloats(self, list_of_dicts):
        return self.getColumns(list_of_dicts, self.toFloat)

    def getRows(self, list_of_dicts, function):
        rows = []
        for dict in list_of_dicts:
            rows.append({key: function(dict[key]) for key in dict})
        return rows

    def getRowsAsIntegers(self, list_of_dicts):
        return self.getRows(list_of_dicts, self.toInt)

    def getRowsAsFloats(self, list_of_dicts):
        return self.getRows(list_of_dicts, self.toFloat)

    def defaultGetRows(self, list_of_dicts):
        raise NotImplementedError("defaultGetRows not implemented!")

    def getDataFileHeader(self):
        raise NotImplementedError("getDataFileHeader not implemented!")

    def save(self, directory):
        self.writeCsv(self.getDataFilePath(directory), self.getDataFileHeader(), self.getDataForSaving())
        self.writeCsv(self.getLabelsFilePath(directory), c.CSV_LABEL_FILE_HEADER, self.getLabelsForSaving())

    def loadData(self, directory):
        with open(self.getDataFilePath(directory), "r") as csv_file:
            self.data = self.defaultGetRows(csv.DictReader(csv_file))

    def loadLabels(self, directory):
        with open(self.getLabelsFilePath(directory), "r") as csv_file:
            columns = self.getColumnsAsIntegers(csv.DictReader(csv_file))
            self.expected_targets = columns[c.CSV_TRUE_LABEL]
            self.predicted_targets = columns[c.CSV_PREDICTED_LABEL]
            self.packet_number = columns[c.CSV_PACKET_NUMBER]

    def load(self, directory):
        self.loadData(directory)
        self.loadLabels(directory)


class Eeg(DataAndExpectedTargets):
    def __init__(self):
        DataAndExpectedTargets.__init__(self)

    def getDataFilePath(self, directory):
        return os.path.join(directory, "eeg.csv")

    def getLabelsFilePath(self, directory):
        return os.path.join(directory, "eeg_labels.csv")

    def getDataFileHeader(self):
        return c.SENSORS

    def getDataForSaving(self):
        return self.data

    def defaultGetRows(self, list_of_dicts):
        return self.getRowsAsIntegers(list_of_dicts)


class Features(DataAndExpectedTargets):
    def __init__(self):
        DataAndExpectedTargets.__init__(self)

    def getDataFilePath(self, directory):
        return os.path.join(directory, "features.csv")

    def getLabelsFilePath(self, directory):
        return os.path.join(directory, "features_labels.csv")

    def getDataForSaving(self):
        return self.data

    def getDataFileHeader(self):
        return sorted(self.data[0].keys()) if len(self.data) > 0 else []

    def defaultGetRows(self, list_of_dicts):
        return self.getRowsAsFloats(list_of_dicts)

    def iterateColumns(self, extraction_method_names):
        columns = self.getColumnsAsFloats(self.data)
        for key in sorted(columns):
            method = FeaturesParser.getMethodFromFeature(key)
            if method in extraction_method_names:
                yield method, columns[key]

    # def getRows(self, list_of_dicts):
    #     rows = []
    #     for dict in list_of_dicts:
    #         rows.append([self.toFloat(dict[key]) for key in sorted(dict)])
    #     return rows


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
        self.features.disable()

    def enableNormal(self):
        self.normal_eeg.enable()
        self.features.enable()

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
