import constants as c


class Bci(object):
    def __init__(self): pass

    def startButtonClickedEvent(self): pass

    def stopButtonClickedEvent(self): pass

    def setupButtonClickedEvent(self): pass

    def saveButtonClickedEvent(self): pass

    def loadButtonClickedEvent(self): pass

    def exitButtonClickedEvent(self): pass

    def saveBciSettingsEvent(self, file): pass

    def loadBciSettingsEvent(self, file): pass


class Recording(object):
    def __init__(self): pass

    def saveEegEvent(self, directory): pass

    def loadEegEvent(self, directory): pass

    def recordTabRemovedEvent(self, deleted_tab): pass

    def getRecordingNotebookWidgetsEvent(self): pass

    def sendRecordingNotebookWidgetsEvent(self, recording_notebook_widgets): pass


class Results(object):
    def __init__(self): pass

    def resultsReceivedEvent(self, results): pass

    def newResultsReceivedEvent(self, new_results): pass

    def recordedEegReceivedEvent(self, eeg): pass

    def recordedFeaturesReceivedEvent(self, features): pass

    def recordedFrequenciesReceivedEvent(self, frequencies): pass

    def addNewRecordingTabEvent(self): pass


class Classification(object):
    def __init__(self): pass

    def trainButtonClickedEvent(self): pass

    def sendFeaturesToRootEvent(self, results): pass

    def getFeaturesEvent(self): pass

    def sendClassificationOptionsToRootEvent(self, features_to_use): pass

    def getClassificationOptionsEvent(self): pass


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

    def monitorFrequencyChangedEvent(self): pass

    def getTargetNotebookWidgetsEvent(self): pass

    def sendTargetNotebookWidgetsEvent(self, target_notebook_widgets): pass


class Training(object):
    def __init__(self): pass

    def addNewModelTabEvent(self): pass

    def modelTabRemovedEvent(self): pass

    def modelReceivedEvent(self, model): pass

    def saveModelEvent(self, directory): pass

    def loadModelEvent(self, directory): pass


class MessagingInterface(Bci, Recording, Results, Robot, Targets, Classification, Training):
    def __init__(self):
        Bci.__init__(self)
        Recording.__init__(self)
        Results.__init__(self)
        Robot.__init__(self)
        Targets.__init__(self)
        Classification.__init__(self)
        Training.__init__(self)

    def trialEndedEvent(self): pass

    def trainingEndedEvent(self): pass


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

    def sendEventToAll(self, function, needs_stopped_state=False):
        self.parent.sendEventToAll(function, needs_stopped_state)


class Root(MessageUp, NonLeaf):
    def __init__(self, widgets_list, post_office_message_handler):
        MessageUp.__init__(self)
        NonLeaf.__init__(self, widgets_list)
        self.post_office_message_handler = post_office_message_handler

    def bciIsStopped(self):
        return self.post_office_message_handler.isStopped()

    def checkIfStopped(self, function, needs_stopped_state):
        if needs_stopped_state and self.bciIsStopped() or not needs_stopped_state:
            function()
        else:
            print "BCI has to be stopped to use this functionality!"

    def sendEventToRoot(self, function, needs_stopped_state=False):
        self.checkIfStopped(lambda: function(self), needs_stopped_state)

    def sendEventToAll(self, function, needs_stopped_state=False):
        self.checkIfStopped(lambda: self.sendEventToChildren(function), needs_stopped_state)


class Widget(NonRoot, Leaf, MessagingInterface):
    def __init__(self, parent):
        NonRoot.__init__(self, parent)
        Leaf.__init__(self)


class Frame(NonRoot, NonLeaf, MessagingInterface):
    def __init__(self, parent, widgets_list):
        NonRoot.__init__(self, parent)
        NonLeaf.__init__(self, widgets_list)
