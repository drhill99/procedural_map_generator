from map import *
import pygame
from character import Character
import random
from dataclasses import dataclass
from map_utilities import *
import threading

pygame.init()


TILE_SIZE = 256
MAP_HEIGHT = 40
MAP_WIDTH = 40
VIEW_WIDTH = 10
VIEW_HEIGHT = 5
map_details = MapDetails(
    tile_size=TILE_SIZE,
    map_height=MAP_HEIGHT,
    map_width=MAP_WIDTH,
    px_height=32*40,
    px_width=32*40,
)

PIXEL_HEIGHT = TILE_SIZE * MAP_HEIGHT
PIXEL_WIDTH = TILE_SIZE * MAP_WIDTH
screen = pygame.display.set_mode((VIEW_WIDTH * TILE_SIZE, VIEW_HEIGHT * TILE_SIZE))
# screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("My game")

clock = pygame.time.Clock()

running = True

floor_texture = pygame.image.load("assets/cobble_stone.png").convert()
map = Map(height=40, width=40, num_floors=1)
map.build_map()
tower = map.get_tower()

wall_tiles: dict = None
for floor in tower:
    wall_tiles = gen_walls(floor, map_details)
wall_tile = pygame.image.load("assets/256wall.png").convert()
floor_textures = {
    0: floor_texture,
    90: pygame.transform.rotate(floor_texture, 90),
    180: pygame.transform.rotate(floor_texture, 180),
    270: pygame.transform.rotate(floor_texture, 270)
}
floor_idx = 0
actors = {}
avatar = Character(map.start_coord)
actors[avatar.coord] = avatar.image

camera = Camera(MAP_WIDTH, MAP_HEIGHT)
camera.x = max(0, min(avatar.coord[0] - VIEW_WIDTH // 2, MAP_WIDTH - VIEW_WIDTH))
camera.y = max(0, min(avatar.coord[1] - VIEW_HEIGHT // 2, MAP_HEIGHT - VIEW_HEIGHT))
while running:
    direction = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                direction = "up"
            elif event.key == pygame.K_DOWN:
                direction = "down"
            elif event.key == pygame.K_LEFT:
                direction = "left"
            elif event.key == pygame.K_RIGHT:
                direction = "right"

    if direction is not None:
        old_coord = avatar.coord
        if map.move_actor(floor_idx, avatar, direction):
            new_coord = avatar.coord
            actors[new_coord] = actors.pop(old_coord)

    camera.x = max(0, min(avatar.coord[0] - VIEW_WIDTH // 2, MAP_WIDTH - VIEW_WIDTH))
    camera.y = max(0, min(avatar.coord[1] - VIEW_HEIGHT // 2, MAP_HEIGHT - VIEW_HEIGHT))
    screen.fill((0,0,0))

    for floor in tower:
        for row in floor:
            for tile in row:
                if isinstance(tile, Tile):
                    world_x, world_y = tile.get_coord()
                    # x = x * TILE_SIZE
                    # y = y * TILE_SIZE
                    screen_x = (world_x - camera.x) * TILE_SIZE
                    screen_y = (world_y - camera.y) * TILE_SIZE

                    if tile.get_type() == WALL:
                        screen.blit(
                            # wall_tiles[tile.tot_adjacency],
                            wall_tile,
                            (screen_x, screen_y)
                        )
                    else:
                         pygame.draw.rect(
                                screen,
                                (180,180,180),
                                (screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                            )
    for (world_x, world_y), image in actors.items():
        screen_x = (world_x - camera.x) * TILE_SIZE
        screen_y = (world_y - camera.y) * TILE_SIZE
        screen.blit(
            image,
            (screen_x, screen_y)
        )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
