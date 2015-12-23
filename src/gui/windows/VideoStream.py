from PIL import Image, ImageTk
import Tkinter
import io

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

    def updateStream(self, bytes):
        image = Image.open(io.BytesIO(bytes))
        tki = ImageTk.PhotoImage(image)
        self.image_label.configure(image=tki)
        self.image_label._backbuffer_ = tki  # avoid flicker caused by premature gc
