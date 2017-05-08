import numpy as np
# import scipy.integrate
import sklearn.metrics
import matplotlib.pyplot as plt

from target_identification.models import LdaModel, TransitionModel, CvCalibrationModel
from curves import AverageCurve, CvCurves
from training import ItrCalculator
import constants as c

from sklearn.ensemble import AdaBoostClassifier


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
        # Check before testing!!
        self.t_use_ml = True
        self.t_use_maf_on_features = True
        self.t_use_maf_on_probas = False and self.t_use_ml
        self.t_normalise_probas = False and self.t_use_ml
        self.t_matrix_builder_types = [True]
        self.hacky_labels = [1,2,3]
        self.t_remove_samples_features = True and self.t_use_maf_on_features
        self.t_remove_samples_probas = True and self.t_use_maf_on_probas
        self.t_feature_maf = self.getMafLength(self.t_use_maf_on_features)
        self.t_proba_maf = self.getMafLength(self.t_use_maf_on_probas)
        self.itr_calculator = ItrCalculator.ItrAccuracySubMatrix(
            window_length=1,
            step=0.125,
            feature_maf_length=self.t_feature_maf,
            proba_maf_length=self.t_proba_maf,
            look_back_length=1 if self.t_use_ml is False else options[c.MODELS_PARSE_LOOK_BACK_LENGTH],
            n_targets=3,
        )
        self.itr_calculator2 = ItrCalculator.ItrCalculator(
            window_length=1,
            step=0.125,
            feature_maf_length=self.t_feature_maf,
            proba_maf_length=self.t_proba_maf,
            look_back_length=1 if self.t_use_ml is False else options[c.MODELS_PARSE_LOOK_BACK_LENGTH],
            n_targets=3,
        )
        # CvCalibrationModel predictProba
        # Normalising = True (before applying MAF)
        # Calibrated cv = 5
        # OneVsOne = {1: 0.8, 0: 0.2}
        # FPR test = 5e-2
        # CvCurves = grid search on ITR

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
        self.cv_model.setup(self.features_to_use, self.look_back_length, self.recordings, self.t_matrix_builder_types)

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

    def predictProbaCv(self, model, split_data, split_labels):
        folds = len(split_data)
        predictions = []
        for i in range(folds):
            data = np.concatenate(self.allExceptOne(split_data, i), axis=0)
            labels = np.concatenate(self.allExceptOne(split_labels, i), axis=0)
            model.fit(data, labels)
            predictions.append(model.predictProba(split_data[i], self.t_proba_maf, self.t_normalise_probas))
        return predictions

    # def secondModel(self, cv_predictions, split_data):
    #     data = np.concatenate(cv_predictions, axis=0)
    #     labels = np.concatenate(split_data, axis=0)
    #     model = LinearDiscriminantAnalysis()
    #     model.fit(data, labels)
    #     return model

    # def derivative(self, x, y):
    #     print x, y
    #     c1 = self.t_window_length + (self.t_look_back_length + self.t_feature_maf + self.t_proba_maf - 4)*self.t_step
    #     c2 = float(self.t_step)
    #     itr = self.getItrBitPerTrial(y)
    #     numerator = c2/x**2*itr
    #     denominator = np.log2(y*(self.t_N - 1)/(1-y))*(c1+c2/x)
    #     return numerator/denominator
    #
    # def estimate(self):
    #     estimator = scipy.integrate.ode(self.derivative)
    #     estimator.set_integrator("dop853").set_initial_value(0.5, 0.5)
    #     dt = 0.1
    #     max_t = 1
    #     # estimator.integrate(estimator.t, step=dt)
    #     while estimator.successful() and estimator.t < max_t:
    #         estimator.integrate(estimator.t+dt)
    #         print ("asd %g %g" % (estimator.t, estimator.y))
    #     raw_input()

    # def optimisationFunction(self, indices, all_thresholds, prediction, labels, label_order):
    #     current_thresholds = list(thresholds[index] for thresholds, index in zip(all_thresholds, indices))
    #     threshold_predictions = self.cv_model.thresholdPredict(prediction, current_thresholds, 0)
    #     confusion_matrix = self.getThresholdConfusionMatrix(threshold_predictions, labels, label_order)
    #     accuracy = self.calculateAccuracyIgnoringLastColumn(confusion_matrix)
    #     support = self.calculateSupport(confusion_matrix)
    #     result = -self.itr_calculator.itrBitPerMin(accuracy, support)
    #     return result

    def calculateSupport(self, confusion_matrix):
        if not isinstance(confusion_matrix, float):
            matrix_sum = confusion_matrix.sum()
            return (matrix_sum-confusion_matrix.sum(axis=0)[-1])/matrix_sum

    def calculateAccuracy(self, confusion_matrix):
        if not isinstance(confusion_matrix, float):
            return np.trace(confusion_matrix)/confusion_matrix.sum()

    def calculateAccuracyIgnoringLastColumn(self, confusion_matrix):
        if not isinstance(confusion_matrix, float):
            return np.trace(confusion_matrix)/(confusion_matrix.sum()-confusion_matrix.sum(axis=0)[-1])

    def printConfusionMatrixData(self, confusion_matrix):
        accuracy = self.calculateAccuracyIgnoringLastColumn(confusion_matrix)
        support = self.calculateSupport(confusion_matrix)
        print self.itr_calculator.itrBitPerMin(accuracy, support)
        print accuracy
        print confusion_matrix

    # def getLabelConverter(self, label_order):
    #     n = len(label_order)
    #     return [{label_order[i]: label_order[(i+shift) % n] for i in range(n)} for shift in range(n)]

    # def rollLabels(self, label_converter, split_labels):
    #     n = len(label_converter)
    #     return list(map(lambda labels: map(lambda label: label_converter[i][label], labels), split_labels) for i in range(n))

    def calculateAverageRocCurve(self, label_order, prediction, labels):
        return AverageCurve.AverageRocCurve(label_order).calculate(prediction, labels)

    def calculateAveragePrcCurve(self, label_order, prediction, labels):
        return AverageCurve.AveragePrecisionRecallCurve(label_order).calculate(prediction, labels)

    def calculateCvRocCurve(self, label_order, prediction, labels):
        return CvCurves.RocCvCurve(label_order).calculate(prediction, labels)

    def calculateCvPrcCurve(self, label_order, prediction, labels):
        return CvCurves.PrecisionRecallCvCurve(label_order).calculate(prediction, labels)

    # def calculateSplitCurves(self, label_order, prediction, rolled_labels, function):
    #     return list(function(label_order, prediction if i == 0 else prediction*-1, split_labels) for i, split_labels in enumerate(rolled_labels))
    #
    # def calculateSplitRocs(self, label_order, prediction, rolled_labels):
    #     return self.calculateSplitCurves(label_order, prediction, rolled_labels, self.calculateCvRocCurve)
    #
    # def calculateSplitPrcs(self, label_order, prediction, rolled_labels):
    #     return self.calculateSplitCurves(label_order, prediction, rolled_labels, self.calculateCvPrcCurve)
    #
    # def calculateSplitThresholds(self, split_training_prcs):
    #     split_current_thresholds = map(lambda x: np.array(x.calculateThresholds()), split_training_prcs[-1])
    #     split_current_thresholds = map(lambda (i, t): t*-1 if i != 0 else t, enumerate(split_current_thresholds))
    #     split_current_thresholds = list(np.roll(t, -i) for i, t in enumerate(split_current_thresholds))
    #     return split_current_thresholds

    # def calculateMultidimensionalPrc(self, label_order, predictions, rolled_labels):
    #     curves = self.calculateSplitPrcs(label_order, predictions, rolled_labels)
    #     for curve in curves:
    #         for class_curve in curve.curves_by_class:
    #             for split_curve in class_curve.curves:

    # def countClasses(self, label_order, labels):
    #     return map(lambda label: sum(map(lambda x: x == label, labels)), label_order)

    def calculateAverageCurves(self, label_order, prediction, labels):
        return (
            self.calculateAverageRocCurve(label_order, np.transpose(prediction), labels),
            self.calculateAveragePrcCurve(label_order, np.transpose(prediction), labels)
        )

    def calculateCvCurves(self, label_order, split_predictions, split_labels):
        return (
            self.calculateCvRocCurve(label_order, split_predictions, split_labels),
            self.calculateCvPrcCurve(label_order, split_predictions, split_labels)
        )

    # def modifyLabels(self, use_maf, labels):
    #     if use_maf:
    #         return labels[1:-1]
    #     else:
    #         return labels

    def modifySplitLabels(self, use_maf, split_labels):
        if use_maf:
            return map(lambda x: x[1:-1], split_labels)
        else:
            return split_labels

    # def modifyTrainingLabels(self, use_maf, training_labels):
    #     return self.modifySplitLabels(use_maf, training_labels)

    def getMafLength(self, use_maf):
        return 3 if use_maf else 1

    def fitAndPredictProbaSingle(self, model, data, labels):
        model.fit(data, labels)
        return model.predictProba(data, self.t_proba_maf, self.t_normalise_probas)

    def fitAndPredictProbaCv(self, model, data, labels):
        cv_predictions = np.array(self.predictProbaCv(model, data, labels))
        model.fit(np.concatenate(data, 0), np.concatenate(labels, 0))
        return cv_predictions

    def fitAndPredictProba(self, n_folds, model, data, labels):
        if n_folds == 1:
            return [self.fitAndPredictProbaSingle(model, data[0], labels[0])]
        else:
            return self.fitAndPredictProbaCv(model, data, labels)

    def calculateTrainingFeatures(self, n_folds, model, data, labels):
        if self.t_use_ml:
            return self.fitAndPredictProba(n_folds, model, data, labels)
        else:
            return self.hackyFeatureFix(data)

    def calculateTestingFeatures(self, model, data):
        if self.t_use_ml:
            return model.predictProba(data, self.t_proba_maf, self.t_normalise_probas)
        else:
            return self.applyRoll(data)

    def hackyFeatureFix(self, data):
        return map(lambda x: self.applyRoll(x), data)

    def applyRoll(self, data):
        return np.roll(data, 1, axis=1)

    def applyMovingAverage(self, data, n):
        return np.transpose(map(lambda x: self.moving_average(x, n), np.transpose(data)))

    def moving_average(self, a, n) :
        ret = np.cumsum(a, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

    def getLabelOrder(self, model):
        if self.t_use_ml:
            return model.getOrderedLabels()
        else:
            return self.hacky_labels

    def removeSamples(self, data, samples_to_remove):
        return map(lambda (x, s): np.delete(x, s, axis=0), zip(data, samples_to_remove))

    def removeSamplesBeforeAfterClassChange(self, split_data, split_labels):
        class_change = map(lambda x: np.where(x[:-1] != x[1:])[0], split_labels)
        samples_to_remove = map(lambda y: np.concatenate(map(lambda x: [x, x+1], y)), class_change)
        # print map(lambda (x,y): list(x[i] for i in y), zip(split_labels, samples_to_remove))
        return (
            np.array(self.removeSamples(split_data, samples_to_remove)),
            np.array(self.removeSamples(split_labels, samples_to_remove))
        )

    def calculateCurves(self, n_folds, prediction, labels, label_order):
        if n_folds == 1:
            return self.calculateAverageCurves(label_order, prediction[0], labels[0])
        else:
            return self.calculateCvCurves(label_order, prediction, labels)
            # n = len(label_order)
            # subtracted_predictions = map(lambda split: map(lambda probas: list(probas[i]-sum(probas[(i+j) % n] for j in range(1, n)) for i in range(n)), split), split_training_predictions)
            # training_rocs.append(self.calculateCvRocCurve(label_order, subtracted_predictions, split_modified_training_labels))
            # training_prcs.append(self.calculateCvPrcCurve(label_order, subtracted_predictions, split_modified_training_labels))
            # split_training_rocs.append(self.calculateSplitRocs(label_order, split_training_predictions, rolled_split_modified_training_labels))
            # split_training_prcs.append(self.calculateSplitPrcs(label_order, split_training_predictions, rolled_split_modified_training_labels))

    def start(self):
        split_data, split_labels = self.splitTrainingData()
        training_rocs = []
        training_prcs = []
        thresholds = []
        testing_rocs = []
        testing_prcs = []
        # split_training_rocs = []
        # split_training_prcs = []
        # split_thresholds = []
        # split_testing_rocs = []
        # split_testing_prcs = []
        training_confusion_matrices = 0.0
        testing_confusion_matrices = 0.0
        n_thresholds = 1
        training_threshold_confusion_matrices = [0.0 for _ in range(n_thresholds)]
        testing_threshold_confusion_matrices = [0.0 for _ in range(n_thresholds)]
        if self.t_use_maf_on_features:
            split_data = map(lambda x: self.applyMovingAverage(x, self.t_feature_maf), split_data)
            split_labels = np.array(self.modifySplitLabels(self.t_use_maf_on_features, split_labels))
        if self.t_remove_samples_features:
            split_data, split_labels = self.removeSamplesBeforeAfterClassChange(split_data, split_labels)
        if self.t_use_maf_on_probas:
            split_labels_proba = self.modifySplitLabels(self.t_use_maf_on_probas, split_labels)
        else:
            split_labels_proba = split_labels
        assert len(split_data) > 1
        # label_order1 = sorted(set(split_labels[0]))
        # split_class_count = map(lambda x: self.countClasses([1,2,3], x), split_labels_proba)
        for test_data_index in range(len(split_data)):
            split_training_data = self.allExceptOne(split_data, test_data_index)
            split_training_labels = self.allExceptOne(split_labels, test_data_index)
            split_training_labels_proba = self.allExceptOne(split_labels_proba, test_data_index)
            # split_training_class_count = self.allExceptOne(split_class_count, test_data_index)
            training_data = np.concatenate(split_training_data, 0)
            training_labels = np.concatenate(split_training_labels, 0)
            testing_data = split_data[test_data_index]
            testing_labels = split_labels[test_data_index]
            testing_labels_proba = split_labels_proba[test_data_index]
            # label_converter = self.getLabelConverter(label_order)
            # rolled_split_modified_training_labels = self.rollLabels(label_converter, split_modified_training_labels)
            n_folds = len(split_training_data)
            tr_prediction = self.calculateTrainingFeatures(n_folds, self.cv_model, split_training_data, split_training_labels)
            if self.t_remove_samples_probas:
                tr_prediction, split_training_labels_proba = self.removeSamplesBeforeAfterClassChange(tr_prediction, split_training_labels_proba)
            label_order = self.getLabelOrder(self.cv_model)
            training_roc, training_prc = self.calculateCurves(
                n_folds,
                tr_prediction,
                split_training_labels_proba,
                label_order
            )
            training_prcs.append(training_prc)
            training_rocs.append(training_roc)
            testing_prediction = self.calculateTestingFeatures(self.cv_model, testing_data)
            if self.t_remove_samples_probas:
                testing_prediction, testing_labels_proba = self.removeSamplesBeforeAfterClassChange([testing_prediction], [testing_labels_proba])
                testing_prediction, testing_labels_proba = testing_prediction[0], testing_labels_proba[0]
            testing_roc, testing_prc = self.calculateAverageCurves(label_order, testing_prediction, testing_labels_proba)
            testing_rocs.append(testing_roc)
            testing_prcs.append(testing_prc)
            # string_training_labels = map(str, np.concatenate(split_training_labels_proba, 0))
            # optimisation_function_lambda = lambda x, y: self.optimisationFunction(x, y, np.concatenate(tr_prediction, 0), string_training_labels, label_order)
            current_thresholds = training_prcs[-1].calculateThresholds(self.itr_calculator, self.itr_calculator2)
            thresholds.append(current_thresholds)
            # split_current_thresholds = self.calculateSplitThresholds(split_training_prcs)

            if self.t_use_ml:
                training_confusion_matrices += sklearn.metrics.confusion_matrix(training_labels, self.cv_model.predict(training_data), labels=label_order)
                testing_confusion_matrices += sklearn.metrics.confusion_matrix(testing_labels, self.cv_model.predict(testing_data), labels=label_order)
            # model = AdaBoostClassifier(n_estimators=50)
            # model.fit(training_prediction, training_labels[1:-1])
            # training_confusion_matrices += sklearn.metrics.confusion_matrix(training_labels[1:-1], model.predict(training_prediction), labels=label_order)
            # testing_confusion_matrices += sklearn.metrics.confusion_matrix(testing_labels[1:-1], model.predict(testing_prediction), labels=label_order)
            for i in range(n_thresholds):
                # training_threshold_confusion_matrices[i] += self.getThresholdConfusionMatrix(self.cv_model.thresholdPredict(training_prediction, current_thresholds, i/10.0), map(str, modified_training_labels), label_order)
                testing_threshold_confusion_matrices[i] += self.getThresholdConfusionMatrix(self.cv_model.thresholdPredict(testing_prediction, current_thresholds, i/10.0), map(str, testing_labels_proba), label_order)
                # split_testing_threshold_confusion_matrices[i] += self.getThresholdConfusionMatrix(self.cv_model.splitThresholdPredict(testing_prediction, split_current_thresholds, i/10.0), map(str, modified_testing_labels), label_order)

            # self.plotAllChanges(self.cv_model.predictProba(training_data), modified_training_labels, current_thresholds)
        #     self.plotAllChanges(self.cv_model.predictProba(testing_data), modified_testing_labels, current_thresholds)
        #     plt.draw()
        # plt.show()
        #
        # self.cv_model.fit(np.concatenate(split_data, 0), np.concatenate(split_labels, 0))
        threshold = np.mean(thresholds, 0)
        testing_prc = CvCurves.PrecisionRecallCvCurve(label_order)
        testing_roc = CvCurves.RocCvCurve(label_order)
        testing_prc.calculateFromCurves(testing_prcs)
        testing_roc.calculateFromCurves(testing_rocs)

        print self.calculateAccuracy(training_confusion_matrices)
        print training_confusion_matrices
        print self.calculateAccuracy(testing_confusion_matrices)
        print testing_confusion_matrices
        for i in range(n_thresholds):
            print i
            print training_threshold_confusion_matrices[i]
            self.printConfusionMatrixData(testing_threshold_confusion_matrices[i])
            # print self.calculateAccuracyIgnoringLastColumn(split_testing_threshold_confusion_matrices[i])
            # print split_testing_threshold_confusion_matrices[i]

        # dummy_model = CvCalibrationModel.TrainingModel()
        # dummy_model.setup(self.features_to_use, 1, self.recordings, [False])
        # features, labels = dummy_model.getConcatenatedMatrix(self.validation_recordings)
        # self.plotAllChanges(features, labels)
        # plt.show()

        # self.training_data = training_data
        # self.training_labels = training_labels
        # self.testing_data = testing_data
        # self.testing_labels = testing_labels
        self.thresholds = threshold
        self.min_max = self.cv_model.getMinMax()
        self.lda_model = None  # self.model.model
        self.training_prc = training_prcs
        self.testing_prc = testing_prc
        self.training_roc = training_rocs
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
