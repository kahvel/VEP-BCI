import AbstractMessageSenders


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

    def resultsReceivedEvent(self, results): pass

    def recordedEegReceivedEvent(self, eeg): pass

    def recordedFeaturesReceivedEvent(self, features): pass

    def recordedFrequenciesReceivedEvent(self, frequencies): pass

    def addNewRecordingTabEvent(self): pass

    def addNewRecordingCheckbuttonEvent(self): pass

    def addNewRecordingOptionEvent(self): pass

    def getRecordingNotebookWidgetsEvent(self): pass

    def sendRecordingNotebookWidgetsEvent(self, recording_notebook_widgets): pass


class Classification(object):
    def __init__(self): pass

    def sendChosenModelNumber(self, model_number): pass  # Currently not used

    def getChosenModelNumber(self): pass  # Currently not used


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


class Models(object):
    def __init__(self): pass

    def addNewModelTabEvent(self): pass

    def modelTabRemovedEvent(self, deleted_tab): pass

    def modelReceivedEvent(self, model): pass

    def secondModelReceivedEvent(self, model): pass

    def validationDataReceivedEvent(self, validation_data): pass

    def validationLabelsReceivedEvent(self, validation_labels): pass

    def trainingDataReceivedEvent(self, training_data): pass

    def trainingLabelsReceivedEvent(self, training_labels): pass

    def minMaxReceivedEvent(self, min_max): pass

    def thresholdsReceivedEvent(self, thresholds): pass

    def trainingRocReceivedEvent(self, training_roc): pass

    def validationRocReceivedEvent(self, validation_roc): pass

    def saveModelEvent(self, directory): pass

    def loadModelEvent(self, directory): pass

    def trainButtonClickedEvent(self): pass

    def sendFeaturesToRootEvent(self, results): pass

    def sendEegToRootEvent(self, results): pass

    def getFeaturesEvent(self): pass

    def getEegEvent(self): pass

    def sendModelOptionsToRootEvent(self, options): pass

    def getModelOptionsEvent(self): pass

    def disableModelOptionsEvent(self): pass

    def usedFeaturesReceivedEvent(self, used_features): pass


class TrialEndedHandler(object):
    def __init__(self): pass

    def trialEndedEvent(self): pass


class TrainingEndedHandler(object):
    def __init__(self): pass

    def trainingEndedEvent(self): pass

    def newRecordingCheckbuttonEvent(self): pass

    def newRecordingOptionEvent(self): pass


class MessagingInterface(Bci, Recording, Robot, Targets, Classification, Models, TrialEndedHandler, TrainingEndedHandler):
    def __init__(self):
        Bci.__init__(self)
        Recording.__init__(self)
        Robot.__init__(self)
        Targets.__init__(self)
        Classification.__init__(self)
        Models.__init__(self)
        TrialEndedHandler.__init__(self)
        TrainingEndedHandler.__init__(self)


class FrameMessageHandler(MessagingInterface, AbstractMessageSenders.Frame):
    def __init__(self, parent, widgets_list):
        MessagingInterface.__init__(self)
        AbstractMessageSenders.Frame.__init__(self, parent, widgets_list)


class WidgetMessageHandler(MessagingInterface, AbstractMessageSenders.Widget):
    def __init__(self, parent):
        MessagingInterface.__init__(self)
        AbstractMessageSenders.Widget.__init__(self, parent)
