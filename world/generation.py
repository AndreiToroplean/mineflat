from enum import Enum
import random
from math import sin

from core.classes import WVec
from core.constants import CHUNK_W_SIZE, WORLD_HEIGHT_BOUNDS
from world.block import Block


class Material(Enum):
    air = "0"
    stone = "1"
    grass = "2"
    dirt = "3"
    bedrock = "7"


class WorldGenerator:
    WATER_HEIGHT = 2 ** 6
    DIRT_DEPTH = 5
    BEDROCK_DEPTH = 5

    WORLD_HEIGHT_FREQ = 50
    CAVES_PROBABILITY = -0.25

    _block_materials_map = {}

    def __init__(self, seed):
        self.seed = seed

    def get_block(self, material):
        try:
            block = self._block_materials_map[material]
        except KeyError:
            block = Block(material)
            self._block_materials_map[material] = block

        return block

    def _choose_material_at_pos(self, block_w_pos):
        # Terrain height
        # terrain_height = self.WATER_HEIGHT + 20 * noise.pnoise2(0.062 + block_w_pos.x/self.WORLD_HEIGHT_FREQ, self.seed, octaves=5)
        terrain_height = self.WATER_HEIGHT + 4 * sin(block_w_pos.x * 50)

        if block_w_pos.y < WORLD_HEIGHT_BOUNDS[0]:
            material = Material.air
        elif block_w_pos.y < self.BEDROCK_DEPTH:
            material = Material.bedrock
        elif block_w_pos.y < terrain_height - self.DIRT_DEPTH:
            material = Material.stone
        elif block_w_pos.y < terrain_height - 1:
            material = Material.dirt
        elif block_w_pos.y < terrain_height:
            material = Material.grass
        else:
            material = Material.air

        # # Caves
        # if noise.pnoise3(0.0468 + block_w_pos.x/10, 0.1564 + block_w_pos.y/10, self.seed, octaves=5) < self.CAVES_PROBABILITY:
        #     material = Material.air

        # Return
        if material == Material.air:
            return None
        return material

    def gen_chunk_blocks(self, chunk_w_pos: WVec):
        blocks_map = {}
        for w_shift_x in range(CHUNK_W_SIZE[0]):
            for w_shift_y in range(CHUNK_W_SIZE[1]):
                block_w_pos = WVec(chunk_w_pos.x + w_shift_x, chunk_w_pos.y + w_shift_y)
                material = self._choose_material_at_pos(block_w_pos)
                if material is None:
                    continue
                blocks_map[block_w_pos] = self.get_block(material)
        return blocks_map

    def load_chunk_blocks(self, blocks_data):
        blocks_map = {}
        for block_w_pos, material in blocks_data.items():
            blocks_map[block_w_pos] = self.get_block(material)
        return blocks_map
