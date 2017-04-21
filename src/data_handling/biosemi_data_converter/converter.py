
import csv
import numpy as np


def toFloat(string):
    if string != "":
        return float(string)
    else:
        return None


def getRows(list_of_dicts, function):
    rows = []
    for dict in list_of_dicts:
        rows.append({key: function(dict[key]) for key in ["O1", "O2"]})
    return rows


n_sensors = 128
fieldnames = list(range(n_sensors))
fieldnames[14] = "O1"
fieldnames[27] = "O2"


def loadData(file_name):
    with open(file_name, "rU") as csv_file:
        return getRows(csv.DictReader(csv_file, fieldnames=fieldnames), toFloat)


def writeCsv(file_name, header, data):
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header)
        writer.writeheader()
        writer.writerows(data)


def getFileContents(file_name, target):
    data = loadData(file_name)[1280:5120]
    length = len(data)
    packet_numbers = list(range(1, length+1))
    expected_targets = [target]*length
    predicted_targets = [None]*length
    label_file_content = map(lambda x: {"Packet": x[0], "True": x[1], "Predicted": x[2]}, zip(packet_numbers, expected_targets, predicted_targets))
    return data, label_file_content

file_name = "sub4trial5t.csv"
frequencies = ["8", "14", "28"]
data = {}
label_file_content = {}
all_data = []
all_label_file_content = []
for i, frequency in enumerate(frequencies):
    data[frequency], label_file_content[frequency] = getFileContents("./" + frequency + "/sub4/" + frequency + file_name, i+1)
    all_data.extend(data[frequency])
    all_label_file_content.extend(label_file_content[frequency])

header = ["O1", "O2"]
label_file_header = ("Packet", "True", "Predicted")
writeCsv("eeg.csv", header, all_data)
writeCsv("eeg_labels.csv", label_file_header, all_label_file_content)