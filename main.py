from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.window import Window
from kivy import platform
from kivy.app import App
from kivy.graphics import Color, Line, Quad
from kivy.properties import NumericProperty, Clock
from kivy.uix.widget import Widget
import random


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
    current_y_loop = 0
    SPEED = 3

    current_offset_x = 0
    current_speed_x = 0
    SPEED_X = 15

    NB_TILES = 8
    tiles = []
    tiles_coordinates = []

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)  # Pourquoi ces arguments pour super? TO DO   (vidéo 297 point de perspective)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.generate_tiles_coordinates()
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

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def generate_tiles_coordinates(self):
        next_y = 0
        next_x = 0
        # Actualisation des tiles :
        if len(self.tiles_coordinates) > 0:
            # suppression des tiles passés
            for i in range(len(self.tiles_coordinates)-1, -1, -1):
                if self.tiles_coordinates[i][1] < self.current_y_loop:
                    del self.tiles_coordinates[i]
            next_x = self.tiles_coordinates[-1][0]
            next_y = self.tiles_coordinates[-1][1] + 1
        # création de nouveaux tiles
        for i in range(len(self.tiles_coordinates)-1, self.NB_TILES):
            trajectoire = random.randint(-1, 1)
            self.tiles_coordinates.append((next_x, next_y))
            if trajectoire == -1:  # décaler à gauche
                next_x -= 1
                self.tiles_coordinates.append((next_x, next_y))
                next_y += 1
                self.tiles_coordinates.append((next_x, next_y))
            elif trajectoire == 1:  # décaler à droite
                next_x += 1
                self.tiles_coordinates.append((next_x, next_y))
                next_y += 1
                self.tiles_coordinates.append((next_x, next_y))
            next_y += 1

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return int(x), int(y)

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)

            # 2 (xmin, ymax)    3 (xmax, ymax)
            #
            # 1 (xmin,ymin)     4 (xmax, ymin)
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)
            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update(self, dt):
        # pour stabiliser la vitesse de défilement du niveau, indépendament des fps du périphérique utilisé
        # print(str(dt*60))
        time_factor = dt * 60
        # actualiser la grille et faire avancer le terrain :
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.current_offset_y = self.current_offset_y + self.SPEED * time_factor
        # Quand le terrain a avancé d'une case
        spacing_y = self.H_LINES_SPACING * self.height
        if self.current_offset_y >= spacing_y:
            # recul du terrain d'une case
            self.current_offset_y -= spacing_y
            # comptage du nombre de cases passées dans la partie
            self.current_y_loop += 1
            # suppression des tiles passés et création de nouveaux tiles
            self.generate_tiles_coordinates()
        # déplacer le vaisseau latéralement
        self.current_offset_x = self.current_offset_x + self.current_speed_x * time_factor


class GalaxyApp(App):
    pass


GalaxyApp().run()
