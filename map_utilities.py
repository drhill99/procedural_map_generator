import pygame
from map import Map
from tile import Tile
from dataclasses import dataclass
from character import *
from pynput import keyboard
from defines import *

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
def has_los(floor, start, target):
    previous = None
    for x, y in bresenham(start, target):
        if (x,y) == start:
            previous = (x,y)
            continue
        if previous is not None:
            prev_x, prev_y = previous
            dx = x - prev_x
            dy = y - prev_y

            if dx != 0 and dy != 0:
                side_1: Tile = floor[prev_y][prev_x + dx]
                side_2: Tile = floor[prev_y + dy][prev_x]

                if (
                    side_1.get_type() == WALL
                    and
                    side_2.get_type() == WALL
                ):
                    return False
        tile: Tile = floor[y][x]

        if tile.get_type() == WALL:
            return (x,y) == target

        previous = (x,y)
    return True
def bresenham(start, end):
    x0, y0 = start
    x1, y1 = end

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1

    error = dx - dy

    while True:
        yield (x0, y0)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * error

        if e2 > -dy:
            error -= dy
            x0 += sx

        if e2 < dx:
            error += dx
            y0 += sy

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




