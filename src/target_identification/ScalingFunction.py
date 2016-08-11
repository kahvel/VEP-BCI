import target_identification.ColumnsIterator


class ScalingFunctions(object):
    def __init__(self):
        self.minima = None
        self.maxima = None
        self.scaling_functions = None

    def setup(self, *args):
        raise NotImplementedError("setup not implemented!")

    def __getitem__(self, item):
        return self.scaling_functions[item]

    def getScalingFunction(self, minimum, maximum):
        return lambda x: (x-minimum)/(maximum-minimum)+1

    def getScalingFunctions(self, minima, maxima, extraction_method_names):
        return {method: self.getScalingFunction(minima[method], maxima[method]) for method in extraction_method_names}


class TrainingScalingFunctions(ScalingFunctions):
    def __init__(self):
        ScalingFunctions.__init__(self)

    def setup(self, extraction_method_names, recordings):
        min_max_finder = MinMaxFinder(extraction_method_names)
        self.minima = min_max_finder.findMin(recordings)
        self.maxima = min_max_finder.findMax(recordings)
        self.scaling_functions = self.getScalingFunctions(self.minima, self.maxima, extraction_method_names)


class OnlineScalingFunctions(ScalingFunctions):
    def __init__(self):
        ScalingFunctions.__init__(self)

    def setup(self, minima, maxima, extraction_method_names):
        self.scaling_functions = self.getScalingFunctions(self.minima, self.maxima, extraction_method_names)


class MinMaxFinder(target_identification.ColumnsIterator.ColumnsIterator):
    def __init__(self, extraction_method_names):
        target_identification.ColumnsIterator.ColumnsIterator.__init__(self)
        self.extraction_method_names = extraction_method_names

    def findMin(self, recordings):
        return self.findExtremum(min, recordings)

    def findMax(self, recordings):
        return self.findExtremum(max, recordings)

    def findExtremum(self, function, recordings):
        extrema = {method: [] for method in self.extraction_method_names}
        for recording in recordings:
            for method, column in self.iterateColumns(recording.getColumnsAsFloats(recording.data), self.extraction_method_names):
                extrema[method].append(function(column))
        return {method: function(extrema[method]) for method in self.extraction_method_names}
