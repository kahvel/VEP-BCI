import numpy as np
import sklearn.metrics
import matplotlib.pyplot as plt

from target_identification.models import LdaModel, TransitionModel, CvCalibrationModel
from curves import AverageCurve, CvCurves
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

    def plotChange(self, data, labels, index, color, plot_count, target_count):
        x = np.arange(0, len(data))
        plt.subplot(plot_count, 1, index+1)
        decision = data.T[index]
        plt.plot(x, decision, color=color)
        plt.plot(x, (labels == index % target_count + 1)*decision.max() + (1-(labels == index % target_count + 1))*decision.min(), "r--", color=color)

    def plotAllChanges(self, data, labels, thresholds):
        plt.figure()
        colors = ["red", "green", "blue"]
        plot_count = data.shape[1]
        target_count = len(colors)
        for i in range(plot_count):
            self.plotChange(data, labels, i, colors[i%target_count], plot_count, target_count)
            plt.plot([0, data.shape[0]], [thresholds[i], thresholds[i]], color=colors[i%target_count])
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

    def allExceptOne(self, data, index):
        return [x for i, x in enumerate(data) if i != index]

    def crossValidation(self, model, split_data, split_labels):
        folds = len(split_data)
        predictions = []
        for i in range(folds):
            data = np.concatenate(self.allExceptOne(split_data, i), axis=0)
            labels = np.concatenate(self.allExceptOne(split_labels, i), axis=0)
            model.fit(data, labels)
            predictions.append(model.predictProba(split_data[i]))
        return predictions

    # def secondModel(self, cv_predictions, split_data):
    #     data = np.concatenate(cv_predictions, axis=0)
    #     labels = np.concatenate(split_data, axis=0)
    #     model = LinearDiscriminantAnalysis()
    #     model.fit(data, labels)
    #     return model

    def start(self):
        training_data, training_labels = self.cv_model.getConcatenatedMatrix(self.training_recordings)

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

        # training_roc = self.calculateRoc(self.model.getDecisionFunctionValues(training_data), training_labels, label_order)
        # validation_roc = self.calculateRoc(self.model.getDecisionFunctionValues(testing_data), testing_labels, label_order)
        # validation_roc = self.calculateRoc(self.transition_model.getDecisionFunctionValues(reduced_validation_data), reduced_validation_labels, self.transition_model.getOrderedLabels())
        # thresholds = self.calculateThresholds(validation_roc, self.transition_model.getOrderedLabels())

        split_data, split_labels = self.splitTrainingData()
        cv_predictions = self.crossValidation(self.cv_model, split_data, split_labels)
        self.cv_model.fit(training_data, training_labels)
        label_order = self.cv_model.getOrderedLabels()
        modified_training_labels = training_labels[1:-1]
        modified_testing_labels = testing_labels[1:-1]
        split_labels = map(lambda x: x[1:-1], split_labels)
        if len(split_data) == 1:
            training_roc = AverageCurve.AverageRocCurve(label_order).calculate(np.transpose(self.cv_model.predictProba(training_data)), modified_training_labels)
            training_prc = AverageCurve.AveragePrecisionRecallCurve(label_order).calculate(np.transpose(self.cv_model.predictProba(training_data)), modified_training_labels)
        else:
            training_roc = CvCurves.RocCvCurve(label_order).calculate(cv_predictions, split_labels)
            training_prc = CvCurves.PrecisionRecallCvCurve(label_order).calculate(cv_predictions, split_labels)
        testing_roc = AverageCurve.AverageRocCurve(label_order).calculate(np.transpose(self.cv_model.predictProba(testing_data)), modified_testing_labels)
        testing_prc = AverageCurve.AveragePrecisionRecallCurve(label_order).calculate(np.transpose(self.cv_model.predictProba(testing_data)), modified_testing_labels)
        thresholds = training_prc.calculateThresholds()

        # training_prc = AverageCurve.AveragePrecisionRecallCurve(label_order).calculate(np.transpose(self.cv_model.predictProba(training_data)), training_labels)
        # testing_prc = AverageCurve.AveragePrecisionRecallCurve(label_order).calculate(np.transpose(self.cv_model.predictProba(testing_data)), testing_labels)
        # thresholds = testing_prc.calculateThresholds()

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

        self.plotAllChanges(self.cv_model.predictProba(training_data), modified_training_labels, thresholds)
        self.plotAllChanges(self.cv_model.predictProba(testing_data), modified_testing_labels, thresholds)
        plt.show()
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
