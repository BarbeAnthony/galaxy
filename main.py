from kivy.app import App
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_LINES_NB = 7 #DOIT ETRE IMPAIR
    V_LINES_SPACING = .1  # % of width
    vertical_lines = []

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(
            **kwargs)  # Pourquoi ces arguments pour super? TO DO   (vidéo 297 point de perspective)
        self.init_vertical_lines()

    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # print(str(self.width) + " , " + str(self.height))
        # self.perspective_point_x = self.width / 2
        # self.perspective_point_y = self.height * 0.75
        # print("perspective point : " + str(self.width / 2) + " , " + str(self.height * 0.75))
        self.update_vertical_lines()

    def on_perspective_point_x(self, widget, value):
        # print("perspective point x : " + str(value))
        pass

    def on_perspective_point_y(self, widget, value):
        # print("perspective point y : " + str(value))
        pass

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_LINES_NB):
                self.vertical_lines.append(Line())

    def update_vertical_lines(self):
        central_line_x = self.width/2
        spacing = self.V_LINES_SPACING * self.width
        offset = -int(self.V_LINES_NB/2) * spacing
        for line in self.vertical_lines:
            x1 = int(central_line_x + offset)
            y1 = 0
            x2 = x1
            y2 = self.height
            line.points = (x1, y1, x2, y2)
            offset += spacing


class GalaxyApp(App):
    pass


GalaxyApp().run()
