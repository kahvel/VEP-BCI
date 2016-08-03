

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

    def resultsReceivedEvent(self, results): pass

    def newResultsReceivedEvent(self, new_results): pass


class Robot(object):
    def __init__(self): pass

    def robotForwardEvent(self): pass

    def robotBackwardEvent(self): pass

    def robotLeftEvent(self): pass

    def robotRightEvent(self): pass

    def robotStopEvent(self): pass


class Targets(object):
    def __init__(self): pass

    def targetAddedEvent(self): pass

    def targetRemovedEvent(self, deleted_tab): pass

    def targetDisabledEvent(self, tabs, current_tab): pass

    def targetEnabledEvent(self, tabs, current_tab): pass


class MessagingInterface(Bci, Recording, Results, Robot, Targets):
    def __init__(self):
        Bci.__init__(self)
        Recording.__init__(self)
        Results.__init__(self)
        Robot.__init__(self)
        Targets.__init__(self)

    def sendEventToRoot(self, function, needs_stopped_state=False):
        raise NotImplementedError("sendEventToRoot not implemented!")

    def sendEventToChildren(self, function):
        raise NotImplementedError("sendEventToChildren not implemented!")

    def trialEndedEvent(self): pass


class MessagingInterfaceWithParent(MessagingInterface):
    def __init__(self, parent):
        MessagingInterface.__init__(self)
        self.parent = parent

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.parent.sendEventToRoot(function, needs_stopped_state)


class WidgetMessagingInterface(MessagingInterfaceWithParent):
    def __init__(self, parent):
        MessagingInterfaceWithParent.__init__(self, parent)

    def sendEventToChildren(self, function):
        function(self)


class FrameMessagingInterface(MessagingInterfaceWithParent):
    def __init__(self, parent, widgets_list):
        MessagingInterfaceWithParent.__init__(self, parent)
        self.widgets_list = widgets_list

    def sendEventToChildren(self, function):
        function(self)
        for widget in self.widgets_list:
            widget.sendEventToChildren(function)
