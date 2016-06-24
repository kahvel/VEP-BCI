import constants as c


def readFeatures(features_file_name, eeg_file_name, trial_number):
    file_content = open(features_file_name).readlines()
    # frequencies = dict(enumerate(sorted(map(lambda x: x[0], eval(file_content[0])[1][('Sum PSDA', ('P7', 'O1', 'O2', 'P8'))][1]))))
    features_list = []
    for result in file_content:
        features_list.append(eval(result))

    file_content = open(eeg_file_name).read().split(";")
    frequencies = eval(file_content[0])[trial_number-1][c.EEG_RECORDING_FREQS]
    expected = eval(file_content[2])[trial_number-1]

    print frequencies
    print expected
    print len(features_list)
    # print len(eval(file_content[0])[trial_number-1]["Packets"])
    print

    return features_list, expected, frequencies


def featuresIterator(features_list, expected_targets, length, step, skip_after_change=False):
    expected_index = 1
    expected_target = expected_targets[0][0]
    packet_at_change = 0
    for i, result in enumerate(features_list):
        if i == 0:
            packet_nr = length
        else:
            packet_nr = length + step * i

        if expected_index < len(expected_targets) and packet_nr >= expected_targets[expected_index][1]:
            expected_target = expected_targets[expected_index][0]
            expected_index += 1
            packet_at_change = packet_nr
        if not skip_after_change:
            # print i, packet_nr, expected_target
            yield result, expected_target
        else:
            if packet_nr - packet_at_change >= length:
                # print i, packet_nr, expected_target
                yield result, expected_target
