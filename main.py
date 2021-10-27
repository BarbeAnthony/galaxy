from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.core.window import Window
from kivy import platform
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.lang import Builder
import random

Builder.load_file("menu.kv")


class MainWidget(RelativeLayout):
    from user_actions import on_keyboard_up, on_keyboard_down, keyboard_closed, on_touch_down, on_touch_up
    from transforms import transform, transform_2D, transform_perspective

    menu_widget = ObjectProperty(None)
    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button_title = StringProperty("START")
    score_text = StringProperty("")

    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_LINES_NB = 8  # doit être pair
    V_LINES_SPACING = .4  # % of width
    vertical_lines = []

    H_LINES_NB = 8
    H_LINES_SPACING = .15  # % of height
    horizontal_lines = []

    current_offset_y = 0
    current_y_loop = 0
    SPEED = .008  # % of height    .005 easy   .008 normal   .012 hard

    current_offset_x = 0
    current_speed_x = 0
    SPEED_X = .02  # % of width

    NB_TILES = 14
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = 0.1  # % of width
    SHIP_HEIGHT = 0.035  # % oh height
    SHIP_BASE_Y = 0.04  # % oh height
    ship = None
    ship_hitbox_coordinates = (0, 0)  #pointe du vaisseau

    state_game_over = False
    state_game_has_started = False

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.reset_game()
        self.ship_init()
        if self.is_desktop:
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down, on_key_up=self.on_keyboard_up)
        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.score_text = "SCORE : " + str(self.current_y_loop)
        self.current_offset_x = 0
        self.current_speed_x = 0
        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.state_game_over = False


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
        start_v_index = -int(self.V_LINES_NB / 2) + 1
        end_v_index = start_v_index + self.V_LINES_NB - 1
        x_min = self.get_line_x_from_index(start_v_index)
        x_max = self.get_line_x_from_index(end_v_index)

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

    def pre_fill_tiles_coordinates(self):
        # démarer la partie par une ligne droite de 10 tiles
        for i in range(0,10):
            self.tiles_coordinates.append((0, i))

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
        start_v_index = -int(self.V_LINES_NB / 2) + 1
        end_v_index = start_v_index + self.V_LINES_NB - 1
        for i in range(len(self.tiles_coordinates)-1, self.NB_TILES):
            # limiter la trajectoire à la grille affichée
            if next_x == start_v_index:
                trajectoire = random.randint(0, 1)
            elif next_x == end_v_index-1:
                trajectoire = random.randint(-1, 0)
            else:
                trajectoire = random.randint(-1, 1)
            # tracer la trajectoire
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

    def ship_init(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def ship_update(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y * self.height
        half_width = self.SHIP_WIDTH * self.width /2
        height = self.SHIP_HEIGHT * self.height
        #   2 <- (Hitbox)
        # 1   3
        x1, y1 = self.transform(center_x-half_width, base_y)
        self.ship_hitbox_coordinates = center_x, base_y + height
        x2, y2 = self.transform(*self.ship_hitbox_coordinates)
        x3, y3 = self.transform(center_x + half_width, base_y)
        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        if xmin <= self.ship_hitbox_coordinates[0] <= xmax and ymin <= self.ship_hitbox_coordinates[1] <= ymax:
            return True
        return False

    def check_ship_collisions(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            # on ne teste pas les tiles au delà de la deuxième rangée car collision impossible
            if ti_y > self.current_y_loop + 1:
                return False
            # test de collision
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def update(self, dt):
        # Pour stabiliser la vitesse de défilement du niveau, indépendament des fps du périphérique utilisé
        # print(str(dt*60))
        time_factor = dt * 60

        # Actualiser la grille :
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.ship_update()

        # Gérer le mouvement (si jeu en cours)
        if self.state_game_has_started and not self.state_game_over:
            # Avancée du terrain
            self.current_offset_y = self.current_offset_y + self.SPEED * self.height * time_factor
            # Quand le terrain a avancé d'une case :
            spacing_y = self.H_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                # recul du terrain d'une case
                self.current_offset_y -= spacing_y
                # comptage du nombre de cases passées dans la partie
                self.current_y_loop += 1
                self.score_text = "SCORE : " + str(self.current_y_loop)
                # suppression des tiles passés et création de nouveaux tiles
                self.generate_tiles_coordinates()
            # déplacer le vaisseau latéralement
            self.current_offset_x = self.current_offset_x + self.current_speed_x * self.width * time_factor

        # tester si le vaisseau est sur la piste
        if not self.check_ship_collisions() and not self.state_game_over:
            self.state_game_over = True
            self.menu_widget.opacity = 1
            self.menu_widget.disabled = False

    def on_menu_button_pressed(self):
        self.reset_game()
        self.state_game_has_started = True
        self.menu_widget.opacity = 0
        self.menu_widget.disabled = True
        self.menu_title = "G  A  M  E    O  V  E  R"
        self.menu_button_title = "RESTART"


class GalaxyApp(App):
    pass


GalaxyApp().run()
