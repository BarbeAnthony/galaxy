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

    V_LINES_NB = 10  # doit être pair
    V_LINES_SPACING = .25  # % of width
    vertical_lines = []

    H_LINES_NB = 8
    H_LINES_SPACING = .1  # % of height
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

    def update_vertical_lines(self):
        central_line_x = self.width / 2
        spacing_x = self.V_LINES_SPACING * self.width
        offset_x = (-self.V_LINES_NB / 2 + 0.5) * spacing_x
        # traçage des lignes verticales
        for line in self.vertical_lines:
            line_x = int(central_line_x + offset_x - self.current_offset_x)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            line.points = (x1, y1, x2, y2)
            offset_x += spacing_x

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.H_LINES_NB):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        # 1ère ligne au bas de l'écran, puis espacement
        line_y = 0
        spacing_y = self.H_LINES_SPACING * self.height

        # limiter la largeur des lignes horizontales aux lignes verticales extrèmes
        central_line_x = self.width / 2
        spacing_x = self.V_LINES_SPACING * self.width
        offset_x = (-self.V_LINES_NB / 2 + 0.5) * spacing_x
        x_min = central_line_x + offset_x - self.current_offset_x
        x_max = central_line_x - offset_x - self.current_offset_x

        # traçage des lignes horizontales
        for line in self.horizontal_lines:
            x1, y1 = self.transform(x_min, line_y - self.current_offset_y)
            x2, y2 = self.transform(x_max, line_y - self.current_offset_y)
            line.points = (x1, y1, x2, y2)
            line_y += spacing_y

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
