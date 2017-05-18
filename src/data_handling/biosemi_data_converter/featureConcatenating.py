
import csv
import numpy as np
# from bci import Recording
#
# target_freqs = {1: 8.0, 2: 14.0, 3:28.0}
# recording_handler = Recording.Recording(target_freqs)

def toFloat(string):
    # return float(string)
    if string != "":  # For converted data
        return float(string)
    else:
        return None

def getRows(list_of_dicts, function):
    rows = []
    for dict in list_of_dicts:
        rows.append({key: function(dict[key]) for key in dict})
    return rows

def getRowsAsFloats(list_of_dicts):
    return getRows(list_of_dicts, toFloat)

def defaultGetRows(list_of_dicts):
    return getRowsAsFloats(list_of_dicts)

def getDataFileHeader(data):
    return sorted(data[0].keys()) if len(data) > 0 else []



path1 = "C:\\Users\\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\src\\data_handling\\biosemi_data_converter\\features_only\\wrong\\sub1_wrong_freqs\\rec1\\features.csv"
path2 = "C:\\Users\\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\src\\data_handling\\biosemi_data_converter\\features_only\\wrong\\sub1_wrong_freqs\\rec2\\features.csv"

file1 = open(path1)
file2 = open(path2)

rows1 = defaultGetRows(csv.DictReader(file1))
rows2 = defaultGetRows(csv.DictReader(file2))

result_file_name = "features.csv"
header1 = getDataFileHeader(rows1)
header2 = getDataFileHeader(rows2)

header = sorted(list(header1) + list(header2))

data = []
for row1, row2 in zip(rows1, rows2):
    result_row = {}
    for feature in header:
        if feature in row1:
            result_row[feature] = row1[feature]
        else:
            result_row[feature] = row2[feature]
    data.append(result_row)

with open(result_file_name, "w") as csv_file:
    writer = csv.DictWriter(csv_file, header)
    writer.writeheader()
    writer.writerows(data)
