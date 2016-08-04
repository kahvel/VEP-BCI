import tkFileDialog
import os


def getLocation():
    import __main__
    return os.path.dirname(os.path.abspath(__main__.__file__))


class Savable(object):
    def saveToFile(self, file):
        raise NotImplementedError("saveToFile not implemented!")

    def askSaveFile(self):
        self.saveFile(tkFileDialog.asksaveasfile(defaultextension=".txt", initialdir=getLocation()))

    def saveFile(self, file):
        if file is not None:
            self.saveToFile(file)
            file.close()


class Loadable(object):
    def loadFromFile(self, file):
        raise NotImplementedError("loadFromFile not implemented!")

    def askLoadFile(self):
        self.loadFile(tkFileDialog.askopenfile(defaultextension=".txt", initialdir=getLocation()))

    def loadFile(self, file):
        if file is not None:
            self.loadFromFile(file)
            file.close()


class SavableDirectory(object):
    def saveToFile(self, file):
        raise NotImplementedError("saveToFile not implemented!")

    def askSaveFile(self):
        self.saveFile(os.path.join(getLocation(), tkFileDialog.askdirectory(initialdir=getLocation())))

    def saveFile(self, directory):
        if directory is not None:
            self.saveToFile(directory)


class LoadableDirectory(object):
    def loadFromFile(self, file):
        raise NotImplementedError("loadFromFile not implemented!")

    def askLoadFile(self):
        self.loadFile(os.path.join(getLocation(), tkFileDialog.askdirectory(initialdir=getLocation())))

    def loadFile(self, directory):
        if directory is not None:
            self.loadFromFile(directory)
