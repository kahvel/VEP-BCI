from gui_elements.widgets import Buttons, Textboxes
from gui_elements.widgets.frames import Frame, AddingCheckbuttonsFrame
from gui_elements.widgets.frames.tabs import DisableDeleteNotebookTab
import constants as c

from sklearn.neighbors import KNeighborsClassifier
from matplotlib.colors import ListedColormap

import matplotlib2tikz
import matplotlib.pyplot as plt
import os
import pickle
import numpy as np
import Tkinter


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


class LabelledCheckbuttonFrame(Frame.Frame):
    def __init__(self, parent, name, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, name, row, column, columnspan=6, **kwargs)
        Tkinter.Label(self.widget, text=name).grid(row=row, column=column, padx=self.padx, pady=self.pady, columnspan=1)
        self.addChildWidgets((
            CheckbuttonFrame(self, name, row, column+1, **kwargs),
        ))


class CheckbuttonFrame(AddingCheckbuttonsFrame.EventNotebookAddingCheckbuttonFrame):
    def __init__(self, parent, name, row, column, **kwargs):
        AddingCheckbuttonsFrame.EventNotebookAddingCheckbuttonFrame.__init__(self, parent, name, row, column+1, **kwargs)

    def addNewRecordingCheckbuttonEvent(self):
        self.addButton()

    def recordTabRemovedEvent(self, deleted_tab):
        self.deleteButton(deleted_tab)

    # def loadEegEvent(self, directory):
    #     self.addButton()

    def sendRecordingNotebookWidgetsEvent(self, recording_notebook_widgets):
        self.setWidgetsNotebook(recording_notebook_widgets)

    def getNotebookWidgetsEvent(self):
        self.sendEventToAll(lambda x: x.getRecordingNotebookWidgetsEvent())


class OptionsFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MODELS_TAB_OPTIONS_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            LabelledCheckbuttonFrame(self, c.MODELS_TAB_RECORDING_FOR_TRAINING, 0, 0),
            LabelledCheckbuttonFrame(self, c.MODELS_TAB_RECORDING_FOR_VALIDATION, 1, 0),
            Textboxes.LabelTextbox(self, c.MODELS_TAB_LOOK_BACK_LENGTH, 2, 0, command=int, default_value=1),
            Textboxes.LabelTextbox(self, c.MODELS_TAB_CV_FOLDS, 2, 2, command=int, default_value=5),
            Textboxes.LabelTextboxNoValidation(self, c.MODELS_TAB_FEATURES_TO_USE, 3, 0, default_value="", width=20, columnspan=3),
        ))

    def disableModelOptionsEvent(self):
        self.disable(c.MODEL_TRAINED_DISABLER)

    def getModelOptionsEvent(self):
        self.sendEventToRoot(lambda x: x.sendModelOptionsToRootEvent(self.getValue()), True)

    def usedFeaturesReceivedEvent(self, used_features):
        self.widgets_dict[c.MODELS_TAB_FEATURES_TO_USE].setValue('"'+'","'.join(used_features)+'"')

    def addNewRecordingCheckbuttonEvent(self):
        if self.disabled:
            return c.STOP_EVENT_SENDING

    def recordTabRemovedEvent(self, deleted_tab):
        if self.disabled:
            return c.STOP_EVENT_SENDING

    # def loadEegEvent(self, directory):
    #     if self.disabled:
    #         return c.STOP_EVENT_SENDING


class SaveButton(Buttons.EventNotebookSaveButton):
    def __init__(self, parent, row, column, **kwargs):
        Buttons.EventNotebookSaveButton.__init__(self, parent, c.MODELS_TAB_SAVE_MODEL, row, column, **kwargs)

    def sendSaveEvent(self, file):
        return lambda x: x.saveModelEvent(file)


class ModelFrame(Frame.Frame):
    def __init__(self, parent, row, column, **kwargs):
        Frame.Frame.__init__(self, parent, c.MODELS_TAB_MODEL_FRAME, row, column, **kwargs)
        self.addChildWidgets((
            Buttons.Button(self, c.MODELS_TAB_SHOW_TRAINING_ROC, 0, 0, command=self.showTrainingRoc),
            Buttons.Button(self, c.MODELS_TAB_SHOW_TESTING_ROC, 1, 0, command=self.showTestingRoc),
            Buttons.Button(self, c.MODELS_TAB_SHOW_TRAINING_PRC, 0, 1, command=self.showTrainingPrc),
            Buttons.Button(self, c.MODELS_TAB_SHOW_TESTING_PRC, 1, 1, command=self.showTestingPrc),
            Buttons.Button(self, c.MODELS_TAB_SHOW_TRAINING_LDA, 0, 2, command=self.showTrainingDataProjection),
            Buttons.Button(self, c.MODELS_TAB_SHOW_TESTING_LDA, 1, 2, command=self.showTestingDataProjection),
        ))
        self.model = None
        self.second_model = None
        self.training_data = None
        self.testing_data = None
        self.training_labels = None
        self.testing_labels = None
        self.min_max = None
        self.thresholds = None
        self.training_roc = None
        self.testing_roc = None
        self.training_prc = None
        self.testing_prc = None

    def getValue(self):
        frame_value = Frame.Frame.getValue(self)
        frame_value.update({c.MODELS_TAB_MODEL_DATA: {
            c.MODELS_TAB_MODEL: self.model,
            c.MODELS_TAB_SECOND_MODEL: self.second_model,
            c.MODELS_TAB_MIN_MAX: self.min_max,
            c.MODELS_TAB_THRESHOLDS: self.thresholds,
        }})
        return frame_value

    def plotRoc(self, roc):
        fpr, tpr, _, roc_auc = roc
        plt.figure()
        if "micro" in fpr and "micro" in tpr:
            plt.plot(fpr["micro"], tpr["micro"],
                     label='micro-average ROC curve (area = {0:0.2f})'
                           ''.format(roc_auc["micro"]),
                     linewidth=2)
        if "macro" in fpr and "macro" in tpr:
            plt.plot(fpr["macro"], tpr["macro"],
                     label='macro-average ROC curve (area = {0:0.2f})'
                           ''.format(roc_auc["macro"]),
                     linewidth=2)
        for i in range(len(self.second_model.classes_)):
            plt.plot(fpr[i], tpr[i], label='ROC curve of class {0} (area = {1:0.2f})'
                                           ''.format(i, roc_auc[i]))
        plt.plot([0, 1], [0, 1], 'k--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Some extension of Receiver operating characteristic to multi-class')
        plt.legend(loc="lower right")
        # import time
        # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")
        plt.show()

    def checkDataAndPlotRoc(self, data):
        if self.training_roc is not None:
            self.plotRoc(data)
        else:
            print "Model is not trained!"

    def checkDataAndPlotLda(self, data, labels):
        if self.training_roc is not None:
            self.plotLda(data, labels)
        else:
            print "Model is not trained!"

    def showTrainingRoc(self):
        self.checkDataAndPlotRoc(self.training_roc)

    def showTestingRoc(self):
        self.checkDataAndPlotRoc(self.testing_roc)

    def showTrainingPrc(self):
        self.checkDataAndPlotRoc(self.training_prc)

    def showTestingPrc(self):
        self.checkDataAndPlotRoc(self.testing_prc)

    def myPredict(self, xx):
        d = np.dot(xx, np.dot(self.model.means_, self.model.scalings_).T)
        y_pred = self.model.classes_.take(d.argmax(1))
        return y_pred

    def plotLda(self, data, labels):
        if self.model is None:
            print "LDA model is not trained!"
        elif len(self.model.classes_) != 3:
            print "Model has", len(self.model.classes_), "classes. Cannot plot in 2D."
        else:
            x = self.model.transform(data)

            plt.figure()
            transformed_means = np.dot(self.model.means_-self.model.xbar_, self.model.scalings_)
            y = [0,1,2]
            n_neighbors = 1
            h = .02  # step size in the mesh
            # Create color maps
            cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF'])
            cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF'])
            # we create an instance of Neighbours Classifier and fit the data.
            clf = KNeighborsClassifier(n_neighbors, weights="uniform")
            clf.fit(transformed_means, y)

            # Plot the decision boundary. For that, we will assign a color to each
            # point in the mesh [x_min, x_max]x[y_min, y_max].
            x_min, x_max = x[:, 0].min() - 1, x[:, 0].max() + 1
            y_min, y_max = x[:, 1].min() - 1, x[:, 1].max() + 1
            xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                                 np.arange(y_min, y_max, h))
            Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
            # Z = self.myPredict(np.c_[xx.ravel(), yy.ravel()])

            # Put the result into a color plot
            Z = Z.reshape(xx.shape)
            plt.pcolormesh(xx, yy, Z, cmap=cmap_light)

            # Plot also the training points
            plt.scatter(transformed_means[:, 0], transformed_means[:, 1], marker="s", c=y, cmap=cmap_bold)

            labels = np.array(labels)
            for c, i, target_name in zip("rgb", [1, 2, 3], [1, 2, 3]):
                plt.scatter(x[labels == i, 0], x[labels == i, 1], c=c, label=target_name, marker="o")
            plt.legend()
            plt.title('LDA')

            plt.xlim(xx.min(), xx.max())
            plt.ylim(yy.min(), yy.max())
            # import time
            # matplotlib2tikz.save("C:\\Users\Anti\\Desktop\\PycharmProjects\\VEP-BCI\\file" + str(round(time.time())) + ".tex")
            plt.show()

    def showTrainingDataProjection(self):
        self.checkDataAndPlotLda(self.training_data, self.training_labels)

    def showTestingDataProjection(self):
        self.checkDataAndPlotLda(self.testing_data, self.testing_labels)

    def loadModelEvent(self, directory):
        file_handle = file(os.path.join(directory, "model.pkl"))
        self.model = pickle.load(file_handle)
        self.second_model = pickle.load(file_handle)
        self.training_data = pickle.load(file_handle)
        self.training_labels = pickle.load(file_handle)
        self.training_roc = pickle.load(file_handle)
        self.testing_data = pickle.load(file_handle)
        self.testing_labels = pickle.load(file_handle)
        self.testing_roc = pickle.load(file_handle)
        self.training_prc = pickle.load(file_handle)
        self.testing_prc = pickle.load(file_handle)
        self.thresholds = pickle.load(file_handle)
        self.min_max = pickle.load(file_handle)  # If there is EOF exception here, it probably means that this file does not have second model saved.

    def saveModelEvent(self, directory):
        file_handle = file(os.path.join(directory, "model.pkl"), "w")
        pickle.dump(self.model, file_handle)
        pickle.dump(self.second_model, file_handle)
        pickle.dump(self.training_data, file_handle)
        pickle.dump(self.training_labels, file_handle)
        pickle.dump(self.training_roc, file_handle)
        pickle.dump(self.testing_data, file_handle)
        pickle.dump(self.testing_labels, file_handle)
        pickle.dump(self.testing_roc, file_handle)
        pickle.dump(self.training_prc, file_handle)
        pickle.dump(self.testing_prc, file_handle)
        pickle.dump(self.thresholds, file_handle)
        pickle.dump(self.min_max, file_handle)

    def modelReceivedEvent(self, model):
        if self.model is None:
            self.model = model

    def secondModelReceivedEvent(self, model):
        if self.second_model is None:
            self.second_model = model

    def trainingDataReceivedEvent(self, training_data):
        if self.training_data is None:
            self.training_data = training_data

    def trainingLabelsReceivedEvent(self, training_labels):
        if self.training_labels is None:
            self.training_labels = training_labels

    def testingDataReceivedEvent(self, validation_data):
        if self.testing_data is None:
            self.testing_data = validation_data

    def testingLabelsReceivedEvent(self, validation_labels):
        if self.testing_labels is None:
            self.testing_labels = validation_labels

    def minMaxReceivedEvent(self, min_max):
        if self.min_max is None:
            self.min_max = min_max

    def thresholdsReceivedEvent(self, thresholds):
        if self.thresholds is None:
            self.thresholds = thresholds

    def trainingRocReceivedEvent(self, training_roc):
        if self.training_roc is None:
            self.training_roc = training_roc

    def testingRocReceivedEvent(self, validation_roc):
        if self.testing_roc is None:
            self.testing_roc = validation_roc

    def trainingPrcReceivedEvent(self, training_prc):
        if self.training_prc is None:
            self.training_prc = training_prc

    def testingPrcReceivedEvent(self, validation_prc):
        if self.testing_prc is None:
            self.testing_prc = validation_prc