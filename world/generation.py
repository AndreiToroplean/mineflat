from enum import Enum
import random

import noise

from core.classes import WorldVec
from core.constants import CHUNK_SIZE, WORLD_HEIGHT_BOUNDS
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

    _block_materials = {}

    def __init__(self, seed):
        self.seed = seed

    def get_block(self, material):
        try:
            block = self._block_materials[material]
        except KeyError:
            block = Block(material)
            self._block_materials[material] = block

        return block

    def _choose_material_at_pos(self, block_world_pos):
        # Terrain height
        terrain_height = self.WATER_HEIGHT + 20 * noise.pnoise2(0.062 + block_world_pos.x/self.WORLD_HEIGHT_FREQ, self.seed, octaves=5)

        if block_world_pos.y < WORLD_HEIGHT_BOUNDS[0]:
            material = Material.air
        elif block_world_pos.y < self.BEDROCK_DEPTH:
            material = Material.bedrock
        elif block_world_pos.y < terrain_height - self.DIRT_DEPTH:
            material = Material.stone
        elif block_world_pos.y < terrain_height - 1:
            material = Material.dirt
        elif block_world_pos.y < terrain_height:
            material = Material.grass
        else:
            material = Material.air

        # Caves
        if noise.pnoise3(0.0468 + block_world_pos.x/10, 0.1564 + block_world_pos.y/10, self.seed, octaves=5) < self.CAVES_PROBABILITY:
            material = Material.air

        # Return
        if material == Material.air:
            return None
        return material

    def gen_chunk_blocks(self, chunk_world_pos):
        blocks = {}
        for world_shift_x in range(CHUNK_SIZE[0]):
            for world_shift_y in range(CHUNK_SIZE[1]):
                block_world_pos = WorldVec(chunk_world_pos.x + world_shift_x, chunk_world_pos.y + world_shift_y)
                material = self._choose_material_at_pos(block_world_pos)
                if material is None:
                    continue
                blocks[block_world_pos] = self.get_block(material)
        return blocks

    def load_chunk_blocks(self, blocks_data):
        blocks = {}
        for block_world_pos, material in blocks_data.items():
            blocks[block_world_pos] = self.get_block(material)
        return blocks
