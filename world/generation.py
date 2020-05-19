from enum import Enum
from math import sin, floor

from core.classes import WorldVec
from core.consts import WATER_HEIGHT, CHUNK_SIZE
from world.block import Block


class Material(Enum):
    stone = "1"
    grass = "2"
    dirt = "3"


class WorldGenerator:
    _block_materials = {}

    def __init__(self):
        pass

    def get_block(self, material):
        try:
            block = self._block_materials[material]
        except KeyError:
            block = Block(material)
            self._block_materials[material] = block

        return block

    @staticmethod
    def gen_material_at_pos(block_world_pos):
        test_height = WATER_HEIGHT + sin(block_world_pos.x / 16) * 4
        if block_world_pos.y >= test_height or block_world_pos.y < 0:
            return None
        if block_world_pos.y >= test_height - 1:
            material = Material.grass
        elif test_height - 1 > block_world_pos.y >= test_height - 4:
            material = Material.dirt
        else:
            material = Material.stone
        return material

    def gen_chunk_blocks(self, chunk_world_pos):
        blocks = {}
        for world_shift_x in range(CHUNK_SIZE[0]):
            for world_shift_y in range(CHUNK_SIZE[1]):
                block_world_pos = WorldVec(chunk_world_pos.x + world_shift_x, chunk_world_pos.y + world_shift_y)
                material = self.gen_material_at_pos(block_world_pos)
                if material is None:
                    continue
                blocks[block_world_pos] = self.get_block(material)
        return blocks
