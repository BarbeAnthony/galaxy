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

    def keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down, on_key_up=self.on_keyboard_up)
        self._keyboard = None

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

    def on_perspective_point_y(self, widget, value):
        # print("perspective point y : " + str(value))
        pass

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

    def transform(self, x, y):  # affichage en perspective pour jouer, ou en 2D pour débuguer
        # return self.transform_2D(x, y)
        return self.transform_perspective(x, y)

    def transform_2D(self, x, y):
        return int(x), int(y)

    def transform_perspective(self, x, y):
        # transformation linéaire de la coordonnée y : le haut de l'écran est projeté au point de perspective,
        # ce qui est encore plus haut aussi
        lin_y = y * self.perspective_point_y / self.height
        if lin_y > self.perspective_point_y:
            lin_y = self.perspective_point_y
        # écart entre le point à transformer et le point de perspective
        diff_x = x - self.perspective_point_x
        diff_y = self.perspective_point_y - lin_y
        # facteur de transformation vertical
        factor_y = diff_y / self.perspective_point_y
        factor_y = pow(factor_y, 4)  # modifier l'effet de perspective
        # calcul des nouvelles coordonées
        offset_x = diff_x * factor_y
        tr_x = self.perspective_point_x + offset_x
        tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
        return int(tr_x), int(tr_y)

    def update(self, dt):
        # pour stabiliser la vitesse de défilement du niveau, indépendament des fps du périphérique utilisé
        # print(str(dt*60))
        time_factor = dt * 60
        # actualiser la grille et faire avancer le terrain :
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.current_offset_y = self.current_offset_y + self.SPEED * time_factor
        # déplacer le vaisseau latéralement
        self.current_offset_x = self.current_offset_x + self.current_speed_x * time_factor
        # retour à l'état initial si le terrain a avancé d'une case :
        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            self.current_offset_y -= spacing_y

    # Contrôles au toucher ou au clic
    def on_touch_down(self, touch):
        if touch.x >= self.width/2:
            self.current_speed_x = self.SPEED_X  # ->
        else:
            self.current_speed_x = -self.SPEED_X  # <-

    def on_touch_up(self, touch):
        self.current_speed_x = 0

    # Contrôles au clavier
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.current_speed_x = -self.SPEED_X
        elif keycode[1] == 'right':
            self.current_speed_x = +self.SPEED_X
        return True

    def on_keyboard_up(self, keyboard, keycode):
        self.current_speed_x = 0
        return True


class GalaxyApp(App):
    pass


GalaxyApp().run()
