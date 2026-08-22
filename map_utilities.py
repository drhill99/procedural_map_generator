import pygame
from map import Map
from tile import Tile
from dataclasses import dataclass
from character import *
from pynput import keyboard
@dataclass
class MapDetails:
    tile_size: int
    map_height: int
    map_width: int
    px_height: int
    px_width: int

    def __iter__(self):
        yield self.tile_size
        yield self.map_height
        yield self.map_width
        yield self.px_height
        yield self.px_width

class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        
def gen_walls(floor: list, map_details: MapDetails):
    tile_size = map_details.tile_size
    # map_height = map_details.map_height
    # map_width = map_details.map_width
    # px_height = map_details.px_height
    # px_width  = map_details.px_width

    wall_tiles = {}
    for tile_row in floor:
        for tile in tile_row:
            if isinstance(tile, Tile):
                adjacencies = tile.adjacencies
                adjacency_value = tile.tot_adjacency

            surface = pygame.Surface((tile_size, tile_size))

            surface.fill((80,80,80))
            if adjacency_value == 255:
                surface.fill((0,0,0))
            else:
                
                flipped_adjacencies = [not x for x in adjacencies]

                for idx, isAdj in enumerate(flipped_adjacencies):

                    match(idx):
                        case(0):
                            # N
                            if isAdj:
                                pygame.draw.rect(
                                    surface,
                                    (110,110,110),
                                    (0,0,tile_size,4)
                                )
                        case(1):
                            # NE
                            if isAdj:
                                pygame.draw.rect(
                                    surface,
                                    (150,150,150),
                                    (tile_size - 4, 0, 4, 4)
                                )
                        case(2):
                            # E
                            if isAdj:
                                pygame.draw.rect(
                                    surface,
                                    (110,110,110),
                                    (tile_size - 4, 4, 4, tile_size - 8)
                                )
                        case(3):
                            if isAdj:
                                # SE
                                pygame.draw.rect(
                                    surface,
                                    (150,150,150),
                                    (tile_size - 4, tile_size - 4, 4, 4)
                                )
                        case(4):
                            if isAdj:
                            # S
                                pygame.draw.rect(
                                    surface,
                                    (110,110,110),
                                    (0, tile_size - 4, tile_size, 4)
                                )
                        case(5):
                            if isAdj:
                                # SW
                                pygame.draw.rect(
                                    surface,
                                    (150,150,150),
                                    (0, tile_size - 4, 4, 4)
                                )
                        case(6):
                            if isAdj:
                                # W
                                pygame.draw.rect(
                                    surface,
                                    (110,110,110),
                                    (0, 4, 4, tile_size - 4)
                                )
                        case(7):
                            if isAdj:
                                # NW
                                pygame.draw.rect(
                                    surface,
                                    (150,150,150),
                                    (0, 0, 4, 4)
                            )
            wall_tiles[adjacency_value] = surface
    return wall_tiles




