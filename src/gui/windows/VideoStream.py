import cv2
from PIL import Image, ImageTk
import Tkinter

import MyWindows


class StreamWindow(MyWindows.TkWindow):
    def __init__(self):
        MyWindows.TkWindow.__init__(self, "Stream")
        self.image_label = None

    def setup(self):
        self.image_label = Tkinter.Label(self)
        self.image_label.pack()

    def exit(self):
        if self.exitFlag:
            self.destroy()

    def updateStream(self, image):
        tki = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)))
        self.image_label.configure(image=tki)
        self.image_label._backbuffer_ = tki  # avoid flicker caused by premature gc
