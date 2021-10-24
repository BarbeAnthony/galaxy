from kivy.app import App
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class MainWidget(Widget):
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)  # Pourquoi ces arguments pour super? TO DO   (vidéo 297 point de perspective)

    def on_parent(self, widget, parent):
        pass

    def on_size(self, *args):
        # print(str(self.width) + " , " + str(self.height))
        # self.perspective_point_x = self.width / 2
        # self.perspective_point_y = self.height * 0.75
        # print("perspective point : " + str(self.width / 2) + " , " + str(self.height * 0.75))
        pass

    def on_perspective_point_x(self, widget, value):
        # print("perspective point x : " + str(value))
        pass

    def on_perspective_point_y(self, widget,  value):
        # print("perspective point y : " + str(value))
        pass


class GalaxyApp(App):
    pass


GalaxyApp().run()
