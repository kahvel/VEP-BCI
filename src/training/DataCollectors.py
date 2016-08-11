import numpy as np


class AbstractDataCollector(object):
    def __init__(self):
        pass

    def handleSample(self, *sample):
        raise NotImplementedError("handleSample not implemented!")


class DataCollector(AbstractDataCollector):
    def __init__(self, sample_count):
        AbstractDataCollector.__init__(self)
        self.collected_samples = []
        self.sample_count = sample_count

    def addingCondition(self):
        raise NotImplementedError("addingCondition not implemented!")

    def enoughSamplesToCombine(self):
        return len(self.collected_samples) == self.sample_count

    def combineSamples(self):
        if self.enoughSamplesToCombine():
            if self.addingCondition():
                return self.processCollectedSamples(self.collected_samples)

    def processCollectedSamples(self, collected_samples):
        raise NotImplementedError("processCollectedSamples not implemented!")

    def removeFirstSample(self):
        if self.enoughSamplesToCombine():
            del self.collected_samples[0]

    def addLastSample(self, sample):
        self.collected_samples.append(sample)

    def getCollectedSamples(self):
        return self.collected_samples


class OnlineCollector(DataCollector):
    def __init__(self, sample_count):
        DataCollector.__init__(self, sample_count)

    def addingCondition(self):
        return True

    def processCollectedSamples(self, collected_samples):
        return np.concatenate(self.collected_samples)

    def handleSample(self, sample):
        combined_sample = self.combineSamples()
        self.removeFirstSample()
        self.addLastSample(sample)
        return combined_sample


class AbstractTrainingCollector(DataCollector):
    def __init__(self, sample_count):
        DataCollector.__init__(self, sample_count)
        self.collected_labels = None
        self.result = []

    def setCollectedLabels(self, collected_labels):
        self.collected_labels = collected_labels

    def addingCondition(self):
        return all(map(lambda x: x == self.collected_labels[0], self.collected_labels))

    def addToResult(self, combined_sample):
        if combined_sample is not None:
            self.result.append(combined_sample)

    def handleSample(self, sample):
        combined_sample = self.combineSamples()
        self.removeFirstSample()
        self.addLastSample(sample)
        self.addToResult(combined_sample)

    def getResult(self):
        return np.array(self.result)


class TrainingLabelCollector(AbstractTrainingCollector):
    def __init__(self, sample_count):
        AbstractTrainingCollector.__init__(self, sample_count)
        self.setCollectedLabels(self.collected_samples)

    def processCollectedSamples(self, collected_samples):
        return collected_samples[0]


class TrainingFeatureCollector(AbstractTrainingCollector):
    def __init__(self, sample_count, label_collector):
        AbstractTrainingCollector.__init__(self, sample_count)
        self.setCollectedLabels(label_collector.getCollectedSamples())

    def processCollectedSamples(self, collected_samples):
        return np.concatenate(self.collected_samples)


class TrainingCollector(AbstractDataCollector):
    def __init__(self, sample_count):
        AbstractDataCollector.__init__(self)
        self.label_collector = TrainingLabelCollector(sample_count)
        self.feature_collector = TrainingFeatureCollector(sample_count, self.label_collector)

    def handleSample(self, features, label):
        self.feature_collector.handleSample(features)  # Has to be before label_collector
        self.label_collector.handleSample(label)

    def combineSamples(self, features, labels):
        for feature, label in zip(features, labels):
            self.handleSample(feature, label)
        self.handleSample(feature, label)
        return self.feature_collector.getResult(), self.label_collector.getResult()


class TrainingCollector2(AbstractDataCollector):
    def __init__(self, sample_count):
        AbstractDataCollector.__init__(self)
        self.label_collector = TrainingLabelCollector(sample_count)
        self.feature_collector = TrainingFeatureCollector(sample_count, self.label_collector)

    def handleSample(self, features, label):
        self.feature_collector.handleSample(features)  # Has to be before label_collector
        self.label_collector.handleSample(label)

    def combineSamples(self, features, labels):
        for feature, label in zip(features, labels):
            self.handleSample(feature, label)
        self.handleSample(feature, label)
        return self.feature_collector.getResult(), self.label_collector.getResult()