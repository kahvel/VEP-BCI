import constants as c


class Bci(object):
    def __init__(self): pass

    def startBciEvent(self): pass

    def stopBciEvent(self): pass

    def setupBciEvent(self): pass

    def saveBciEvent(self): pass

    def loadBciEvent(self): pass

    def exitBciEvent(self): pass

    def saveBciSettingsEvent(self, file): pass

    def loadBciSettingsEvent(self, file): pass


class Recording(object):
    def __init__(self): pass

    def saveEegEvent(self, directory): pass

    def loadEegEvent(self, directory): pass


class Results(object):
    def __init__(self): pass

    def resultsReceivedEvent(self, results): pass

    def newResultsReceivedEvent(self, new_results): pass

    def recordedEegReceivedEvent(self, eeg): pass

    def recordedFeaturesReceivedEvent(self, features): pass

    def recordedFrequenciesReceivedEvent(self, frequencies): pass


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

    def trialEndedEvent(self): pass


class MessageDown(object):
    def __init__(self):
        pass

    def sendEventToChildren(self, function):
        raise NotImplementedError("sendEventToChildren not implemented!")


class Leaf(MessageDown):
    def __init__(self):
        MessageDown.__init__(self)

    def sendEventToChildren(self, function):
        function(self)


class NonLeaf(MessageDown):
    def __init__(self, widgets_list):
        MessageDown.__init__(self)
        self.widgets_list = widgets_list

    def sendEventToChildren(self, function):
        message = function(self)
        if not message == c.STOP_EVENT_SENDING:
            for widget in self.widgets_list:
                widget.sendEventToChildren(function)


class MessageUp(object):
    def __init__(self):
        pass

    def sendEventToRoot(self, function, needs_stopped_state=False):
        raise NotImplementedError("sendEventToRoot not implemented!")


class NonRoot(MessageUp):
    def __init__(self, parent):
        MessageUp.__init__(self)
        self.parent = parent

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.parent.sendEventToRoot(function, needs_stopped_state)


class Root(MessageUp, NonLeaf):
    def __init__(self, widgets_list, post_office_message_handler):
        MessageUp.__init__(self)
        NonLeaf.__init__(self, widgets_list)
        self.post_office_message_handler = post_office_message_handler

    def bciIsStopped(self):
        return self.post_office_message_handler.isStopped()

    def sendEventToRoot(self, function, needs_stopped_state=False):
        if needs_stopped_state and self.bciIsStopped() or not needs_stopped_state:
            self.sendEventToChildren(function)
        else:
            print "BCI has to be stopped to use this functionality!"


class Widget(NonRoot, Leaf, MessagingInterface):
    def __init__(self, parent):
        NonRoot.__init__(self, parent)
        Leaf.__init__(self)


class Frame(NonRoot, NonLeaf, MessagingInterface):
    def __init__(self, parent, widgets_list):
        NonRoot.__init__(self, parent)
        NonLeaf.__init__(self, widgets_list)
