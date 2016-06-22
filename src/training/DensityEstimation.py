from utils import readFeatures


features_list, expected, frequencies = readFeatures(
    "../save/eeg_new_detrend2.txt",
    "C:\\Users\\Anti\\Desktop\\PycharmProjects\\MAProject\\src\\eeg\\eeg_new.txt",
    1
)


length = 256
step = 32
packet_nr = 0
target = expected[0][0]
expected_index = 1

density = {}

for extracted_features in features_list:
    for tab in extracted_features:
        for method in extracted_features[tab]:
            for harmonic in extracted_features[tab][method]:
                pass