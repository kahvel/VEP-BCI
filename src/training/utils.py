import constants as c


def readFeatures(features_file_name, eeg_file_name, trial_number):
    """
    Old feature reading function. Bad because has to read EEG file and hard to get indices right between features and
    expected targets.
    :param features_file_name:
    :param eeg_file_name:
    :param trial_number:
    :return:
    """
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


def readFeaturesWithTargets(features_file_name, frequencies_file_name):
    """
    New features file reader. Avoids reading EEG files. Instead gets expected targets from features file and
    frequencies from separate file.
    :param features_file_name:
    :param frequencies_file_name:
    :return:
    """
    file_content = open(features_file_name).readlines()
    # frequencies = dict(enumerate(sorted(map(lambda x: x[0], eval(file_content[0])[1][('Sum PSDA', ('P7', 'O1', 'O2', 'P8'))][1]))))
    features_list = []
    expected_targets = []
    for result in file_content:
        features, expected_target = eval(result)
        features_list.append(features)
        expected_targets.append(expected_target)
    frequencies = eval(open(frequencies_file_name).read())
    print frequencies
    print expected_targets
    print len(features_list)
    print
    return features_list, expected_targets, frequencies


def newFeaturesIterator(features_list, expected_targets, number_of_steps_to_skip):
    previous_expected_target = None
    skip_counter = 0
    skipping = False
    for features, expected_target in zip(features_list, expected_targets):
        if previous_expected_target is not None:
            if expected_target != previous_expected_target:
                skipping = True
                skip_counter = 0
        if skipping:
            skip_counter += 1
            if skip_counter > number_of_steps_to_skip:
                skipping = False
        if not skipping:
            yield features, expected_target
        previous_expected_target = expected_target


def removeResultsAfterChange(features_list, expected_targets, number_of_steps_to_skip):
    new_features = []
    new_expected_targets = []
    for features, expected_target in newFeaturesIterator(features_list, expected_targets, number_of_steps_to_skip):
        new_features.append(features)
        new_expected_targets.append(expected_target)
    return new_features, new_expected_targets


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
