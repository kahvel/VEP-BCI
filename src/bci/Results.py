import numpy as np
import sklearn.metrics

import constants as c


class Result(object):
    def __init__(self, target_freqs):
        self.results = {current: {detected: 0 for detected in target_freqs.values()+[None]} for current in target_freqs.values()+[None]}
        self.true_labels = []
        self.predicted_labels = []
        self.target_count = len(target_freqs)
        self.total_packets = None
        self.frequency_to_label = {frequency: label for label, frequency in target_freqs.items()}
        self.frequency_to_label[None] = None
        self.target_frequencies = target_freqs.values()
        self.prev_result = None

    def isEqualToPreviousResult(self, result):
        return self.prev_result == result

    def add(self, current, detected):
        """
        Current is None if there is no computer-chosen target presented to user.
        Detected is None if no target was detected. Otherwise both are respective frequencies.
        :param current: The frequency of the current expected target.
        :param detected: The frequency of the detected target.
        :return:
        """
        self.results[current][detected] += 1
        self.true_labels.append(self.frequency_to_label[current])
        self.predicted_labels.append(self.frequency_to_label[detected])
        self.prev_result = detected

    def setTime(self, total_time):
        self.total_packets = total_time

    def getTimeInSec(self, time):
        return float(time)/c.HEADSET_FREQ

    def getTimePerTarget(self, total_results, total_time):
        if total_results == 0:
            return np.nan
        else:
            return float(total_time)/total_results

    def countMatrixElements(self):
        """
        Returns the number of true positives and false positives.
        If detected is None, then negative class was predicted.
        :return:
        """
        diagonal = 0
        off_diagonal = 0
        for correct in self.results:
            for detected in self.results[correct]:
                if detected is not None:
                    if correct == detected:
                        diagonal += self.results[correct][detected]
                    else:
                        off_diagonal += self.results[correct][detected]
        return diagonal, off_diagonal

    def getPrecision(self, true_positives, false_positives):
        if true_positives+false_positives == 0:
            return np.nan
        else:
            return float(true_positives)/(true_positives+false_positives)

    def getItrBitPerMin(self, itr, time):
        return itr*60.0/time

    def getItrBitPerTrial(self, P, N):
        """
        :param P: Accuracy
        :param N: Target count
        :return:
        """
        if N == 1:
            return np.nan
        elif P == 1:
            return self.log2(N)+P*self.log2(P)
        else:
            return self.log2(N)+P*self.log2(P)+(1-P)*self.log2((1-P)/(N-1))

    def log2(self, x):
        if x == 0:
            return np.nan
        else:
            return np.log10(x)/np.log10(2)

    def calculateF1(self, true_labels, predicted_labels, beta):
        """
        With beta = 1, same as sklearn.metrics.f1_score(true_labels, predicted_labels, average="binary")
        :param true_labels:
        :param predicted_labels:
        :param beta:
        :return:
        """
        precision = sklearn.metrics.precision_score(true_labels, predicted_labels)
        recall = sklearn.metrics.recall_score(true_labels, predicted_labels)
        denominator = (beta**2 * precision + recall)
        if denominator == 0:
            return 0
        else:
            return (1 + beta**2) * precision * recall / denominator

    def calculateWeightedMeanF1(self, scores):
        label_count = len(self.true_labels)
        if label_count == 0:
            return 0
        else:
            return sum(scores[frequency]*sum(
                np.array(self.true_labels) == self.frequency_to_label[frequency]
            ) for frequency in self.target_frequencies)/label_count

    def calculateMeanF1(self, scores, weighted):
        """
        With beta = 1 same as sklearn.metrics.f1_score(self.true_labels, self.predicted_labels, average="macro").
        If also weighted = True, then the same as average="weighted".
        :param scores:
        :param weighted:
        :return:
        """
        if weighted:
            return self.calculateWeightedMeanF1(scores)
        else:
            return np.mean(scores.values())

    def calculateF1ScoreDict(self, beta):
        return {frequency: self.calculateF1(
            np.array(self.true_labels) == self.frequency_to_label[frequency],
            np.array(self.predicted_labels) == self.frequency_to_label[frequency],
            beta
        ) for frequency in self.target_frequencies}

    def getData(self, beta=1, weighted=True):
        diagonal_elements, off_diagonal_elements = self.countMatrixElements()
        accuracy = self.getPrecision(diagonal_elements, off_diagonal_elements)
        time_in_sec = self.getTimeInSec(self.total_packets)
        time_per_target = self.getTimePerTarget(diagonal_elements+off_diagonal_elements, time_in_sec)
        itr = self.getItrBitPerTrial(accuracy, self.target_count)
        f1_scores = self.calculateF1ScoreDict(beta)
        return {
            c.RESULTS_DATA_TOTAL_TIME_PACKETS: self.total_packets,
            c.RESULTS_DATA_TOTAL_TIME_SECONDS: time_in_sec,
            c.RESULTS_DATA_TIME_PER_TARGET: time_per_target,
            c.RESULTS_DATA_ACCURACY: accuracy,
            c.RESULTS_DATA_DIAGONAL_ELEMENTS: diagonal_elements,
            c.RESULTS_DATA_OFF_DIAGONAL_ELEMENTS: off_diagonal_elements,
            c.RESULTS_DATA_ITR_BIT_PER_TRIAL: itr,
            c.RESULTS_DATA_ITR_BIT_PER_MIN: self.getItrBitPerMin(itr, time_per_target),
            c.RESULTS_DATA_F1: f1_scores,
            c.RESULTS_DATA_MACRO_F1: self.calculateMeanF1(f1_scores, weighted),
        }

    def __repr__(self):
        result = "\n".join(str(key) + ": " + str(value) for key, value in self.getData().items()) + "\n"
        for freq in self.results:
            result += str(freq) + " " + str(self.results[freq]) + "\n"
        # result += str(self.true_labels) + "\n"
        # result += str(self.predicted_labels) + "\n"
        return result
