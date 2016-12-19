import numpy as np
import sklearn.metrics
import scipy

import matplotlib.pyplot as plt
import matplotlib2tikz

from target_identification.models import LdaModel, TransitionModel, CalibrationModel, CvCalibrationModel
import constants as c


class ModelTrainer(object):
    def __init__(self):
        self.recordings = []
        self.look_back_length = None
        self.cross_validation_folds = None
        self.training_recordings = []
        self.validation_recordings = []
        self.training_data = None
        self.training_labels = None
        self.validation_data = None
        self.validation_labels = None
        self.validation_roc = None
        self.training_roc = None
        self.model = None
        self.lda_model = None
        self.transition_model = None
        self.thresholds = None
        self.min_max = None
        self.random_forest_model = None
        self.cv_model = None

    def setRecordings(self, recordings):
        self.recordings = recordings

    def setup(self, options):
        features_to_use = options[c.MODELS_PARSE_FEATURES_TO_USE]
        self.look_back_length = options[c.MODELS_PARSE_LOOK_BACK_LENGTH]
        self.cross_validation_folds = options[c.MODELS_PARSE_CV_FOLDS]
        self.training_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_TRAINING]]
        self.validation_recordings = [self.recordings[i] for i in options[c.MODELS_PARSE_RECORDING_FOR_VALIDATION]]
        self.model = LdaModel.TrainingLdaModel()
        self.model.setup(features_to_use, self.look_back_length, self.recordings)
        self.transition_model = TransitionModel.TrainingModel(False)
        self.transition_model.setup(None, 1)
        self.cv_model = CvCalibrationModel.TrainingModel()
        self.cv_model.setup(None, self.look_back_length)

    def getConfusionMatrix(self, model, data, labels, label_order):
        prediction = model.predict(data)
        return sklearn.metrics.confusion_matrix(labels, prediction, labels=label_order)

    def getThresholdConfusionMatrix(self, prediction, labels, label_order):
        return sklearn.metrics.confusion_matrix(labels, prediction, labels=list(label_order)+["None"])

    def calculateBinaryRoc(self, predictions, binary_labels, labels_order):
        predictions = np.transpose(predictions)
        fpr = dict()
        tpr = dict()
        thresholds = dict()
        roc_auc = dict()
        for i in range(len(labels_order)):
            fpr[i], tpr[i], thresholds[i] = sklearn.metrics.roc_curve(binary_labels[i], predictions[i])
            roc_auc[i] = sklearn.metrics.auc(fpr[i], tpr[i])
        return fpr, tpr, thresholds, roc_auc

    def addMicroRoc(self, roc, predictions, binary_labels):
        predictions = np.array(predictions)
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
            for j, (false_positive_rate, true_positive_rate, threshold) in enumerate(zip(fpr[i], tpr[i], thresholds[i])):
                if true_positive_rate == 1:
                    assert j-1 > 0
                    cut_off_threshold.append(thresholds[i][j-1])
                    break
                if false_positive_rate > fpr_threshold:
                    cut_off_threshold.append(threshold)
                    break
            else:
                print "Warning: no cutoff obtained!"
        return cut_off_threshold

    def getBinaryLabels(self, labels, label_order):
        binary_labels = []
        for label in label_order:
            binary_labels.append(list(map(lambda x: x == label, labels)))
        return binary_labels

    def calculateMulticlassRoc(self, decision_function_values, binary_labels, label_order):
        roc = self.calculateBinaryRoc(decision_function_values, binary_labels, label_order)
        self.addMicroRoc(roc, decision_function_values, binary_labels)
        self.addMacroRoc(roc, binary_labels)
        return roc

    def calculateRoc(self, decision_function_values, labels, label_order):
        binary_labels = self.getBinaryLabels(labels, label_order)
        return self.calculateMulticlassRoc(decision_function_values, binary_labels, label_order)

    def plotChange(self, data, labels, index, color):
        x = np.arange(0, len(data))
        plt.subplot(3,1,index+1)
        decision = data.T[index]
        plt.plot(x, decision, color=color)
        plt.plot(x, (labels == index+1)*decision.max() + (1-(labels == index+1))*decision.min(), "r--", color=color)

    def plotAllChanges(self, data, labels):
        self.plotChange(data, labels, 0, "red")
        self.plotChange(data, labels, 1, "green")
        self.plotChange(data, labels, 2, "blue")
        # import time
        # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")
        plt.show()

    def start(self):
        training_data, training_labels = self.model.getConcatenatedMatrix(self.training_recordings)
        self.model.fit(training_data, training_labels)
        self.cv_model.fit(training_data, training_labels)

        training_data_per_recording, training_labels_per_recording = self.model.getAllLookBackRatioMatrices(self.training_recordings)
        training_lda_values = map(lambda x: self.model.decisionFunction(x), training_data_per_recording)
        reduced_data, reduced_labels = self.transition_model.getConcatenatedMatrix(training_lda_values, training_labels_per_recording)
        reduced_labels = map(str, reduced_labels)
        self.transition_model.fit(reduced_data, reduced_labels)
        training_roc = self.calculateRoc(self.transition_model.getDecisionFunctionValues(reduced_data), reduced_labels, self.transition_model.getOrderedLabels())

        validation_data, validation_labels = self.model.getConcatenatedMatrix(self.validation_recordings)

        validation_data_per_recording, validation_labels_per_recording = self.model.getAllLookBackRatioMatrices(self.validation_recordings)
        validation_lda_values = map(lambda x: self.model.decisionFunction(x), validation_data_per_recording)
        reduced_validation_data, reduced_validation_labels = self.transition_model.getConcatenatedMatrix(validation_lda_values, validation_labels_per_recording)
        reduced_validation_labels = map(str, reduced_validation_labels)

        label_order = self.model.getOrderedLabels()
        # training_roc = self.calculateRoc(self.model.getDecisionFunctionValues(training_data), training_labels, label_order)
        # validation_roc = self.calculateRoc(self.model.getDecisionFunctionValues(validation_data), validation_labels, label_order)
        validation_roc = self.calculateRoc(self.transition_model.getDecisionFunctionValues(reduced_validation_data), reduced_validation_labels, self.transition_model.getOrderedLabels())
        thresholds = self.calculateThresholds(validation_roc, self.transition_model.getOrderedLabels())
        roc = self.calculateRoc(self.cv_model.predictProba(training_data), training_labels, label_order)
        roc2 = self.calculateRoc(self.cv_model.predictProba(validation_data), validation_labels, label_order)
        thresholds2 = self.calculateThresholds(roc2, self.cv_model.getOrderedLabels())

        print self.getConfusionMatrix(self.transition_model, reduced_data, reduced_labels, self.transition_model.getOrderedLabels())
        print self.getConfusionMatrix(self.transition_model, reduced_validation_data, reduced_validation_labels, self.transition_model.getOrderedLabels())
        print self.transition_model.getOrderedLabels()
        print sklearn.metrics.confusion_matrix(training_labels, self.cv_model.predict(training_data), labels=self.cv_model.getOrderedLabels())
        print sklearn.metrics.confusion_matrix(validation_labels, self.cv_model.predict(validation_data), labels=self.cv_model.getOrderedLabels())
        for i in range(21):
            print i
            print self.getThresholdConfusionMatrix(self.transition_model.thresholdPredict(reduced_data, thresholds, i/10.0), reduced_labels, self.transition_model.getOrderedLabels())
            print self.getThresholdConfusionMatrix(self.transition_model.thresholdPredict(reduced_validation_data, thresholds, i/10.0), reduced_validation_labels, self.transition_model.getOrderedLabels())
            print self.getThresholdConfusionMatrix(self.cv_model.thresholdPredict(training_data, thresholds2, i/10.0), map(str, training_labels), self.cv_model.getOrderedLabels())
            print self.getThresholdConfusionMatrix(self.cv_model.thresholdPredict(validation_data, thresholds2, i/10.0), map(str, validation_labels), self.cv_model.getOrderedLabels())

        # self.plotAllChanges(self.model.decisionFunction(training_data), training_labels)
        # self.plotAllChanges(self.model.decisionFunction(validation_data), validation_labels)
        self.plotAllChanges(self.cv_model.predictProba(training_data), training_labels)
        self.plotAllChanges(self.cv_model.predictProba(validation_data), validation_labels)

        self.training_data = training_data
        self.training_labels = training_labels
        self.validation_data = validation_data
        self.validation_labels = validation_labels
        self.thresholds = thresholds2
        self.min_max = self.model.getMinMax()
        self.lda_model = self.model.model
        self.training_roc = roc
        self.validation_roc = roc2

    def getSecondModel(self):
        return self.cv_model.model

    def getModel(self):
        return self.lda_model

    def getTrainingData(self):
        return self.training_data

    def getTrainingLabels(self):
        return self.training_labels

    def getValidationData(self):
        return self.validation_data

    def getValidationLabels(self):
        return self.validation_labels

    def getThresholds(self):
        return self.thresholds

    def getMinMax(self):
        return self.min_max

    def getTrainingRoc(self):
        return self.training_roc

    def getValidationRoc(self):
        return self.validation_roc

    def getUsedFeatures(self):
        return self.model.getUsedFeatures()
