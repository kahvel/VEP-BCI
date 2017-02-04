import csv


def toFloat(string):
    return float(string)


def loadData(file_name, header):
    with open(file_name, "rU") as csv_file:
        return getRowsAsFloats(csv.DictReader(csv_file), header)


def getRows(list_of_dicts, function, header):
    rows = []
    for dict in list_of_dicts:
        rows.append({key: function(dict[key]) for key in header})
    return rows


def getRowsAsFloats(list_of_dicts, header):
    return getRows(list_of_dicts, toFloat, header)


read_header = ("AF3", "F7", "F3", "FC5","T7", "P7", "O1", "O2", "P8", "T8", "FC6","F4", "F8", "AF4", "CLASS")
header = ("AF3", "F7", "F3", "FC5","T7", "P7", "O1", "O2", "P8", "T8", "FC6","F4", "F8", "AF4")
file_name = "2016-08-04--00-03_mike_ssvep_second.csv"
data = loadData(file_name, read_header)


def writeCsv(file_name, header, data):
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header)
        writer.writeheader()
        writer.writerows(data)

expected_targets = map(lambda x: int(x["CLASS"]), data)
new_data = []
for row in data:
    row.pop("CLASS")
writeCsv("test1.csv", header, data)
packet_count = len(data)
label_file_header = ("Packet", "True", "Predicted")
predicted_targets = [None]*packet_count
packet_numbers = list(range(1, packet_count+1))

label_file_content = map(lambda x: {"Packet": x[0], "True": x[1], "Predicted": x[2]}, zip(packet_numbers, expected_targets, predicted_targets))
writeCsv("test1_labels.csv", label_file_header, label_file_content)
