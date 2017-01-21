import numpy as np
import matplotlib.pyplot as plt
import csv


def getReferenceSignals(length, frequencies, all_harmonics, sampling_freq):
    """
    Returns reference signals grouped per target. Each target has number of harmonics times two reference signals,
    that is sine and cosine for each harmonic.
    :param length:
    :param frequencies:
    :return:
    """
    reference_signals = []
    t = np.arange(0, length, step=1.0)/sampling_freq
    for freq, harmonics in zip(frequencies, all_harmonics):
        reference_signals.append([])
        for harmonic in harmonics:
            reference_signals[-1].append(map(lambda x: int(x*10000), np.sin(np.pi*2*harmonic*freq*t)))
            reference_signals[-1].append(map(lambda x: int(x*10000), np.cos(np.pi*2*harmonic*freq*t)))
    return reference_signals


length = 512
frequencies = [60.0/9, 60.0/8, 60.0/7]
all_harmonics = [[1, 2, 3], [1, 2, 3], [1, 2, 3]]
sampling_freq = 128.0


reference_signals = getReferenceSignals(length, frequencies, all_harmonics, sampling_freq)

time = np.arange(0, length, step=1.0)
# for signals in reference_signals:
#     plt.figure()
#     for i, signal in enumerate(signals):
#         plt.subplot(len(signals), 1, i+1)
#         plt.plot(time, signal)
# plt.show()

# bins = np.fft.rfftfreq(length)[1:]*sampling_freq
# for signals in reference_signals:
#     plt.figure()
#     for i, signal in enumerate(signals):
#         psd = (np.abs(np.fft.rfft(signal))**2)[1:]
#         plt.subplot(len(signals), 1, i+1)
#         plt.plot(bins, psd)
# plt.show()

header = ("O1", "O2", "P7", "P8", "T7", "T8")
reference_signals_dict = map(lambda x: {"O1": x[0], "O2": x[1], "P7": x[2], "P8": x[3], "T7": x[4], "T8": x[5]}, np.transpose(np.column_stack(reference_signals)))


def writeCsv(file_name, header, data):
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header)
        writer.writeheader()
        writer.writerows(data)

writeCsv("eeg.csv", header, reference_signals_dict)
label_file_header = ("Packet", "True", "Predicted")
packet_numbers = list(range(1, len(reference_signals_dict)+1))
expected_targets = [1]*length+[2]*length+[3]*length
predicted_targets = [None]*len(reference_signals_dict)
label_file_content = map(lambda x: {"Packet": x[0], "True": x[1], "Predicted": x[2]}, zip(packet_numbers, expected_targets, predicted_targets))
writeCsv("eeg_labels.csv", label_file_header, label_file_content)
