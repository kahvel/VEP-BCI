import numpy as np


class DataCollector(object):
    def __init__(self, sample_count):
        self.collected_samples = []
        self.sample_count = sample_count

    def addingCondition(self, previous_labels):
        raise NotImplementedError("addingCondition not implemented!")

    def enoughSamplesToCombine(self):
        return len(self.collected_samples) == self.sample_count

    def combineSamples(self, previous_labels):
        if self.enoughSamplesToCombine():
            if self.addingCondition(previous_labels):
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

    def handleSample(self, sample, previous_labels=None):
        self.removeFirstSample()
        self.addLastSample(sample)
        return self.combineSamples(previous_labels)


class OnlineCollector(DataCollector):
    def __init__(self, sample_count):
        DataCollector.__init__(self, sample_count)

    def addingCondition(self, previous_labels):
        return True

    def processCollectedSamples(self, collected_samples):
        return np.concatenate(self.collected_samples)


class AbstractTrainingCollector(DataCollector):
    def __init__(self, sample_count):
        DataCollector.__init__(self, sample_count)
        self.result = []

    def addingCondition(self, labels):
        return all(map(lambda x: x == labels[0], labels))

    def getResult(self):
        return np.array(self.result)


class TrainingLabelCollector(AbstractTrainingCollector):
    def __init__(self, sample_count):
        AbstractTrainingCollector.__init__(self, sample_count)

    def processCollectedSamples(self, collected_samples):
        return self.result.append(collected_samples[0])


class TrainingFeatureCollector(AbstractTrainingCollector):
    def __init__(self, sample_count):
        AbstractTrainingCollector.__init__(self, sample_count)

    def processCollectedSamples(self, collected_samples):
        return self.result.append(np.concatenate(self.collected_samples))


class TrainingCollector(object):
    def __init__(self, sample_count):
        self.label_collector = TrainingLabelCollector(sample_count)
        self.feature_collector = TrainingFeatureCollector(sample_count)

    def handleSample(self, features, label):
        previous_labels = self.label_collector.getCollectedSamples()
        self.label_collector.handleSample(label, previous_labels)
        self.feature_collector.handleSample(features, previous_labels)

    def combineSamples(self, features, labels):
        for feature, label in zip(features, labels):
            self.handleSample(feature, label)
        return self.feature_collector.getResult(), self.label_collector.getResult()
