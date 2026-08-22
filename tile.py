from pygame import *

class Tile:
    def __init__(self, type, coord):
        self.type = type
        self.coord = coord
        self.texture_rot = None
        self.texture_idx = None
        self.adjacencies = [False] * 8
        self.tot_adjacency = 0
    def get_type(self):
        return self.type
    def get_coord(self):
        return self.coord
    def set_type(self, new_type):
        self.type = new_type
    def set_texture_rot(self, rot: int):
        self.texture_rot = rot
    def get_texture_rot(self):
        return self.texture_rot
    def set_texture_idx(self, idx):
        self.texture_idx = idx
    def get_texture_idx(self):
        return self.texture_idx
    def update_adj(self, idx: int, adj: bool):
        self.adjacencies[idx] = adj
    def calc_adj(self):
        powers = [2**i for i in range(8)]
        overlay = list(zip(self.adjacencies, powers))
        for (bit, value) in overlay:
            self.tot_adjacency += bit * value
    def get_adjacencies(self):
        return self.adjacencies

