__author__ = 'Anti'

from main_window import MyWindows
import Tkinter


class Game(MyWindows.TkWindow):
    def __init__(self, connection):
        MyWindows.TkWindow.__init__(self, "Game", 500, 500)
        self.canvas = Tkinter.Canvas(self, width=self.window_width, height=self.window_height)
        self.canvas.pack()
        self.connection = connection
        self.rect = self.canvas.create_rectangle(self.window_width/2-5, self.window_height/2-5,
                                                 self.window_width/2+5, self.window_height/2+5,fill="blue")
        self.target_freqs = None
        self.exitFlag = False
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.myMainloop()

    def exit(self):
        self.exitFlag = True

    def start(self):
        step = 3
        print self.canvas.coords(self.rect)
        while True:
            detected_freq = self.recvPacket()
            if isinstance(detected_freq, basestring):
                return detected_freq
            if detected_freq == self.target_freqs[0] and self.canvas.coords(self.rect)[1] > step:
                self.canvas.move(self.rect, 0, -step)
            elif len(self.target_freqs) > 1 and detected_freq == self.target_freqs[1] and self.canvas.coords(self.rect)[2] < self.window_height-step:
                self.canvas.move(self.rect, step, 0)
            elif len(self.target_freqs) > 2 and detected_freq == self.target_freqs[2] and self.canvas.coords(self.rect)[3] < self.window_width-step:
                self.canvas.move(self.rect, 0, step)
            elif len(self.target_freqs) > 3 and detected_freq == self.target_freqs[3] and self.canvas.coords(self.rect)[0] > step:
                self.canvas.move(self.rect, -step, 0)

    def recvPacket(self):
        while True:
            self.update()
            if self.connection.poll(0.1):
                message = self.connection.recv()
                return message
            if self.exitFlag:
                return "Exit"

    def myMainloop(self):
        while True:
            message = self.recvPacket()
            if message == "Start":
                print "Starting", self.name
                self.target_freqs = self.connection.recv()
                message = self.start()
                if message == "Stop":
                    print "Stopping", self.name
            if message == "Exit" or self.exitFlag:
                print "Exiting", self.name
                break
        self.connection.send("Close")
        self.connection.close()
        self.destroy()
