import constants as c


class ResultsParser(object):
    def __init__(self, add_sum=True, data_has_method=False):
        self.data = None
        self.parse_result = {}
        self.add_sum = add_sum
        self.data_has_method = data_has_method

    def setup(self, data):
        self.data = data

    def parseSensorResults(self, parse_result, results, data):
        for sensor in results:
            # if sensor in data:  # Currently data does not contain sensors??
                self.parseHarmonicResults(self.parseResultValue(parse_result, sensor), results[sensor], data)

    def parseHarmonicResults(self, parse_result, results, data):
        for harmonic in results:
            if harmonic in data:
                self.parseFrequencyResults(self.parseResultValue(parse_result, harmonic), results[harmonic], data[harmonic])

    def parseFrequencyResults(self, parse_result, result, data):
        raise NotImplementedError("parseFrequencyResult not implemented!")

    def parseResultValue(self, parse_result, key):
        if key not in parse_result:
            parse_result[key] = {}
        return parse_result[key]

    def parseResults(self, results):
        for tab in results:
            for method in results[tab]:
                if tab in self.data:
                    parse_result = self.parseResultValue(self.parse_result, tab)
                    parse_result = self.parseResultValue(parse_result, method)
                    if self.data_has_method:
                        data = self.data[tab][method]
                    else:
                        data = self.data[tab]
                    if method[0] == c.CCA or method[0] == c.LRT:
                        if self.add_sum:
                            self.parseHarmonicResults(parse_result, {c.RESULT_SUM: results[tab][method]}, data)
                        else:
                            self.parseHarmonicResults(parse_result, results[tab][method], data)
                    elif method[0] == c.SUM_PSDA:
                        self.parseHarmonicResults(parse_result, results[tab][method], data)
                    elif method[0] == c.PSDA:
                        self.parseSensorResults(parse_result, results[tab][method], data)
                    elif method[0] == c.MEC:
                        self.parseHarmonicResults(parse_result, results[tab][method], data)
        return self.parse_result

    def parseResultsNewDict(self, results):
        self.parse_result = {}
        return self.parseResults(results)


class WeightFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            # total = result[0][1]/sum(map(lambda x: x[1], result))*data
            if result[0][0] in parse_result:
                parse_result[result[0][0]] += data
            else:
                parse_result[result[0][0]] = data

    def parseResultValue(self, parse_result, key):
        return parse_result


class DifferenceFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)
        self.comparison = []

    def parseResultsNewDict(self, results):
        self.comparison = []
        return ResultsParser.parseResultsNewDict(self, results)

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) > 1:  # If we have at least 2 targets in the result dict
            difference = result[0][1]-result[1][1]
            parse_result[result[0][0], result[1][0]] = difference
            self.comparison.append(difference >= data)


class RatioFinder(ResultsParser):
    def __init__(self):
        ResultsParser.__init__(self)

    def parseFrequencyResults(self, parse_result, result, data):
        if len(result) != 0:
            for frequency, value in result:
                processed_value = self.getValue(value, result, data, frequency)
                parse_result[frequency] = processed_value

    def getValue(self, value, result, data, frequency):
        results_sum = sum(map(lambda x: data(x), dict(result).values()))
        return data(value)/results_sum


def getMethodFromFeature(feature):
    return "_".join(feature.split("_")[:-1])


class Flattener(object):
    def __init__(self):
        pass

    def getFeaturesByFrequencies(self, getKey, frequency_results):
        return {getKey(frequency): frequency_results[frequency] for frequency in frequency_results}

    def combineKeys(self, tab, method, sensors, harmonic, frequency, sensor):
        return str(tab) + "_" + str(sensor) + "_" + str(method) + "_" + str(sensors) + "_" + str(harmonic) + "_" + str(frequency)

    def combineKeysLambda(self, tab, method, sensors, harmonic, sensor):
        return lambda frequency: self.combineKeys(tab, method, sensors, harmonic, frequency, sensor)

    def parseFrequencyResults(self, tab, method, sensors, harmonic, frequency_results, sensor):
        getKey = self.combineKeysLambda(tab, method, sensors, harmonic, sensor)
        return self.getFeaturesByFrequencies(getKey, dict(frequency_results))

    def parseHarmonicResults(self, tab, method, sensors, harmonic_results, sensor):
        flattened = {}
        for harmonic in harmonic_results:
            flattened.update(self.parseFrequencyResults(tab, method, sensors, harmonic, harmonic_results[harmonic], sensor))
        return flattened

    def parseSensorResults(self, tab, method, sensors, sensor_results):
        flattened = {}
        for sensor in sensor_results:
            flattened.update(self.parseHarmonicResults(tab, method, sensors, sensor_results[sensor], sensor))
        return flattened

    def parseFeatures(self, features):
        parse_result = {}
        for tab in sorted(features):
            for method, sensors in features[tab]:
                if method == c.CCA or method == c.LRT:
                    parse_result.update(self.parseFrequencyResults(tab, method, sensors, c.RESULT_SUM, features[tab][method, sensors], str(sensors)))
                elif method == c.SUM_PSDA or method == c.MEC:
                    parse_result.update(self.parseHarmonicResults(tab, method, sensors, features[tab][method, sensors], str(sensors)))
                elif method == c.PSDA or method == c.WAVELET:
                    parse_result.update(self.parseSensorResults(tab, method, sensors, features[tab][method, sensors]))
        return parse_result
