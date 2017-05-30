# -*- coding: utf-8 -*-
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib2tikz


def toFloat(string):
    if string != "":
        return float(string)
    else:
        return None


def getRows(list_of_dicts, function):
    rows = []
    for dict in list_of_dicts:
        rows.append({key: function(dict[key]) for key in ["O2"]})
    return rows


n_sensors = 128


def loadData(file_name):
    with open(file_name, "rU") as csv_file:
        return getRows(csv.DictReader(csv_file), toFloat)

file_name = "C:\\Users\\Anti\\Desktop\\eeg.csv"
data = map(lambda x: x["O2"], loadData(file_name))[:1000]

plt.plot(np.arange(0, len(data)), data)
matplotlib2tikz.save("eeg.tex")
plt.show()