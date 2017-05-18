import numpy as np
from training.itr_calculators import ItrCalculatorProb


table = """[[ 333.    0.   18.  174.]
 [  10.  313.   26.  176.]
 [   0.    0.  240.  285.]
 [   0.    0.    0.    0.]]

""".strip()


parsed_table = np.array(map(lambda x: map(lambda y: int(y.strip()), x.strip().split(".")), table.replace("[", "").replace("]","").strip(".").split(".\n")), dtype=np.float)

# parsed_table = np.array([[51,0,0,49],[0,48,0,52],[0,0,1,99],[0,0,0,0]], dtype=np.float)
# parsed_table = np.array([[21,0,1,78],[0,22,2,76],[0,0,10,90],[0,0,0,0]], dtype=np.float)

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

def calculatePredictionProbability(confusion_matrix):
    if not isinstance(confusion_matrix, float):
        matrix_sum = confusion_matrix.sum()
        return (matrix_sum-confusion_matrix.sum(axis=0)[-1])/matrix_sum

def calculateAccuracy(confusion_matrix):
    if not isinstance(confusion_matrix, float):
        return np.trace(confusion_matrix)/confusion_matrix.sum()

def calculateAccuracyIgnoringLastColumn(confusion_matrix):
    if not isinstance(confusion_matrix, float):
            return np.trace(confusion_matrix)/(confusion_matrix.sum()-confusion_matrix.sum(axis=0)[-1])


calculator = ItrCalculatorProb.ItrCalculatorProb(
    window_length = 2,
    step = 0.125,
    look_back_length = 1,
    feature_maf_length = 1,
    proba_maf_length = 1,
    n_targets = 3
)
calculator.n_classes = 3


def printConfusionMatrixData(confusion_matrix):
    calculator.class_probas = (confusion_matrix.sum(1)/confusion_matrix.sum())[:-1]
    accuracy = calculateAccuracyIgnoringLastColumn(confusion_matrix)
    prediction_probability = calculatePredictionProbability(confusion_matrix)
    # print "Mutual information ITR:"
    print calculator.itrMiFromMatrix(confusion_matrix)
    # print "Standard ITR:"
    print calculator.itrBitPerMin(accuracy, prediction_probability)
    # print "Accuracy:"
    print accuracy
    # print "MDT:"
    print calculator.mdt(prediction_probability)
    # print "Predictions:"
    print ((confusion_matrix.sum()-confusion_matrix.sum(axis=0)[-1])), (confusion_matrix.sum())
    print confusion_matrix

printConfusionMatrixData(parsed_table)


row = """649.0/1695.0	616.0/1695.0	445.0/1695.0	1.0/1695.0

"""
row = row.strip()
split = row.split()
new_row = map(lambda x: "$\\frac{" + x.split("/")[0][:-2] + "}{" + x.split("/")[1][:-2] + "}$", split)
print "\t".join(new_row)