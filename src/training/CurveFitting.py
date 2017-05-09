import numpy as np
import matplotlib2tikz
import matplotlib.pyplot as plt


class CurveFitting(object):
    def extendThresholdsValues(self, thresholds):
        min = thresholds[0]
        max = thresholds[-1]
        range = (max-min)*0.2
        return [min-range, max+range]

    def extendThresholds(self, all_thresholds):
        return [np.insert(thresholds, [0, len(thresholds)-1], self.extendThresholdsValues(thresholds)) for thresholds in all_thresholds]

    def extendYValuesHelper(self, values):
        first = values[0]
        last = values[-1]
        return [first, last]

    def extendYValues(self, y_values):
        return [np.insert(values, [0, len(values)-1], self.extendYValuesHelper(values)) for values in y_values]

    def plotCurves(self, thresholds, precisions, precision_function, predictions, prediction_function, precision_derivative, prediction_derivative):
        import time
        points = np.linspace(thresholds[0], thresholds[-1], 3000)
        plt.figure()
        plt.ylim(0, 1.1)
        plt.plot(thresholds, precisions)
        plt.plot(points, precision_function(points))
        matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")
        plt.figure()
        plt.plot(thresholds, predictions)
        plt.plot(points, prediction_function(points))
        matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + "1.tex")
        plt.figure()
        plt.plot(points, precision_derivative(points))
        plt.plot(points, prediction_derivative(points))

    def makeFunction(self, coefficients):
        return lambda x: sum(p*x**(len(coefficients)-1-i) for i, p in enumerate(coefficients))

    def makeDerivative(self, coefficient):
        return lambda x: sum(p*x**(len(coefficient[:-1])-1-i)*(len(coefficient)-1-i) for i, p in enumerate(coefficient[:-1]))

    def fitCurves(self, thresholds, precisions, predictions):
        precision_coefficients = [
            np.polyfit(threshold, precision, deg=7)
            for threshold, precision in zip(thresholds, precisions)
        ]
        prediction_coefficients = [
            np.polyfit(threshold, relative_prediction, deg=7)
            for threshold, relative_prediction in zip(thresholds, predictions)
        ]
        precision_functions = [
            self.makeFunction(coefficient)
            for coefficient in precision_coefficients
        ]
        prediction_functions = [
            self.makeFunction(coefficient)
            for coefficient in prediction_coefficients
        ]
        precision_derivative = [
            self.makeDerivative(coefficient)
            for coefficient in precision_coefficients
        ]
        prediction_derivative = [
            self.makeDerivative(coefficient)
            for coefficient in prediction_coefficients
        ]
        return precision_functions, prediction_functions, precision_derivative, prediction_derivative

    def calculatePrecisionPredictionCurves(self, all_thresholds, all_precisions, all_relative_predictions):
        extended_thresholds = self.extendThresholds(all_thresholds)
        extended_precisions = self.extendYValues(all_precisions)
        extended_prediction = self.extendYValues(all_relative_predictions)
        precision_functions, prediction_functions, precision_derivative, prediction_derivative = self.fitCurves(extended_thresholds, extended_precisions, extended_prediction)
        # precision_functions1, prediction_functions1, precision_derivative1, prediction_derivative1 = self.fitCurves(all_thresholds, all_precisions, all_relative_predictions)
        # class_index = 0
        # self.plotCurves(all_thresholds[class_index], all_precisions[class_index], precision_functions[class_index], all_relative_predictions[class_index], prediction_functions[class_index], precision_derivative[class_index], prediction_derivative[class_index])
        # raw_input()
        # self.plotCurves(all_thresholds[class_index], all_precisions[class_index], precision_functions1[class_index], all_relative_predictions[class_index], prediction_functions1[class_index], precision_derivative1[class_index], prediction_derivative1[class_index])
        # plt.show()
        return precision_functions, prediction_functions, precision_derivative, prediction_derivative