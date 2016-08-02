

class Bci(object):
    def __init__(self): pass

    def startBciEvent(self): pass

    def stopBciEvent(self): pass

    def setupBciEvent(self): pass

    def saveBciEvent(self): pass

    def loadBciEvent(self): pass

    def exitBciEvent(self): pass


class Recording(object):
    def __init__(self): pass

    def saveEegEvent(self, file): pass

    def loadEegEvent(self, file): pass

    def resetEegEvent(self): pass


class Results(object):
    def __init__(self): pass

    def saveResultsEvent(self): pass

    def showResultsEvent(self): pass

    def resetResultsEvent(self): pass


class Robot(object):
    def __init__(self): pass

    def robotForwardEvent(self): pass

    def robotBackwardEvent(self): pass

    def robotLeftEvent(self): pass

    def robotRightEvent(self): pass

    def robotStopEvent(self): pass


class MessagingInterface(Bci, Recording, Results, Robot):
    def __init__(self):
        Bci.__init__(self)
        Recording.__init__(self)
        Results.__init__(self)
        Robot.__init__(self)

    def targetAdded(self): pass

    def targetRemoved(self, deleted_tab): pass

    def targetDisabled(self, tabs, current_tab): pass

    def targetEnabled(self, tabs, current_tab): pass

    def trialEnded(self): pass

    def sendEventToRoot(self, function, needs_stopped_state=False):
        raise NotImplementedError("sendEventToRoot not implemented!")


class MessagingInterfaceChild(MessagingInterface):
    def __init__(self, parent):
        MessagingInterface.__init__(self)
        self.parent = parent

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.parent.sendEventToRoot(function)
