# libraries
import pygame
import random
import math
from dataclasses import dataclass
from pynput import keyboard
# local imports
from map import Map
from tile import Tile
from character import *
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

def render_first_person(
    screen,
    floor: list,
    avatar: Character,
    wall_texture,
    render_distance=8
):
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    FOV =math.radians(70)

    focal_length = (
        screen_width / 2
    ) / math.tan(FOV / 2)

    #
    # background
    #

    # ceiling/sky
    pygame.draw.rect(
        screen,
        (40,40,50),
        (0, 0, screen_width, screen_height // 2)
    )

    # distant floor background
    pygame.draw.rect(
        screen,
        (50,50,40),
        (
            0,
            screen_height // 2,
            screen_width,
            screen_height // 2
        )
    )

    #
    # player location
    #

    player_tile_x, player_tile_y = avatar.coord

    camera_z = 0.5
    # put camera in center of tile
    player_x = player_tile_x + camera_z
    player_y = player_tile_y + camera_z

    player_angle = avatar.angle

    forward_x = math.sin(player_angle)
    forward_y = -math.cos(player_angle)

    CAMERA_BACK_OFFSET = 0.75

    camera_x = player_x - forward_x * CAMERA_BACK_OFFSET
    camera_y = player_y - forward_y * CAMERA_BACK_OFFSET

    floor_z = 0
    ceiling_z = 1
    world_z = 1.0


    renderables = []

    #
    # examine only nearby tiles
    #

    min_x = max(
        0, player_tile_x - render_distance
    )

    max_x = min(
        len(floor[0]),
        player_tile_x + render_distance + 1
    )

    min_y = max(
        0,
        player_tile_y - render_distance
    )

    max_y = min(
        len(floor), 
        player_tile_y + render_distance + 1
    )

    for y in range(min_y, max_y):
        for x in range(min_x, max_x):

            tile = floor[y][x]

            #
            # distance used for painter sorting
            #

            center_x = x + 0.5
            center_y = y + 0.5

            dx = center_x - camera_x
            dy = center_y - camera_y

            distance = math.sqrt(
                (dx**2)+(dy**2)
            )

            #
            # FLOOR
            #
            if tile.get_type() == FLOOR:
                floor_polygon, ceiling_polygon = project_floor_tile(
                    x, y, world_z,
                    camera_x, camera_y, camera_z, player_angle,
                    screen_width, screen_height,
                    focal_length,
                    floor_z, ceiling_z
                )
                if floor_polygon is not None:

                    renderables.append(
                        (
                            distance,
                            "floor",
                            floor_polygon
                            # (80,70,60)
                        )
                    )
                if ceiling_polygon is not None:

                    renderables.append(
                        (
                            distance,
                            "ceiling",
                            ceiling_polygon
                        )
                    )

            #
            # WALL
            #

            elif tile.get_type() == WALL:

                faces = get_wall_faces(x, y)

                # wall center
                wall_center_x = x + 0.5
                wall_center_y = y + 0.5

                dx = camera_x - wall_center_x
                dy = camera_y - wall_center_y

                # faces returned in:
                # 0 = north
                # 1 = east
                # 2 = south
                # 3 = west

                visible_faces = []

                if camera_y < y:
                    visible_faces.append(faces[0])

                if camera_x > x + 1:
                    visible_faces.append(faces[1])

                if camera_y > y + 1:
                    visible_faces.append(faces[2])

                if camera_x < x:
                    visible_faces.append(faces[3])

                for face in visible_faces:

                    polygon = project_face(
                        face,
                        camera_x,
                        camera_y,
                        player_angle,
                        screen_width,
                        screen_height,
                        focal_length
                    )

                    if polygon is not None:
                        renderables.append(
                            (
                                distance,
                                "wall",
                                polygon
                                # (120, 120, 120)
                            )
                        )
            #
            # Painters algorithm
            #
            # far things first
            # near things last
            #

    renderables.sort(
        key=lambda item: item[0],
        reverse=True
    )

    for distance, surface_type, polygon in renderables:
        
        # pygame.draw.polygon(
        #     screen,
        #     color,
        #     polygon
        # )

        # pygame.draw.polygon(
        #     screen,
        #     (30,30,30),
        #     polygon,
        #     1
        # )
        if surface_type == "wall":
            textured = draw_textured_wall_perspective(
                screen,
                wall_texture,
                polygon
            )

            if not textured:
                pygame.draw.polygon(
                    screen,
                    (120,120,120),
                    polygon
                )
        elif surface_type == "floor":
            pygame.draw.polygon(
                screen,
                (80,70,60),
                polygon
            )
        elif surface_type == "ceiling":
            pygame.draw.polygon(
                screen,
                (25,25,25),
                polygon
            )

        # pygame.draw.polygon(
        #     screen,
        #     (30,30,30),
        #     polygon,
        #     1
        # )

def world_to_camera(
    world_x, world_y, world_z,
    camera_x, camera_y,
    player_angle,
    eye_height=0.5
):
    dx = world_x - camera_x
    dy = world_y - camera_y

    forward_x = math.sin(player_angle)
    forward_y = -math.cos(player_angle)

    right_x = math.cos(player_angle)
    right_y = math.sin(player_angle)

    camera_side = (
        dx * right_x
        + dy * right_y
    )

    camera_depth = (
        dx * forward_x
        + dy * forward_y
    )

    camera_height = (
        world_z - eye_height
    )

    return (
        camera_side,
        camera_depth,
        camera_height
    )

def clip_polygon_near_plane(
    points,
    near_plane=0.05
):
    clipped = []

    if not points:
        return clipped

    previous = points[-1]
    previous_inside = previous[1] >= near_plane

    for current in points:

        current_inside = (
            current[1] >= near_plane
        )

        if current_inside != previous_inside:
            # edge crosses near plane
            t = (
                (near_plane - previous[1])
                /
                (current[1] - previous[1])
            )

            intersection_side = (
                previous[0]
                + t * (current[2] - previous[2])
            )

            intersection_height = (
                previous[2]
                + t * (current[2] - previous[2])
            )

            clipped.append(
                (
                    intersection_side,
                    near_plane,
                    intersection_height
                )
            )
        if current_inside:
            clipped.append(current)

        previous = current
        previous_inside = current_inside

    return clipped
    
def camera_to_screen(
    camera_side, camera_depth, camera_height,
    screen_width, screen_height, focal_length
):
    screen_x = (
        screen_width / 2
        + (camera_side / camera_depth)
        * focal_length
    )

    screen_y = (
        screen_height / 2
        + (camera_height / camera_depth)
        * focal_length
    )

    return (
        int(screen_x),
        int(screen_y)
    )

def project_point(
    world_x,
    world_y,
    world_z,
    camera_x,
    camera_y,
    camera_z,
    player_angle,
    screen_width,
    screen_height,
    focal_length,
    eye_height=0.5
):

    # position relative to player
    dx = world_x - camera_x
    dy = world_y - camera_y
    dz = world_z - camera_z

    # # camera direction
    # forward_x = math.cos(player_angle)
    # forward_y = math.sin(player_angle)

    # # camera rigtht direction
    # right_x = -math.sin(player_angle)
    # right_y = math.cos(player_angle)

    forward_x = math.sin(player_angle)
    forward_y = -math.cos(player_angle)

    right_x = math.cos(player_angle)
    right_y = math.sin(player_angle)

    # convert world coordiante into comera-relative coordinate
    camera_horizontal = dx * right_x + dy * right_y
    camera_depth = dx * forward_x + dy * forward_y

    # behind player / too close to projection plane
    if camera_depth <= 0.05:
    # if camera_depth <= 0.001:
        return None

    screen_center_x = screen_width / 2
    screen_center_y = screen_height / 2

    screen_x = (
        screen_center_x
        + (camera_horizontal / camera_depth) * focal_length
    )

    screen_y = (
        screen_center_y
        - (dz / camera_depth) * focal_length
    )

    return (int(screen_x), int(screen_y))

def project_floor_tile(
    x, y, world_z,
    camera_x, camera_y, camera_z, player_angle,
    screen_width, screen_height,
    focal_length,
    floor_z, ceiling_z
):

    floor_relative_z = floor_z - camera_z
    ceiling_relative_z = ceiling_z - camera_z

    floor_corners = [
        (x,     y,      floor_z),
        (x + 1, y,      floor_z),
        (x + 1, y + 1,  floor_z),
        (x,     y + 1,  floor_z)
    ]

    ceiling_corners = [
        (x,     y,      ceiling_z),
        (x + 1, y,      ceiling_z),
        (x + 1, y + 1,  ceiling_z),
        (x,     y + 1,  ceiling_z)
    ]
    
    floor_projected = []
    ceiling_projected = []

    for wx, wy, wz in floor_corners:
        point = project_point(
            wx, wy, wz,
            camera_x, camera_y, camera_z,
            player_angle,
            screen_width, screen_height,
            focal_length
        )

        if point is None:
            return None, None

        floor_projected.append(point)

    for wx, wy, wz in ceiling_corners:
        point = project_point(
            wx, wy, wz,
            camera_x, camera_y, camera_z, 
            player_angle,
            screen_width, screen_height,
            focal_length
        )

        if point is None:
            return None, None

        ceiling_projected.append(point)

    return floor_projected, ceiling_projected

def get_wall_faces(x, y):
    return [
        # north face
        [
            (x,     y, 0),
            (x + 1, y, 0),
            (x + 1, y, 1),
            (x,     y, 1),
        ],

        # east face
        [
            (x + 1, y,     0),
            (x + 1, y + 1, 0),
            (x + 1, y + 1, 1),
            (x + 1, y,     1),
        ],

        # south face
        [
            (x + 1, y + 1, 0),
            (x,     y + 1, 0),
            (x,     y + 1, 1),
            (x + 1, y + 1, 1),
        ],

        # west face
        [
            (x, y + 1, 0),
            (x, y,     0),
            (x, y,     1),
            (x, y + 1, 1),
        ],
    ]

# def project_face(
#     face,
#     camera_x, camera_y, player_angle,
#     screen_width, screen_height,
#     focal_lenght
# ):
#     projected = []

#     for wx, wy, wz in face:

#         point = project_point(
#             wx, wy, wz,
#             camera_x, camera_y, player_angle,
#             screen_width, screen_height,
#             focal_lenght
#         )

#         if point is None:
#             return None
#         projected.append(point)

#     return projected

def project_face(
    face,
    camera_x,
    camera_y,
    player_angle,
    screen_width,
    screen_height,
    focal_length
):
    camera_points = []

    for wx, wy, wz in face:

        camera_points.append(
            world_to_camera(
                wx,
                wy,
                wz,
                camera_x,
                camera_y,
                player_angle
            )
        )

    camera_points = clip_polygon_near_plane(
        camera_points
    )

    if len(camera_points) < 3:
        return None

    projected = []

    for side, depth, height in camera_points:

        projected.append(
            camera_to_screen(
                side,
                depth,
                height,
                screen_width,
                screen_height,
                focal_length
            )
        )

    return projected

def vector_to_direction(dx, dy):
    directions = {
        (0, -1): "up",
        (1, 0): "right",
        (0, 1): "down",
        (-1, 0): "left",
    }

    return directions[(dx, dy)]

# def render_top_down(
#     surface,
#     floor,
#     avatar,
#     camera,
#     visible_tiles,
#     tile_size,
#     wall_tile
# ):
#     TILE_SIZE = tile_size
#     tile_visibility = {}
#     for row in floor:
#             for tile in row:
#                 if isinstance(tile, Tile):
#                     world_x, world_y = tile.get_coord()
#                     # x = x * TILE_SIZE
#                     # y = y * TILE_SIZE
#                     screen_x = int((world_x - camera.x) * TILE_SIZE)
#                     screen_y = int((world_y - camera.y) * TILE_SIZE)

#                     target_alpha = 1.0 if tile.coord in visible_tiles else 0.0

#                     current_alpha = tile_visibility.get(tile.coord, 0.0)

#                     current_alpha += (target_alpha - current_alpha) * 0.25

#                     tile_visibility[tile.coord] = current_alpha

#                     alpha = int(current_alpha * 255)

#                     if alpha <= 0:
#                         continue

#                     if tile.coord in visible_tiles:
#                         tile_type = tile.get_type()
#                         if tile_type == WALL:
#                             wall_surface = wall_tile.copy()
#                             wall_surface.set_alpha(alpha)
#                             surface.blit(
#                                 # wall_tiles[tile.tot_adjacency],
#                                 wall_surface,
#                                 (screen_x, screen_y)
#                             )
#                         elif tile_type == FLOOR:
#                             floor_surface = pygame.Surface(
#                                 (TILE_SIZE, TILE_SIZE),
#                                 pygame.SRCALPHA
#                             )
#                             floor_surface.fill((180,180,180,alpha))
#                             surface.blit(
#                                 floor_surface,
#                                 (screen_x, screen_y)
#                             )
#                         elif tile_type == ENDPOINT:
#                             ep_surface = pygame.Surface(
#                                 (TILE_SIZE, TILE_SIZE),
#                                 pygame.SRCALPHA
#                             )
#                             ep_surface.fill((255,255,255,alpha))
#                             surface.blit(
#                                 ep_surface,
#                                 (screen_x, screen_y)
#                             )
#                     # else:
#                     #     surface.blit(
#                     #             # wall_tiles[tile.tot_adjacency],
#                     #             wall_tile,
#                     #             (screen_x, screen_y)
#                     #         )
#     screen_x = int((avatar.render_x - camera.x) * TILE_SIZE)
#     screen_y = int((avatar.render_y - camera.y) * TILE_SIZE)

#     # for (world_x, world_y), image in actors.items():
#     #     screen_x = (world_x - camera.x) * TILE_SIZE
#     #     screen_y = (world_y - camera.y) * TILE_SIZE
#     surface.blit(
#         avatar.image,
#         (screen_x, screen_y)
#     )

# def render_top_down(
#     surface,
#     floor,
#     avatar,
#     camera,
#     visible_tiles,
#     tile_size,
#     wall_tile
# ):
#     surface.fill((0, 0, 0))

#     for row in floor:
#         for tile in row:

#             if not isinstance(tile, Tile):
#                 continue

#             if tile.coord not in visible_tiles:
#                 continue

#             world_x, world_y = tile.get_coord()

#             screen_x = int(
#                 (world_x - camera.x) * tile_size
#             )

#             screen_y = int(
#                 (world_y - camera.y) * tile_size
#             )

#             tile_type = tile.get_type()

#             if tile_type == WALL:

#                 surface.blit(
#                     wall_tile,
#                     (screen_x, screen_y)
#                 )

#             elif tile_type == FLOOR:

#                 pygame.draw.rect(
#                     surface,
#                     (180, 180, 180),
#                     (
#                         screen_x,
#                         screen_y,
#                         tile_size,
#                         tile_size
#                     )
#                 )

#             elif tile_type == ENDPOINT:

#                 pygame.draw.rect(
#                     surface,
#                     (255, 255, 255),
#                     (
#                         screen_x,
#                         screen_y,
#                         tile_size,
#                         tile_size
#                     )
#                 )

#     screen_x = int(
#         (avatar.render_x - camera.x) * tile_size
#     )

#     screen_y = int(
#         (avatar.render_y - camera.y) * tile_size
#     )
#     # avatar_surface = pygame.transform.scale(
#     #     avatar.image,
#     #     (tile_size, tile_size)
#     # )
#     # rotated_avatar = pygame.transform.rotate(
#     #     avatar_surface,
#     #     -math.degrees(avatar.angle)
#     # )
#     # surface.blit(
#     #     rotated_avatar,
#     #     (screen_x, screen_y)
#     # )
#     surface.blit(
#         pygame.transform.scale(
#             avatar.image,
#             (tile_size, tile_size)
#         ),
#         (screen_x, screen_y)
#     )

def render_top_down(
    surface,
    floor,
    avatar,
    camera,
    visible_tiles,
    tile_size,
    wall_tile
):
    surface.fill((0, 0, 0))

    #
    # The logical viewport is still 10 x 5 tiles.
    #
    view_width = 10
    view_height = 5

    #
    # Determine a tile size that fits this surface.
    #
    render_tile_size = min(
        surface.get_width() // view_width,
        surface.get_height() // view_height
    )

    #
    # Center the 10x5 viewport inside the surface.
    #
    viewport_width = view_width * render_tile_size
    viewport_height = view_height * render_tile_size

    offset_x = (
        surface.get_width() - viewport_width
    ) // 2

    offset_y = (
        surface.get_height() - viewport_height
    ) // 2

    #
    # Scale wall texture to our debug tile size.
    #
    scaled_wall = pygame.transform.scale(
        wall_tile,
        (render_tile_size, render_tile_size)
    )

    for row in floor:
        for tile in row:

            if not isinstance(tile, Tile):
                continue

            if tile.coord not in visible_tiles:
                continue

            world_x, world_y = tile.get_coord()

            screen_x = (
                int((world_x - camera.x) * render_tile_size)
                + offset_x
            )

            screen_y = (
                int((world_y - camera.y) * render_tile_size)
                + offset_y
            )

            #
            # Don't bother drawing tiles outside the surface.
            #
            if (
                screen_x + render_tile_size < 0
                or screen_x >= surface.get_width()
                or screen_y + render_tile_size < 0
                or screen_y >= surface.get_height()
            ):
                continue

            tile_type = tile.get_type()

            if tile_type == WALL:

                surface.blit(
                    scaled_wall,
                    (screen_x, screen_y)
                )

            elif tile_type == FLOOR:

                pygame.draw.rect(
                    surface,
                    (180, 180, 180),
                    (
                        screen_x,
                        screen_y,
                        render_tile_size,
                        render_tile_size
                    )
                )

            elif tile_type == ENDPOINT:

                pygame.draw.rect(
                    surface,
                    (255, 255, 255),
                    (
                        screen_x,
                        screen_y,
                        render_tile_size,
                        render_tile_size
                    )
                )

    #
    # Avatar position
    #
    avatar_x = (
        int((avatar.render_x - camera.x) * render_tile_size)
        + offset_x
    )

    avatar_y = (
        int((avatar.render_y - camera.y) * render_tile_size)
        + offset_y
    )

    avatar_surface = pygame.transform.scale(
        avatar.image,
        (render_tile_size, render_tile_size)
    )

    rotated_avatar = pygame.transform.rotate(
        avatar_surface,
        -math.degrees(avatar.angle)
    )

    surface.blit(
        rotated_avatar,
        (avatar_x, avatar_y)
    )

def relative_move(angle, movement):

    heading = round(math.degrees(angle)) % 360
    print(f"heading: {heading} movement: {movement}")
    movement_table = {

        # Facing NORTH
        0: {
            "forward":  "up",
            "backward": "down",
            "strafe_left":  "left",
            "strafe_right": "right",
        },

        # Facing EAST
        90: {
            "forward":  "right",
            "backward": "left",
            "strafe_left":  "up",
            "strafe_right": "down",
        },

        # Facing SOUTH
        180: {
            "forward":  "down",
            "backward": "up",
            "strafe_left":  "right",
            "strafe_right": "left",
        },

        # Facing WEST
        270: {
            "forward":  "left",
            "backward": "right",
            "strafe_left":  "down",
            "strafe_right": "up",
        },
    }

    return movement_table[heading][movement]

# def draw_textured_wall(
#     screen,
#     texture,
#     polygon
# ):
#     if len(polygon) != 4:
#         return False

#     #
#     # Our wall faces are expected to be:
#     #
#     # bottom-left
#     # bottom-right
#     # top-right
#     # top-left
#     #
#     p0, p1, p2, p3 = polygon

#     tex_width = texture.get_width()
#     tex_height = texture.get_height()

#     for tex_x in range(tex_width):

#         t = tex_x / (tex_width - 1)

#         #
#         # Interpolate along bottom edge
#         #
#         bottom_x = (
#             p0[0]
#             + (p1[0] - p0[0]) * t
#         )

#         bottom_y = (
#             p0[1]
#             + (p1[1] - p0[1]) * t
#         )

#         #
#         # Interpolate along top edge
#         #
#         top_x = (
#             p3[0]
#             + (p2[0] - p3[0]) * t
#         )

#         top_y = (
#             p3[1]
#             + (p2[1] - p3[1]) * t
#         )

#         #
#         # Grab one vertical column of texture
#         #
#         column = texture.subsurface(
#             tex_x,
#             0,
#             1,
#             tex_height
#         )

#         wall_height = abs(
#             int(bottom_y - top_y)
#         )

#         if wall_height <= 0:
#             continue

#         column = pygame.transform.scale(
#             column,
#             (1, wall_height)
#         )

#         #
#         # At cardinal camera angles these should normally
#         # be nearly the same X coordinate.
#         #
#         screen_x = int(
#             (bottom_x + top_x) / 2
#         )

#         screen_y = int(
#             min(top_y, bottom_y)
#         )

#         screen.blit(
#             column,
#             (screen_x, screen_y)
#         )

#     return True

def draw_textured_wall_perspective(
    screen,
    texture,
    polygon
):
    if len(polygon) != 4:
        return False

    p0, p1, p2, p3 = polygon

    tex_w = texture.get_width()
    tex_h = texture.get_height()

    left = max(
        0,
        int(min(p0[0], p3[0], p1[0], p2[0]))
    )

    right = min(
        screen.get_width() - 1,
        int(max(p0[0], p3[0], p1[0], p2[0]))
    )

    if right <= left:
        return False

    #
    # Which side is visually left/right?
    #
    if p0[0] <= p1[0]:
        bottom_left = p0
        bottom_right = p1
        top_left = p3
        top_right = p2
        flip_texture = False
    else:
        bottom_left = p1
        bottom_right = p0
        top_left = p2
        top_right = p3
        flip_texture = True

    width = bottom_right[0] - bottom_left[0]

    if abs(width) < 1:
        return False

    for screen_x in range(left, right + 1):

        #
        # Horizontal location across wall.
        #
        t = (
            (screen_x - bottom_left[0])
            / width
        )

        t = max(0.0, min(1.0, t))

        #
        # Top/bottom positions at this screen X.
        #
        bottom_y = (
            bottom_left[1]
            + (bottom_right[1] - bottom_left[1]) * t
        )

        top_y = (
            top_left[1]
            + (top_right[1] - top_left[1]) * t
        )

        top = max(
            0,
            int(min(top_y, bottom_y))
        )

        bottom = min(
            screen.get_height() - 1,
            int(max(top_y, bottom_y))
        )

        height = bottom - top

        if height <= 0:
            continue

        if flip_texture:
            tex_x = int(
                (1.0 - t) * (tex_w - 1)
            )
        else:
            tex_x = int(
                t * (tex_w - 1)
            )

        #
        # Grab one source column.
        #
        column = texture.subsurface(
            tex_x,
            0,
            1,
            tex_h
        )

        #
        # Scale that column to EXACTLY cover this
        # screen column.
        #
        column = pygame.transform.scale(
            column,
            (1, height)
        )

        screen.blit(
            column,
            (screen_x, top)
        )

    return True

def build_wall_texture(row_textures):
    wall = pygame.Surface((256, 256))

    y = 0

    while y < 256:
        candidates = [
            texture
            for texture in row_textures
            if y + texture.get_height() <= 256
        ]

        if not candidates:
            break

        row = random.choice(candidates)

        wall.blit(
            row,
            (0, y)
        )

        y += row.get_height()

    return wall