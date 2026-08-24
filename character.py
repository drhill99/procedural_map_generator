import pygame

class Character:
    def __init__(self, coord: tuple, angle: int):
        self.coord = coord
        self.angle = angle
        self.render_x = float(self.coord[0])
        self.render_y = float(self.coord[1])
        self.image = pygame.image.load("assets/avatar.png").convert_alpha()
        self.image = pygame.transform.rotate(
             self.image,
             90
        )
        for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    if self.image.get_at((x,y))[:3] == (255,255,255):
                        self.image.set_at((x,y), (255,255,255,0))
    def set_coord(self, new_coord):
        self.coord = new_coord