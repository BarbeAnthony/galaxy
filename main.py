from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.window import Window
from kivy import platform
from kivy.app import App
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget


class MainWidget(Widget):
    from user_actions import on_keyboard_up, on_keyboard_down, keyboard_closed, on_touch_down, on_touch_up
    from transforms import transform, transform_2D, transform_perspective

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_LINES_NB = 4  # doit être pair
    V_LINES_SPACING = .1  # % of width
    vertical_lines = []

    H_LINES_NB = 8
    H_LINES_SPACING = .15  # % of height
    horizontal_lines = []

    current_offset_y = 0
    SPEED = 1

    current_offset_x = 0
    current_speed_x = 0
    SPEED_X = 15

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)  # Pourquoi ces arguments pour super? TO DO   (vidéo 297 point de perspective)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        if self.is_desktop:
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def is_desktop(self):
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.V_LINES_NB):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, h_index):
        central_line_x = self.perspective_point_x
        spacing_x = self.V_LINES_SPACING * self.width
        offset_x = (h_index - 0.5) * spacing_x
        line_x = int(central_line_x + offset_x - self.current_offset_x)
        return line_x

    def update_vertical_lines(self):
        # traçage des lignes verticales
        start_index = -int(self.V_LINES_NB/2) + 1
        for i in range(start_index, start_index + self.V_LINES_NB):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = (x1, y1, x2, y2)

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_LINES_NB):
                self.horizontal_lines.append(Line())

    def get_line_y_from_index(self, v_index):
        spacing_y = self.H_LINES_SPACING * self.height
        line_y = v_index * spacing_y - self.current_offset_y
        return line_y

    def update_horizontal_lines(self):
        # limiter la largeur des lignes horizontales aux lignes verticales extrèmes
        start_index = -int(self.V_LINES_NB / 2) + 1
        end_index = start_index + self.V_LINES_NB - 1
        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)

        # traçage des lignes horizontales
        for i in range(0, self.H_LINES_NB):
            x1, y1 = self.transform(x_min, self.get_line_y_from_index(i))
            x2, y2 = self.transform(x_max, self.get_line_y_from_index(i))
            self.horizontal_lines[i].points = (x1, y1, x2, y2)

    def update(self, dt):
        # pour stabiliser la vitesse de défilement du niveau, indépendament des fps du périphérique utilisé
        # print(str(dt*60))
        time_factor = dt * 60
        # actualiser la grille et faire avancer le terrain :
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.current_offset_y = self.current_offset_y + self.SPEED * time_factor
        # retour à l'état initial si le terrain a avancé d'une case :
        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y
        # déplacer le vaisseau latéralement
        self.current_offset_x = self.current_offset_x + self.current_speed_x * time_factor


class GalaxyApp(App):
    pass


GalaxyApp().run()
