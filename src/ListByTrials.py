

class ListByTrials(object):
    def __init__(self):
        self.list = []
        self.current_data = None

    def reset(self):
        self.list = []

    def add(self, *args):
        raise NotImplementedError("add not implemented!")

    def start(self, *args):
        self.current_data = self.getTrialCollection(*args)

    def getTrialCollection(self, *args):
        raise NotImplementedError("getTrialCollection not implemented!")

    def trialEnded(self, *args):
        self.list.append(self.current_data)
