

class ListByTrials(object):
    def __init__(self):
        self.list = []

    def reset(self):
        self.list = []

    def add(self, *args):
        raise NotImplementedError("add not implemented!")

    def setup(self, *args):
        self.list.append(self.getTrialCollection(args))

    def getTrialCollection(self, *args):
        raise NotImplementedError("getTrialCollection not implemented!")
