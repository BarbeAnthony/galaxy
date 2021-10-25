
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