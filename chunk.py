import random

import pygame as pg

from core_funcs import chunk_to_world_vec, world_to_pix_shift
from global_params import BLOCK_PIX_SIZE, CHUNK_SIZE, WATER_HEIGHT, C_KEY
from core import PixVec, ChunkVec, WorldVec, ChunkData, Colliders, Material
from block import Block


class Chunk:
    block_materials = {}

    def __init__(self, world_pos):
        self.world_pos = world_pos
        self.blocks = self.generate_blocks()
        self.surf = pg.Surface((
                BLOCK_PIX_SIZE * CHUNK_SIZE[0],
                BLOCK_PIX_SIZE * CHUNK_SIZE[1],
            ))
        self.surf.set_colorkey(C_KEY)
        self.colliders = None
        self.draw()

    def generate_blocks(self):
        blocks = {}
        for world_shift_x in range(CHUNK_SIZE[0]):
            for world_shift_y in range(CHUNK_SIZE[1]):
                block_world_pos = WorldVec(self.world_pos.x+world_shift_x, self.world_pos.y+world_shift_y)
                if block_world_pos.y < WATER_HEIGHT:
                    material = random.choice(list(Material))
                    try:
                        block = self.block_materials[material]
                    except KeyError:
                        block = Block(material)
                        self.block_materials[material] = block

                    blocks[WorldVec(world_shift_x, world_shift_y)] = block
        return blocks

    def draw(self):
        self.surf.fill(C_KEY)
        blit_sequence = [(
            block.surf,
            world_to_pix_shift(world_shift, self.surf.get_size(), (BLOCK_PIX_SIZE,)*2)
            ) for world_shift, block in self.blocks.items()]
        self.surf.blits(blit_sequence, doreturn=False)

    @property
    def data(self):
        return ChunkData(
            surf=self.surf,
            colliders=self.colliders,
            )


if __name__ == "__main__":
    from debug.display import Display
    from global_params import WATER_HEIGHT

    test_surf = Chunk(WorldVec(0, WATER_HEIGHT-4)).surf
    Display(test_surf)
