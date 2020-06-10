from math import sin

from core.classes import WVec
from core.constants import CHUNK_W_SIZE, WORLD_HEIGHT_BOUNDS
from item.block import Block, BlockType


class WorldGenerator:
    WATER_HEIGHT = 2 ** 6
    DIRT_DEPTH = 5
    BEDROCK_DEPTH = 5

    WORLD_HEIGHT_FREQ = 50
    CAVES_PROBABILITY = -0.25

    def __init__(self, seed):
        self.seed = seed

    def _choose_block_type_at_pos(self, block_w_pos):
        # Terrain height
        # terrain_height = self.WATER_HEIGHT + 20 * noise.pnoise2(0.062 + block_w_pos.x/self.WORLD_HEIGHT_FREQ, self.seed, octaves=5)
        terrain_height = self.WATER_HEIGHT + 4 * sin(block_w_pos.x * 50)

        if block_w_pos.y < WORLD_HEIGHT_BOUNDS[0]:
            block_type = BlockType.air
        elif block_w_pos.y < self.BEDROCK_DEPTH:
            block_type = BlockType.bedrock
        elif block_w_pos.y < terrain_height - self.DIRT_DEPTH:
            block_type = BlockType.stone
        elif block_w_pos.y < terrain_height - 1:
            block_type = BlockType.dirt
        elif block_w_pos.y < terrain_height:
            block_type = BlockType.grass
        else:
            block_type = BlockType.air

        # # Caves
        # if noise.pnoise3(0.0468 + block_w_pos.x/10, 0.1564 + block_w_pos.y/10, self.seed, octaves=5) < self.CAVES_PROBABILITY:
        #     block_type = Material.air

        # Return
        if block_type == BlockType.air:
            return None
        return block_type

    def gen_chunk_blocks(self, chunk_w_pos: WVec):
        blocks_map = {}
        for w_shift_x in range(CHUNK_W_SIZE.x):
            for w_shift_y in range(CHUNK_W_SIZE.y):
                block_w_pos = WVec(chunk_w_pos.x + w_shift_x, chunk_w_pos.y + w_shift_y)
                block_type = self._choose_block_type_at_pos(block_w_pos)
                if block_type is None:
                    continue
                blocks_map[block_w_pos] = Block(block_type)
        return blocks_map

    def load_chunk_blocks(self, blocks_data):
        blocks_map = {}
        for block_w_pos, block_type in blocks_data.items():
            blocks_map[block_w_pos] = Block(block_type)
        return blocks_map
