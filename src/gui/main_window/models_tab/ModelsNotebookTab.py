from gui_elements.widgets import Buttons, Textboxes
from gui_elements.widgets.frames import Frame, AddingCheckbuttonsFrame
from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import constants as c

import matplotlib.pyplot as plt
import os
import pickle
import numpy as np


class ModelsNotebookTab(DisableDeleteNotebookTab.Delete):
    def __init__(self, parent, deleteTab, **kwargs):
        DisableDeleteNotebookTab.Delete.__init__(self, parent, c.MODELS_NOTEBOOK_TAB, **kwargs)
        self.addChildWidgets((
            OptionsFrame(self, 0, 0, columnspan=4),
            ModelFrame(self, 1, 0, columnspan=4),
            Textboxes.TimestampTextbox(self, 2, 0),
            Textboxes.DirectoryTextbox(self, 3, 0),
            SaveButton(self, 4, 0),
            self.getDeleteButton(4, 1, deleteTab)
        ))

    def saveModelEvent(self, directory):
        if self.saveMe():
            file = open(os.path.join(directory, "results.txt"), "w")
            self.sendEventToChildren(lambda x: x.saveBciSettingsEvent(file))
        else:
            return c.STOP_EVENT_SENDING

    def saveMe(self):
        return self.widgets_dict[c.MODELS_TAB_SAVE_MODEL].saveMe()

    def loadModelEvent(self, directory):
        file_name = os.path.join(directory, "results.txt")
        if os.path.isfile(file_name):
            file = open(file_name, "r")
            self.sendEventToChildren(lambda x: x.loadBciSettingsEvent(file))
        else:
            print file_name, "does not exist!"

    def addNewModelTabEvent(self):
        self.widgets_dict[c.TIMESTAMP_TEXTBOX].setTimestamp()


class CheckbuttonFrame(AddingCheckbuttonsFrame.LabelledEventNotebookAddingCheckbuttonFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        AddingCheckbuttonsFrame.LabelledEventNotebookAddingCheckbuttonFrame.__init__(self, parent, name, row, column, columnspan=6, **kwargs)

    def addNewRecordingTabEvent(self):
        self.addButton()

    def recordTabRemovedEvent(self, deleted_tab):
        self.deleteButton(deleted_tab)

    def loadEegEvent(self, directory):
        self.addButton()

    def saveBciSettingsEvent(self, file):
        return c.STOP_EVENT_SENDING

    def loadBciSettingsEvent(self, file):
        return c.STOP_EVENT_SENDING


class OptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MODELS_TAB_OPTIONS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            CheckbuttonFrame(self, c.MODELS_TAB_RECORDING_FOR_TRAINING, 0, 0),
            CheckbuttonFrame(self, c.MODELS_TAB_RECORDING_FOR_VALIDATION, 1, 0),
            Textboxes.LabelTextbox(self, c.MODELS_TAB_LOOK_BACK_LENGTH, 2, 0, command=int, default_value=1),
            Textboxes.LabelTextbox(self, c.MODELS_TAB_CV_FOLDS, 2, 2, command=int, default_value=5),
            Textboxes.LabelTextboxNoValidation(self, c.MODELS_TAB_FEATURES_TO_USE, 3, 0, default_value="", width=20, columnspan=3),
        ))

    def disableModelOptionsEvent(self):
        self.disable(c.MODEL_TRAINED_DISABLER)

    def getModelOptionsEvent(self):
        self.sendEventToRoot(lambda x: x.sendModelOptionsToRootEvent(self.getValue()), True)


class SaveButton(Buttons.EventNotebookSaveButton):
    def __init__(self, parent, row, column, **kwargs):
        Buttons.EventNotebookSaveButton.__init__(self, parent, c.MODELS_TAB_SAVE_MODEL, row, column, **kwargs)

    def sendSaveEvent(self, file):
        return lambda x: x.saveModelEvent(file)


class ModelFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.EEG_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self, c.MODELS_TAB_SHOW_TRAINING_ROC, 0, 0, command=self.showTrainingRoc),
            Buttons.Button(self, c.MODELS_TAB_SHOW_VALIDATION_ROC, 0, 1, command=self.showValidationRoc),
            Buttons.Button(self, c.MODELS_TAB_SHOW_TRAINING_LDA, 1, 0, command=self.showTrainingDataProjection),
            Buttons.Button(self, c.MODELS_TAB_SHOW_VALIDATION_LDA, 1, 1, command=self.showValidationDataProjection),
        ))
        self.model = None
        self.training_data = None
        self.validation_data = None
        self.training_labels = None
        self.validation_labels = None
        self.min_max = None
        self.thresholds = None
        self.training_roc = None
        self.validation_roc = None

    def plotRoc(self, roc):
        fpr, tpr, _, roc_auc = roc
        plt.figure()
        plt.plot(fpr["micro"], tpr["micro"],
                 label='micro-average ROC curve (area = {0:0.2f})'
                       ''.format(roc_auc["micro"]),
                 linewidth=2)
        plt.plot(fpr["macro"], tpr["macro"],
                 label='macro-average ROC curve (area = {0:0.2f})'
                       ''.format(roc_auc["macro"]),
                 linewidth=2)
        for i in range(len(self.model.classes_)):
            plt.plot(fpr[i], tpr[i], label='ROC curve of class {0} (area = {1:0.2f})'
                                           ''.format(i, roc_auc[i]))
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Some extension of Receiver operating characteristic to multi-class')
        plt.legend(loc="lower right")
        plt.show()

    def showTrainingRoc(self):
        self.plotRoc(self.training_roc)

    def showValidationRoc(self):
        self.plotRoc(self.validation_roc)

    def plotLda(self, data, labels):
        if len(self.model.classes_) == 3:
            x = self.model.transform(data)
            step_size = 0.2
            # x_min, x_max = x[:, 0].min() - 1, x[:, 0].max() + 1
            # y_min, y_max = x[:, 1].min() - 1, x[:, 1].max() + 1
            # xx, yy = np.meshgrid(np.arange(x_min, x_max, step_size), np.arange(y_min, y_max, step_size))
            # print xx.shape
            # print yy.shape
            # print np.c_[xx.ravel(), yy.ravel()]
            # print np.c_[xx.ravel(), yy.ravel()].shape
            # print
            # Z = self.model.predict(np.c_[xx.ravel(), yy.ravel()])
            # Z = Z.reshape(xx.shape)
            # plt.contourf(xx, yy, Z, cmap=plt.cm.Paired, alpha=0.8)

            # mins = [data[:, i].min() for i in range(data.shape[1])]
            # maxs = [data[:, i].max() for i in range(data.shape[1])]
            # decision_function_values = []
            # for feature in range(x.shape[1]):
            #     for value in np.linspace(mins[feature], maxs[feature]):
            #         decision_function_values.append(self.model.decision_function([features])[0])

            # grid = np.array(np.meshgrid(*[np.linspace(mins[i], maxs[i], num=5) for i in range(data.shape[1])]))
            # print grid
            # print grid.shape
            # print np.c_[grid[0].ravel(), grid[1].ravel()]
            # print np.c_[grid[0].ravel(), grid[1].ravel()].shape
            # prediction = self.model.predict(np.c_[grid[0].ravel(), grid[1].ravel()])
            # w, v = np.linalg.eig(self.model.covariance_)

            # print map(lambda x: np.sqrt(sum(x[i]**2 for i in range(self.model.coef_.shape[1]))), self.model.coef_)
            # coef_in_new_space = self.model.transform(self.model.coef_)
            # row_lengths = map(lambda x: np.sqrt(x[0]**2+x[1]**2), coef_in_new_space)
            # print row_lengths
            # new_matrix = np.array(map(lambda r: [r[0][0]/r[1], r[0][1]/r[1]], zip(coef_in_new_space, row_lengths)))
            # print self.model.coef_.shape
            # print coef_in_new_space
            # print new_matrix.shape
            # print new_matrix
            # decision_values = np.dot(x, new_matrix.T)# + self.model.intercept_
            # print decision_values
            # print self.model.decision_function(data)
            # print decision_values - self.model.decision_function(data)

            labels = np.array(labels)
            plt.figure()
            # plt.plot(coef_in_new_space[0])
            for c, i, target_name in zip("rgb", [1, 2, 3], [1, 2, 3]):
                plt.scatter(x[labels == i, 0], x[labels == i, 1], c=c, label=target_name, marker="o")
            plt.legend()
            plt.title('LDA')
            plt.show()
        else:
            print "Model has", len(self.model.classes_), "classes. Cannot plot."

    def showTrainingDataProjection(self):
        self.plotLda(self.training_data, self.training_labels)

    def showValidationDataProjection(self):
        self.plotLda(self.validation_data, self.validation_labels)

    def loadModelEvent(self, directory):
        file_handle = file(os.path.join(directory, "model.pkl"))
        self.model = pickle.load(file_handle)
        self.training_data = pickle.load(file_handle)
        self.training_labels = pickle.load(file_handle)
        self.training_roc = pickle.load(file_handle)
        self.validation_data = pickle.load(file_handle)
        self.validation_labels = pickle.load(file_handle)
        self.validation_roc = pickle.load(file_handle)
        self.thresholds = pickle.load(file_handle)
        self.min_max = pickle.load(file_handle)

    def saveModelEvent(self, directory):
        file_handle = file(os.path.join(directory, "model.pkl"), "w")
        pickle.dump(self.model, file_handle)
        pickle.dump(self.training_data, file_handle)
        pickle.dump(self.training_labels, file_handle)
        pickle.dump(self.training_roc, file_handle)
        pickle.dump(self.validation_data, file_handle)
        pickle.dump(self.validation_labels, file_handle)
        pickle.dump(self.validation_roc, file_handle)
        pickle.dump(self.thresholds, file_handle)
        pickle.dump(self.min_max, file_handle)

    def modelReceivedEvent(self, model):
        self.model = model

    def trainingDataReceivedEvent(self, training_data):
        self.training_data = training_data

    def trainingLabelsReceivedEvent(self, training_labels):
        self.training_labels = training_labels

    def validationDataReceivedEvent(self, validation_data):
        self.validation_data = validation_data

    def validationLabelsReceivedEvent(self, validation_labels):
        self.validation_labels = validation_labels

    def minMaxReceivedEvent(self, min_max):
        self.min_max = min_max

    def thresholdsReceivedEvent(self, thresholds):
        self.thresholds = thresholds

    def trainingRocReceivedEvent(self, training_roc):
        self.training_roc = training_roc

    def validationRocReceivedEvent(self, validation_roc):
        self.validation_roc = validation_roc
