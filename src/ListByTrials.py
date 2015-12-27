

class ListByTrials(object):
    def __init__(self):
        self.list = []
        self.start_new_trial = True

    def reset(self):
        self.list = []
        self.start_new_trial = True

    def add(self, *args):
        raise NotImplementedError("add not implemented!")

    def setup(self, *args):
        if self.start_new_trial:
            self.list.append(self.getTrialCollection(*args))
            self.start_new_trial = False

    def getTrialCollection(self, *args):
        raise NotImplementedError("getTrialCollection not implemented!")

    def trialEnded(self, *args):
        self.start_new_trial = True
