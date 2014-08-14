__author__ = 'Anti'
import Tkinter
import ControllableWindow


class PlotWindow(ControllableWindow.ControllableWindow):
    def __init__(self, title):
        ControllableWindow.ControllableWindow.__init__(self, title, 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.canvas.pack()

    def resetCanvas(self):
        self.canvas.delete("all")
        for i in range(0, 512, 40):  # scale
            self.canvas.create_line(i, 0, i, 512, fill="red")
            self.canvas.create_text(i, 10, text=i/8)

    def scaleY(self, y,  index, plot_count, old_max, old_min, new_max=-100, new_min=100):
        return ((((y - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min
                + index*self.window_height + self.window_height/2) / plot_count

    def scale(self, avg, index, packet_count):
        raise NotImplementedError("scale not implemented")

    def generator(self, index, start_deleting):
        coordinates_generator = self.getGenerator()
        try:
            lines = [self.canvas.create_line(0, 0, 0, 0)]
            packet_count = 0
            delete = False
            coordinates_generator.send(None)
            while True:
                y = yield
                avg = coordinates_generator.send(y)
                if avg is not None:
                    scaled_avg = self.scale(avg, index, packet_count)
                    lines.append(self.canvas.create_line(scaled_avg))
                    coordinates_generator.next()
                    if start_deleting(packet_count):
                        packet_count = 0
                        delete = True
                    if delete:
                        self.canvas.delete(lines[0])
                        del lines[0]
                packet_count += 1
        finally:
            print "Closing generator"
            coordinates_generator.close()