

class ListByTrials(object):
    def __init__(self):
        self.list = []

    def reset(self):
        self.list = []

    def add(self, *args):
        raise NotImplementedError("add not implemented!")

    def setup(self, *args):
        if not self.previousTrialEmpty(*args):
            self.list.append(self.getTrialCollection(*args))

    def getTrialCollection(self, *args):
        raise NotImplementedError("getTrialCollection not implemented!")

    def previousTrialEmpty(self, *args):
        return len(self.list) != 0 and self.trialEmpty(self.list[-1], *args)

    def trialEmpty(self, trial, *args):
        return trial == self.getTrialCollection(*args)
