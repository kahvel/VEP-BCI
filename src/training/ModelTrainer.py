import numpy as np
import sklearn.metrics
import scipy

import matplotlib.pyplot as plt
import matplotlib2tikz

from target_identification.models import LdaModel, TransitionModel, CalibrationModel, CvCalibrationModel
import Curve
import constants as c


class ModelTrainer(object):
    def __init__(self):
        self.recordings = []
        self.eeg = []
        self.look_back_length = None
        self.cross_validation_folds = None
        self.training_recordings = []
        self.testing_recordings = []
        self.training_data = None
        self.training_labels = None
        self.testing_data = None
        self.testing_labels = None
        self.testing_roc = None
        self.training_roc = None
        self.training_prc = None
        self.testing_prc = None
        self.model = None
        self.lda_model = None
        self.transition_model = None
        self.thresholds = None
        self.min_max = None
        self.random_forest_model = None
        self.cv_model = None
        self.features_to_use = None

    def setRecordings(self, recordings):
        self.recordings = recordings

    def setEeg(self, eeg):
        self.eeg = eeg

    def setup(self, options):
        self.features_to_use = options[c.MODELS_PARSE_FEATURES_TO_USE]
        self.look_back_length = options[c.MODELS_PARSE_LOOK_BACK_LENGTH]
        self.cross_validation_folds = options[c.MODELS_PARSE_CV_FOLDS]
        self.training_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_TRAINING]]
        self.testing_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_TESTING]]
        self.model = LdaModel.TrainingLdaModel()
        self.model.setup(self.features_to_use, self.look_back_length, self.recordings, True)
        self.transition_model = TransitionModel.TrainingModel(False)
        self.transition_model.setup(None, 1)
        self.cv_model = CvCalibrationModel.TrainingModel()
        self.cv_model.setup(self.features_to_use, self.look_back_length, self.recordings, [True])

    def getConfusionMatrix(self, model, data, labels, label_order):
        prediction = model.predict(data)
        return sklearn.metrics.confusion_matrix(labels, prediction, labels=label_order)

    def getThresholdConfusionMatrix(self, prediction, labels, label_order):
        return sklearn.metrics.confusion_matrix(labels, prediction, labels=list(label_order)+["None"])

    def calculateBinaryRoc(self, predictions, binary_labels, labels_order):
        fpr = dict()
        tpr = dict()
        thresholds = dict()
        roc_auc = dict()
        for i in range(len(labels_order)):
            fpr[i], tpr[i], thresholds[i] = sklearn.metrics.roc_curve(binary_labels[i], predictions[i])
            roc_auc[i] = sklearn.metrics.auc(fpr[i], tpr[i])
        return fpr, tpr, thresholds, roc_auc

    def calculateBinaryPrecisionRecallCurve(self, predictions, binary_labels, labels_order):
        precision = dict()
        recall = dict()
        thresholds = dict()
        average_precision = dict()
        for i in range(len(labels_order)):
            precision[i], recall[i], thresholds[i] = sklearn.metrics.precision_recall_curve(binary_labels[i], predictions[i])
            average_precision[i] = sklearn.metrics.average_precision_score(binary_labels[i], predictions[i])
        return recall, precision, thresholds, average_precision

    def addMicroPrecisionRecallCurve(self, curve, predictions, binary_labels):
        binary_labels = np.array(binary_labels)
        recall, precision, thresholds, average_precision = curve
        precision["micro"], recall["micro"], _ = sklearn.metrics.precision_recall_curve(binary_labels.ravel(), predictions.ravel())
        average_precision["micro"] = sklearn.metrics.average_precision_score(binary_labels, predictions, average="micro")

    def addMicroRoc(self, roc, predictions, binary_labels):
        fpr, tpr, _, roc_auc = roc
        fpr["micro"], tpr["micro"], _ = sklearn.metrics.roc_curve(np.array(binary_labels).ravel(), predictions.ravel())
        roc_auc["micro"] = sklearn.metrics.auc(fpr["micro"], tpr["micro"])

    def addMacroRoc(self, roc, labels_order):
        fpr, tpr, _, roc_auc = roc
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(len(labels_order))]))
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(len(labels_order)):
            mean_tpr += scipy.interp(all_fpr, fpr[i], tpr[i])
        mean_tpr /= len(labels_order)
        fpr["macro"] = all_fpr
        tpr["macro"] = mean_tpr
        roc_auc["macro"] = sklearn.metrics.auc(fpr["macro"], tpr["macro"])

    def calculateThresholds(self, roc, labels_order, fpr_threshold=0.05):
        fpr, tpr, thresholds, _ = roc
        cut_off_threshold = []
        for i in range(len(labels_order)):
            cut_off_threshold.append(thresholds[i][np.argmax(tpr[i][:-1])])
        return cut_off_threshold
        # for i in range(len(labels_order)):
        #     for j, (false_positive_rate, true_positive_rate, threshold) in enumerate(zip(fpr[i], tpr[i], thresholds[i])):
        #         if true_positive_rate == 1:
        #             # assert j-1 > 0
        #             cut_off_threshold.append(thresholds[i][j-1])
        #             break
        #         if false_positive_rate > fpr_threshold:
        #             cut_off_threshold.append(threshold)
        #             break
        #     else:
        #         print "Warning: no cutoff obtained!"
        # return cut_off_threshold

    def getBinaryLabels(self, labels, label_order):
        binary_labels = []
        for label in label_order:
            binary_labels.append(list(map(lambda x: x == label, labels)))
        return binary_labels

    def calculateMulticlassPrecisionRecallCurve(self, decision_function_values, binary_labels, label_order):
        curve = self.calculateBinaryPrecisionRecallCurve(decision_function_values, binary_labels, label_order)
        self.addMicroPrecisionRecallCurve(curve, decision_function_values, binary_labels)
        return curve

    def calculateMulticlassRoc(self, decision_function_values, binary_labels, label_order):
        roc = self.calculateBinaryRoc(decision_function_values, binary_labels, label_order)
        self.addMicroRoc(roc, decision_function_values, binary_labels)
        self.addMacroRoc(roc, label_order)
        return roc

    def calculateRoc(self, decision_function_values, labels, label_order):
        binary_labels = self.getBinaryLabels(labels, label_order)
        return self.calculateMulticlassRoc(decision_function_values, binary_labels, label_order)

    def calculatePrecisionRecallCurve(self, decision_function_values, labels, label_order):
        binary_labels = self.getBinaryLabels(labels, label_order)
        return self.calculateMulticlassPrecisionRecallCurve(decision_function_values, binary_labels, label_order)

    def plotChange(self, data, labels, index, color, plot_count, target_count):
        x = np.arange(0, len(data))
        plt.subplot(plot_count, 1, index+1)
        decision = data.T[index]
        plt.plot(x, decision, color=color)
        plt.plot(x, (labels == index % target_count + 1)*decision.max() + (1-(labels == index % target_count + 1))*decision.min(), "r--", color=color)

    def plotAllChanges(self, data, labels):
        plt.figure()
        colors = ["red", "green", "blue"]
        plot_count = data.shape[1]
        target_count = len(colors)
        for i in range(plot_count):
            self.plotChange(data, labels, i, colors[i%target_count], plot_count, target_count)
        # import time
        # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")

    def splitTrainingData(self):
        data_split = []
        labels_split = []
        for recording in self.training_recordings:
            data, labels = self.cv_model.getConcatenatedMatrix([recording])
            data_split.append(data)
            labels_split.append(labels)
        return data_split, labels_split

    def crossValidationPrecisionRecallCurve(self, training_data_split, training_labels_split, label_order):
        all_x = []
        all_y = []
        all_thresholds = []
        all_auc = []
        for data, labels in zip(training_data_split, training_labels_split):
            curve = self.calculatePrecisionRecallCurve(self.cv_model.predictProba(data), labels, label_order)
            chosen_thresholds = self.calculateThresholds(curve, self.cv_model.getOrderedLabels())
            x, y, thresholds, auc = curve

    def start(self):
        training_data_split, training_labels_split = self.splitTrainingData()
        training_data, training_labels = self.cv_model.getConcatenatedMatrix(self.training_recordings)

        self.cv_model.fit(training_data, training_labels)

        # training_data_per_recording, training_labels_per_recording = self.model.getAllLookBackRatioMatrices(self.training_recordings)
        # training_lda_values = map(lambda x: self.model.decisionFunction(x), training_data_per_recording)
        # reduced_data, reduced_labels = self.transition_model.getConcatenatedMatrix(training_lda_values, training_labels_per_recording)
        # reduced_labels = map(str, reduced_labels)
        # self.transition_model.fit(reduced_data, reduced_labels)
        # training_roc = self.calculateRoc(self.transition_model.getDecisionFunctionValues(reduced_data), reduced_labels, self.transition_model.getOrderedLabels())

        testing_data, testing_labels = self.cv_model.getConcatenatedMatrix(self.testing_recordings)

        # validation_data_per_recording, validation_labels_per_recording = self.model.getAllLookBackRatioMatrices(self.validation_recordings)
        # validation_lda_values = map(lambda x: self.model.decisionFunction(x), validation_data_per_recording)
        # reduced_validation_data, reduced_validation_labels = self.transition_model.getConcatenatedMatrix(validation_lda_values, validation_labels_per_recording)
        # reduced_validation_labels = map(str, reduced_validation_labels)

        label_order = self.cv_model.getOrderedLabels()
        # training_roc = self.calculateRoc(self.model.getDecisionFunctionValues(training_data), training_labels, label_order)
        # validation_roc = self.calculateRoc(self.model.getDecisionFunctionValues(testing_data), testing_labels, label_order)
        # validation_roc = self.calculateRoc(self.transition_model.getDecisionFunctionValues(reduced_validation_data), reduced_validation_labels, self.transition_model.getOrderedLabels())
        # thresholds = self.calculateThresholds(validation_roc, self.transition_model.getOrderedLabels())
        training_roc = Curve.RocCurve().calculate(np.transpose(self.cv_model.predictProba(training_data)), training_labels, label_order)
        testing_roc = Curve.RocCurve().calculate(np.transpose(self.cv_model.predictProba(testing_data)), testing_labels, label_order)
        training_prc = Curve.PrecisionRecallCurve().calculate(np.transpose(self.cv_model.predictProba(training_data)), training_labels, label_order)
        testing_prc = Curve.PrecisionRecallCurve().calculate(np.transpose(self.cv_model.predictProba(testing_data)), testing_labels, label_order)
        thresholds = self.calculateThresholds(testing_prc, self.cv_model.getOrderedLabels())

        # print self.getConfusionMatrix(self.transition_model, reduced_data, reduced_labels, self.transition_model.getOrderedLabels())
        # print self.getConfusionMatrix(self.transition_model, reduced_validation_data, reduced_validation_labels, self.transition_model.getOrderedLabels())
        # print self.transition_model.getOrderedLabels()
        print sklearn.metrics.confusion_matrix(training_labels, self.cv_model.predict(training_data), labels=self.cv_model.getOrderedLabels())
        print sklearn.metrics.confusion_matrix(testing_labels, self.cv_model.predict(testing_data), labels=self.cv_model.getOrderedLabels())
        for i in range(3):
            print i
            # print self.getThresholdConfusionMatrix(self.transition_model.thresholdPredict(reduced_data, thresholds, i/10.0), reduced_labels, self.transition_model.getOrderedLabels())
            # print self.getThresholdConfusionMatrix(self.transition_model.thresholdPredict(reduced_validation_data, thresholds, i/10.0), reduced_validation_labels, self.transition_model.getOrderedLabels())
            print self.getThresholdConfusionMatrix(self.cv_model.thresholdPredict(training_data, thresholds, i/10.0), map(str, training_labels), self.cv_model.getOrderedLabels())
            print self.getThresholdConfusionMatrix(self.cv_model.thresholdPredict(testing_data, thresholds, i/10.0), map(str, testing_labels), self.cv_model.getOrderedLabels())

        # self.plotAllChanges(self.cv_model.predictProba(training_data), training_labels)
        # self.plotAllChanges(self.cv_model.predictProba(testing_data), testing_labels)
        # plt.show()
        # dummy_model = CvCalibrationModel.TrainingModel()
        # dummy_model.setup(self.features_to_use, 1, self.recordings, [False])
        # features, labels = dummy_model.getConcatenatedMatrix(self.validation_recordings)
        # self.plotAllChanges(features, labels)
        # plt.show()

        self.training_data = training_data
        self.training_labels = training_labels
        self.testing_data = testing_data
        self.testing_labels = testing_labels
        self.thresholds = thresholds
        self.min_max = self.cv_model.getMinMax()
        self.lda_model = None  # self.model.model
        self.training_prc = training_prc
        self.testing_prc = testing_prc
        self.training_roc = training_roc
        self.testing_roc = testing_roc

    def getSecondModel(self):
        return self.cv_model.model

    def getModel(self):
        return self.lda_model

    def getTrainingData(self):
        return self.training_data

    def getTrainingLabels(self):
        return self.training_labels

    def getTestingData(self):
        return self.testing_data

    def getTestingLabels(self):
        return self.testing_labels

    def getThresholds(self):
        return self.thresholds

    def getMinMax(self):
        return self.min_max

    def getTrainingRoc(self):
        return self.training_roc

    def getTestingRoc(self):
        return self.testing_roc

    def getTrainingPrc(self):
        return self.training_prc

    def getTestingPrc(self):
        return self.testing_prc

    def getUsedFeatures(self):
        return self.model.getUsedFeatures()
