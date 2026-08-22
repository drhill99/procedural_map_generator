from tile import Tile
import math
import random
from colorama import init, Fore, Back, Style
from character import Character

init()

WALL = f"{Fore.BLACK}{Back.LIGHTBLACK_EX}#{Style.RESET_ALL}"
DELETED = f"{Fore.RED}D{Style.RESET_ALL}"
EXPANDED = f"{Fore.GREEN}E{Style.RESET_ALL}"
NEW = f"{Fore.MAGENTA}N{Style.RESET_ALL}"
FLOOR = f"{Fore.LIGHTWHITE_EX}{Back.BLACK}+{Style.RESET_ALL}"
tile_type_map = {
    " ": "floor",
    "#": "wall"
}
class Map:
    def __init__(self, height, width, num_floors):
        self.height = height
        self.width = width
        self.area = self.height * self.width
        self.num_floors = num_floors
        self.tower = []
        self.unique_adjacencies = set()
        self.start_coord = None
        self.moves = {
            "up": (0,-1),
            "down": (0,1),
            "left": (-1,0),
            "right": (1,0),
        }
        self.diag_moves = {
            "up_left": (-1, -1),
            "up_right": (1, -1),
            "down_left": (-1, 1),
            "down_right": (1, 1)
        }
        self.adjacencies = {
            0: (0,-1),
            1: (1,-1),
            2: (1, 0),
            3: (1, 1),
            4: (0, 1),
            5: (-1, 1),
            6: (-1, 0),
            7: (-1, -1)
        }
        self.all_moves = self.moves | self.diag_moves
        self.already_visited_coords = []
        self.map_area_usage = 0.6
        self.walls = set()
    def build_map(self):
        self.tower = [self.build_floor() for _ in range(self.num_floors)]
        self.build_path()
        # self.display_map()
    def get_tower(self):
        return self.tower
    def build_floor(self):
        floor = [[Tile(WALL, (x,y)) for x in range(self.width)] for y in range(self.height)]
        return floor
    def display_map(self):
        for floor in self.tower:
            for row in floor:
                display: str = ""
                for tile in row:
                    # display += f"{tile.get_type()}, {tile.get_coord()}, "
                    display += f"{tile.get_type()} "
                print(display)
    def build_path(self, inc_start_coord = None, rerun: bool = None):
        if rerun is None:
            self.already_visited_coords = []
        current_tile = None
        for floor in self.tower:
            previous_direction = None
            consecutive_moves = 0

            side = random.randint(1,4)
            start_coord = None
            match side:
                case 1:
                    start_coord = (random.randint(0,self.width-1), 0)
                case 2:
                    start_coord = (self.width - 1, random.randint(0,self.height-1))
                case 3:
                    start_coord = (random.randint(0,self.height-1), self.height - 1)
                case 4:
                    start_coord = (0, random.randint(0,self.height-1))
            start_coord = start_coord if inc_start_coord is None else inc_start_coord
            self.start_coord = start_coord
            self.already_visited_coords.append(start_coord)
            current_coord = start_coord
            current_tile = floor[start_coord[1]][start_coord[0]]
            current_tile.set_type(FLOOR)
            # floor[start_coord[0]][start_coord[1]].set_type(FLOOR)
            # for _ in range(50):
            while True:
                # print(f"current_coord: {current_coord}")
                # print("current_map")
                # self.display_map()
                possible_moves = self.check_moves(floor, current_coord)
                if len(possible_moves) == 0:
                    break
                if consecutive_moves >= 4:
                    if len(possible_moves) > 1:
                        if previous_direction in possible_moves:
                            possible_moves.remove(previous_direction)
                
                next_move = random.choice(possible_moves)
                if next_move == previous_direction:
                    consecutive_moves += 1
                # print(f"moving {next_move}")
                shift = self.moves[next_move]
                next_coord = (
                    current_coord[0]+shift[0],
                    current_coord[1]+shift[1] 
                )
                current_coord = next_coord
                # if current_coord in self.walls:
                #     self.walls.remove(current_coord)
                self.already_visited_coords.append(current_coord)
                # print(f"next_coord: {next_coord}")
                next_tile = floor[next_coord[1]][next_coord[0]]
                current_tile = next_tile
                current_tile.set_type(FLOOR)
                # check and save neighbor alls
                # self.save_neighbor_walls(floor, next_coord)
                # for wall_coord in self.walls:
                #     print(f"wall coord: {wall_coord}")

            floor_tiles = 0
            for row in floor:
                for tile_type in row:
                    tile_type = tile_type.get_type()
                    # print(f"tile_type: {tile_type}")
                    floor_tiles += 1 if tile_type == FLOOR else 0
            tile_utilization = floor_tiles / self.area
        
            # print(f"used area: {tile_utilization}, area useage threshold: {self.map_area_usage} of total area: {self.area}")
            if tile_utilization > self.map_area_usage:
                return
            else:
                # farthest_coord = self.find_furthest_visited_tile(start_coord)
                best_tile: Tile = self.find_best_candidate_tile(floor)
                new_start_coord = best_tile.get_coord()
                self.build_path(inc_start_coord=new_start_coord, rerun=True)
            # print("before orphan expansion")
            for row in floor:
                for tile in row:
                    if tile.get_type() == WALL:
                        self.walls.add(tile.get_coord())
            for coord in self.walls:
                x, y = coord
                tile: Tile = floor[y][x]
                # print("tile", x, y)
                for idx, (dx, dy) in self.adjacencies.items():
                    tx = x + dx
                    ty = y + dy
                    adj_tile: Tile = None
                    try:
                        adj_tile: Tile = floor[ty][tx]
                    except:
                        pass
                    if adj_tile is not None:
                        adj_tile_is_wall = adj_tile.get_type() == WALL
                        tile.update_adj(idx, adj_tile_is_wall)
                tile.calc_adj()
                self.unique_adjacencies.add(tuple(tile.adjacencies))
                            
            # self.display_map()

            self.remove_orphaned_wall_tiles(floor)
    def check_tile_sides(self, floor: list, tile: Tile):
        x, y = tile.get_coord()
        for (dx, dy) in self.moves.values():
            trans_x = x + dx
            trans_y = y + dy
            pass
    def check_moves(self, floor: list, coords):
        x, y = coords
        possible_moves = []

        for movement, (dx, dy) in self.moves.items():
            new_x = x + dx
            new_y = y + dy

            # Candidate tile must be inside the map
            if not (0 <= new_x < self.width and 0 <= new_y < self.height):
                continue

            # Don't revisit a tile we've already carved
            if (new_x, new_y) in self.already_visited_coords:
                continue

            # Look one more tile beyond the candidate
            beyond_x = new_x + dx
            beyond_y = new_y + dy

            # If the tile beyond is outside the map, that's okay.
            # We're approaching the edge.
            if 0 <= beyond_x < self.width and 0 <= beyond_y < self.height:
                if floor[beyond_y][beyond_x].get_type() == FLOOR:
                    continue

            possible_moves.append(movement)

        return possible_moves
    
    def find_furthest_visited_tile(self, start_point):
        farthest: float = 0.0
        farthest_coord = start_point
        for (x, y) in self.already_visited_coords:
            distance = math.sqrt((math.pow(x-start_point[0],2))+(math.pow(y-start_point[1],2)))
            # print(f"distance: {distance}")
            if distance > farthest:
                farthest = distance
                farthest_coord = (x,y)
            # print(f"farthest: {farthest}")
        return farthest_coord
    
    def find_best_candidate_tile(self, floor: list):
        best_tile = None
        most_unused_space = 0
        for x, y in self.already_visited_coords:
            available_moves = self.check_moves(floor, (x,y))
            # print(f"available moves: {available_moves}")
            for move in available_moves:
                dx, dy = self.moves[move]
                unused_space = 0
                temp_x = x
                temp_y = y
                while True:
                    # if temp_x >= self.height - 1 or temp_y >= self.width - 1 or temp_x <= 0 or temp_y <= 0:
                    #     break
                    temp_x += dx
                    temp_y += dy

                    if not (
                        0 <= temp_x < self.width
                        and 
                        0 <= temp_y < self.height
                    ): 
                        break

                    tile: Tile = floor[temp_y][temp_x]

                    # tile_type = tile.get_type()
                    if tile.get_type() == FLOOR:
                        break

                    unused_space += 1

                if unused_space > most_unused_space:
                    most_unused_space = unused_space
                    best_tile = floor[y][x]
        return best_tile
    def remove_orphaned_wall_tiles(self, floor):
        # print(f"wall count: {len(self.walls)}")
        orphaned_walls = set()
        for (x, y) in self.walls:
            if self.check_orphan_status(floor, (x,y)):
                floor[y][x].set_type(FLOOR)

    def save_neighbor_walls(self, floor, coords):
        x, y = coords
        for _, (dx, dy) in self.all_moves.items():
            # get transformation
            temp_x = x + dx
            temp_y = y + dy
            # check the resulting transformation tile for wall/floor status.
            try:
                neighbor_tile: Tile = floor[temp_y][temp_x]
                tile_type = neighbor_tile.get_type()
                if tile_type == WALL:
                    self.walls.add((temp_x, temp_y))
            except Exception as e:
                # print(f"Failed to get tile: {e}")
                pass

    def check_orphan_status(self, floor, coords):
        x, y = coords
        neighbor_floor_count = 0
        for (dx, dy) in self.all_moves.values():
            temp_x = x + dx
            temp_y = y + dy
            if temp_x < 0 or temp_y < 0:
                neighbor_floor_count += 1
                continue
            try:
                neighbor_tile: Tile = floor[temp_y][temp_x]
                tile_type = neighbor_tile.get_type()
                if tile_type == FLOOR:
                    neighbor_floor_count += 1
            except:
                pass    
        return neighbor_floor_count == 8
    
    def how_do_I_place_POI():
        #TODO I need to figure out how to determine interesting locations for POI:
        # monster encounters, treasure, bosses etc, stairs up and down, traps etc.
        # I need to recognize shapes in the path.
        pass

    def move_actor(self, floor_idx, avatar: Character, direction: str):
        print(f"attempting to move: {direction}")
        floor = self.tower[floor_idx]
        x, y = avatar.coord
        dx, dy = self.moves[direction]
        tx = x + dx
        ty = y + dy
        print(f"tx: {tx} ty: {ty}")
        if not (0 <= tx < self.width and 0 <= ty < self.height):
            print("Cannot move outside map")
            return False
        try:
            dest_tile: Tile = floor[ty][tx]
            if dest_tile.get_type() != FLOOR:
                print(f"Cannot move into wall")
                return False
        except Exception as e:
            print(f"failed to get tile: {e}")
            return False
        avatar.set_coord((tx, ty))
        return True



            




     






    
            