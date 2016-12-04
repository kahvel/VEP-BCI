from parsers import FeaturesParser


class FeaturesHandler(object):
    def __init__(self):
        self.features_to_use = None
        self.extraction_method_names = None

    def setup(self, features_to_use):
        self.features_to_use = self.getFeaturesToUse(features_to_use)
        self.extraction_method_names = self.findExtractionMethodNames(self.features_to_use)
        # print self.features_to_use, self.extraction_method_names
        self.printWarningIfBadFeatures(features_to_use)

    def findExtractionMethodNames(self, features_to_use):
        return sorted(set(FeaturesParser.getMethodFromFeature(feature) for feature in features_to_use))

    def getFeaturesToUse(self, features_to_use):
        raise NotImplementedError("getFeaturesToUse not implemented!")

    def checkFeatures(self, features_to_use):
        raise NotImplementedError("checkFeatures not implemented!")

    def printWarningIfBadFeatures(self, features_to_use):
        if not self.checkFeatures(features_to_use):
            print "Recordings are missing features!"

    def getExtractionMethodNames(self):
        return self.extraction_method_names

    def getUsedFeatures(self):
        return self.features_to_use


class OnlineFeaturesHandler(FeaturesHandler):
    def __init__(self):
        FeaturesHandler.__init__(self)

    def getFeaturesToUse(self, features_to_use):
        return features_to_use

    def checkFeatures(self, features_to_use):
        return True


class TrainingFeaturesHandler(FeaturesHandler):
    def __init__(self, recordings):
        FeaturesHandler.__init__(self)
        self.recordings = recordings

    def getFeaturesToUse(self, features_to_use):
        if features_to_use is None:
            return self.getHeaderOfFirstRecording()
        else:
            return features_to_use

    def getHeaderOfFirstRecording(self):
        return self.recordings[0].getDataFileHeader()

    def allFeaturesInRecordings(self, features_to_use):
        return all(feature in recording.getDataFileHeader() for feature in features_to_use for recording in self.recordings)

    def allRecordingsSameFeatures(self):
        return all(self.getHeaderOfFirstRecording() == recording.getDataFileHeader() for recording in self.recordings)

    def checkFeatures(self, features_to_use):
        if features_to_use is None:
            return self.allRecordingsSameFeatures()
        else:
            return self.allFeaturesInRecordings(features_to_use)

