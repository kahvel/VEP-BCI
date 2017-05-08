import numpy as np


table = """[[ 51.    0.    18.  496.]
 [   10.  27.    20.  508.]
 [   1.    9.   40.  .]
 [   0.    0.    0.    0.]]
""".strip()


parsed_table = np.array(map(lambda x: map(lambda y: int(y.strip()), x.strip().split(".")), table.replace("[", "").replace("]","").strip(".").split(".\n")), dtype=np.float)

def getItrBitPerMin(P, recall):
    window_length = 1
    step = 0.125
    look_back_length = 1
    feature_maf = 1
    proba_maf = 1
    mean_detection_time = window_length + (look_back_length + feature_maf + proba_maf + 1.0/recall - 4)*step
    N = 3
    if mean_detection_time != 0:
        return getItrBitPerTrial(P, N)*60.0/mean_detection_time
    else:
        return np.nan

def getItrOffline(accuracy, mdt, N):
    return getItrBitPerTrial(accuracy, N)*60.0/mdt

def getItrBitPerTrial(P, N):
    """
    :param P: Accuracy
    :param N: Target count
    :return:
    """
    if N == 1:
        return np.nan
    elif P == 1:
        return np.log10(N)/np.log10(2)
    elif P == 0:
        return np.nan
    else:
        return (np.log10(N)+P*np.log10(P)+(1-P)*np.log10((1-P)/(N-1)))/np.log10(2)

def calculateRecall(confusion_matrix):
    if not isinstance(confusion_matrix, float):
        matrix_sum = confusion_matrix.sum()
        return (sumWithoutLastColumn(confusion_matrix))/matrix_sum

def sumWithoutLastColumn(confusion_matrix):
    if not isinstance(confusion_matrix, float):
        matrix_sum = confusion_matrix.sum()
        return matrix_sum-confusion_matrix.sum(axis=0)[-1]

def calculateAccuracy(confusion_matrix):
    if not isinstance(confusion_matrix, float):
        return np.trace(confusion_matrix)/confusion_matrix.sum()

def calculateAccuracyIgnoringLastColumn(confusion_matrix):
    if not isinstance(confusion_matrix, float):
        return np.trace(confusion_matrix)/(confusion_matrix.sum()-confusion_matrix.sum(axis=0)[-1])

def printConfusionMatrixData(confusion_matrix):
    accuracy = calculateAccuracyIgnoringLastColumn(confusion_matrix)
    recall = calculateRecall(confusion_matrix)
    print getItrBitPerMin(accuracy, recall)
    print accuracy
    print confusion_matrix
    print getItrOffline(accuracy, 225.0/sumWithoutLastColumn(confusion_matrix), 3)

printConfusionMatrixData(parsed_table)