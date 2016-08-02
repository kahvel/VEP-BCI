

class MessagingInterface(object):
    def __init__(self): pass

    def targetAdded(self): pass

    def targetRemoved(self, deleted_tab): pass

    def targetDisabled(self, tabs, current_tab): pass

    def targetEnabled(self, tabs, current_tab): pass

    def trialEnded(self): pass

    def saveEegEvent(self, file): pass

    def loadEegEvent(self, file): pass

    def resetEegEvent(self): pass

    def sendEventToRoot(self, function):
        raise NotImplementedError("sendEventToRoot not implemented!")


class MessagingInterfaceChild(MessagingInterface):
    def __init__(self, parent):
        MessagingInterface.__init__(self)
        self.parent = parent

    def sendEventToRoot(self, function):
        self.parent.sendEventToRoot(function)


class MessagingInterfaceRoot(MessagingInterface):
    def __init__(self):
        MessagingInterface.__init__(self)
