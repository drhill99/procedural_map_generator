import pygame

class Character:
    def __init__(self, coord: tuple):
        self.coord = coord
        self.image = pygame.image.load("assets/avatar.png").convert_alpha()
        for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    if self.image.get_at((x,y))[:3] == (255,255,255):
                        self.image.set_at((x,y), (255,255,255,0))
    def set_coord(self, new_coord):
        self.coord = new_coord