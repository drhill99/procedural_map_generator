from map import *
import pygame
from character import Character
import random
from dataclasses import dataclass
from map_utilities import *
import threading
from defines import *

pygame.init()


TILE_SIZE = 256
MAP_HEIGHT = 80
MAP_WIDTH = 80
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
map = Map(height=MAP_HEIGHT, width=MAP_WIDTH, num_floors=1)
map.build_map()
tower = map.get_tower()
map.display_map()

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
tile_visibility = {}
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

    avatar.render_x += (avatar.coord[0] - avatar.render_x) * 0.15
    avatar.render_y += (avatar.coord[1] - avatar.render_y) * 0.15

    visible_tiles = set() 

    player_x, player_y = avatar.coord
    radius = 5
    for y in range(player_y - radius, player_y + radius + 1):
        for x in range(player_x - radius, player_x + radius + 1):
            if not (0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT):
                continue
            if abs(x - player_x) + abs(y - player_y) > radius:
                continue
            if has_los(floor, avatar.coord, (x,y)):
                visible_tiles.add((x,y))


    target_x = max(0, min(avatar.coord[0] - VIEW_WIDTH // 2, MAP_WIDTH - VIEW_WIDTH))
    target_y = max(0, min(avatar.coord[1] - VIEW_HEIGHT // 2, MAP_HEIGHT - VIEW_HEIGHT))

    camera.x += (target_x - camera.x) * 0.1
    camera.y += (target_y - camera.y) * 0.1
    # camera.x = max(0, min(avatar.coord[0] - VIEW_WIDTH // 2, MAP_WIDTH - VIEW_WIDTH))
    # camera.y = max(0, min(avatar.coord[1] - VIEW_HEIGHT // 2, MAP_HEIGHT - VIEW_HEIGHT))
    screen.fill((0,0,0))
    for floor in tower:
        for row in floor:
            for tile in row:
                if isinstance(tile, Tile):
                    world_x, world_y = tile.get_coord()
                    # x = x * TILE_SIZE
                    # y = y * TILE_SIZE
                    screen_x = int((world_x - camera.x) * TILE_SIZE)
                    screen_y = int((world_y - camera.y) * TILE_SIZE)

                    target_alpha = 1.0 if tile.coord in visible_tiles else 0.0

                    current_alpha = tile_visibility.get(tile.coord, 0.0)

                    current_alpha += (target_alpha - current_alpha) * 0.25

                    tile_visibility[tile.coord] = current_alpha

                    alpha = int(current_alpha * 255)

                    if alpha <= 0:
                        continue

                    if tile.coord in visible_tiles:
                        tile_type = tile.get_type()
                        if tile_type == WALL:
                            surface = wall_tile.copy()
                            surface.set_alpha(alpha)
                            screen.blit(
                                # wall_tiles[tile.tot_adjacency],
                                surface,
                                (screen_x, screen_y)
                            )
                        elif tile_type == FLOOR:
                            surface = pygame.Surface(
                                (TILE_SIZE, TILE_SIZE),
                                pygame.SRCALPHA
                            )
                            surface.fill((180,180,180,alpha))
                            screen.blit(
                                surface,
                                (screen_x, screen_y)
                            )
                        elif tile_type == ENDPOINT:
                            surface = pygame.Surface(
                                (TILE_SIZE, TILE_SIZE),
                                pygame.SRCALPHA
                            )
                            surface.fill((255,255,255,alpha))
                            screen.blit(
                                surface,
                                (screen_x, screen_y)
                            )
                    # else:
                    #     screen.blit(
                    #             # wall_tiles[tile.tot_adjacency],
                    #             wall_tile,
                    #             (screen_x, screen_y)
                    #         )
    screen_x = int((avatar.render_x - camera.x) * TILE_SIZE)
    screen_y = int((avatar.render_y - camera.y) * TILE_SIZE)

    # for (world_x, world_y), image in actors.items():
    #     screen_x = (world_x - camera.x) * TILE_SIZE
    #     screen_y = (world_y - camera.y) * TILE_SIZE
    screen.blit(
        avatar.image,
        (screen_x, screen_y)
    )

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
