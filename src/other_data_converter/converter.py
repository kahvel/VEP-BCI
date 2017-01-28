
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
        rows.append({key: function(dict[key]) for key in dict})
    return rows

# 1
# 8 - 6330
# 14 - 6343
# 28 - 6370
# 2
# 8 - 6361
# 14 - 6361
# 28 - 6379

length = 6379

def loadData(file_name):
    with open(file_name, "rU") as csv_file:
        return getRows(csv.DictReader(csv_file, fieldnames=list(range(length))), toFloat)


data = loadData("28sub1trial2.csv")

indices = [14, 27]
new_data = [{} for _ in range(len(data[0]))]
for i, dict in enumerate(data):
    if i in indices:
        for j in sorted(dict):
            new_data[j][i] = dict[j]

# print data
# print new_data


def writeCsv(file_name, header, data):
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header)
        writer.writeheader()
        writer.writerows(data)


header = [14, 27]

# writeCsv("rec6.csv", header, new_data)

label_file_header = ("Packet", "True", "Predicted")
packet_numbers = list(range(1, length+1))
expected_targets = [3]*length
predicted_targets = [None]*length
label_file_content = map(lambda x: {"Packet": x[0], "True": x[1], "Predicted": x[2]}, zip(packet_numbers, expected_targets, predicted_targets))
writeCsv("eeg_labels.csv", label_file_header, label_file_content)