__author__ = 'Anti'

from controllable_windows import ControllableWindow
import Tkinter


class PlotWindow(ControllableWindow.ControllableWindow):
    def __init__(self, title):
        ControllableWindow.ControllableWindow.__init__(self, title, 512, 512)
        self.canvas = Tkinter.Canvas(self, width=512, height=512)
        self.canvas.pack()

    def resetCanvas(self):
        self.canvas.delete("all")
        for i in range(0, self.window_width, 40):  # scale for FFT
            self.canvas.create_line(i, 0, i, self.window_height, fill="red")
            self.canvas.create_text(i, 10, text=i/8)

    def scaleY(self, y,  index, new_max=-100, new_min=100):
        old_max, old_min = self.getScale()
        return ((((y - old_min) * (new_max - new_min)) / (old_max - old_min)) + new_min
                + index*self.window_height + self.window_height/2) / self.gen_count

    def getScale(self):
        raise NotImplementedError("getScale not implemented")

    def getLength(self, coordinates):
        raise NotImplementedError("getLength not implemented")

    def scale(self, coordinates, index):
        result = []
        length = self.getLength(coordinates)
        for i in range(len(coordinates)):
            result.append(i*self.window_width/length)
            result.append(self.scaleY(coordinates[i], index))
        return result

    def getGenerator(self, index):
        return self.generator(index)

    def generator(self, index):
        coordinates_generator = self.getCoordGenerator()
        try:
            line = self.canvas.create_line(0, 0, 0, 0)
            coordinates_generator.send(None)
            while True:
                y = yield
                coordinates = coordinates_generator.send(y)
                if coordinates is not None:
                    scaled_avg = self.scale(coordinates, index)
                    self.canvas.delete(line)
                    line = self.canvas.create_line(scaled_avg)
                    coordinates_generator.next()
        finally:
            print "Closing generator"
            coordinates_generator.close()