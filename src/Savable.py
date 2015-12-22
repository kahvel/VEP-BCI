import tkFileDialog


class Savable(object):
    def save(self, file):
        raise NotImplementedError("save not implemented!")

    def askSaveFile(self):
        self.saveFile(tkFileDialog.asksaveasfile())

    def saveFile(self, file):
        if file is not None:
            self.save(file)
            file.close()


class Loadable(object):
    def load(self, file):
        raise NotImplementedError("load not implemented!")

    def askLoadFile(self):
        self.loadFile(tkFileDialog.askopenfile())

    def loadFile(self, file):
        if file is not None:
            self.load(file)
            file.close()