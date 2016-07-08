import tkFileDialog
import os


def getLocation():
    import __main__
    return os.path.dirname(os.path.abspath(__main__.__file__))


class Savable(object):
    def saveToFile(self, file):
        raise NotImplementedError("save not implemented!")

    def askSaveFile(self):
        self.saveFile(tkFileDialog.asksaveasfile(defaultextension=".txt", initialdir=getLocation()))

    def saveFile(self, file):
        if file is not None:
            self.saveToFile(file)
            file.close()


class Loadable(object):
    def loadFromFile(self, file):
        raise NotImplementedError("load not implemented!")

    def askLoadFile(self):
        self.loadFile(tkFileDialog.askopenfile(defaultextension=".txt", initialdir=getLocation()))

    def loadFile(self, file):
        if file is not None:
            self.loadFromFile(file)
            file.close()
