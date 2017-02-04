import csv
import os


def writeCsv(file_name, header, data):
    with open(file_name, "w") as csv_file:
        writer = csv.DictWriter(csv_file, header)
        writer.writeheader()
        writer.writerows(data)


file_name = "test4.txt"

f = open(file_name, mode="r")
content = f.read().split(";")
f.close()

targets_and_packets = eval(content[0])
empty_list = eval(content[1])
expected_targets = eval(content[2])

header = ("AF3", "F7", "F3", "FC5","T7", "P7", "O1", "O2", "P8", "T8", "FC6","F4", "F8", "AF4")
first_target_freqs = None
for i, (dictionary, expected) in enumerate(zip(targets_and_packets, expected_targets)):
    directory_name = "rec" + str(i+1)
    os.makedirs(directory_name)
    target_freqs = dictionary['TargetFreqs']
    packets = dictionary["Packets"]
    if first_target_freqs is not None:
        if target_freqs != first_target_freqs:
            print "target frequencies different!", target_freqs, first_target_freqs
    else:
        first_target_freqs = target_freqs

    packet_count = len(packets)
    writeCsv(os.path.join(directory_name, "eeg.csv"), header, packets)
    label_file_header = ("Packet", "True", "Predicted")
    packet_numbers = list(range(1, packet_count+1))

    expected_targets123 = []
    previous_target, previous_packet_number = expected[0]
    for target, packet_number in expected[1:]:
        expected_targets123.extend([previous_target]*(packet_number-previous_packet_number))
        previous_target = target
        previous_packet_number = packet_number
    expected_targets123.extend([previous_target]*(packet_count-previous_packet_number))

    predicted_targets = [None]*packet_count
    label_file_content = map(lambda x: {"Packet": x[0], "True": x[1], "Predicted": x[2]}, zip(packet_numbers, expected_targets123, predicted_targets))
    writeCsv(os.path.join(directory_name, "eeg_labels.csv"), label_file_header, label_file_content)
