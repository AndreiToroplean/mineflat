import math
import random

import pygame as pg

from core_funcs import chunk_to_world_vec, world_to_pix_shift
from global_params import BLOCK_PIX_SIZE, CHUNK_SIZE, WATER_HEIGHT, C_KEY
from core import PixVec, ChunkVec, WorldVec, ChunkData, Colliders
from block import Block, Material


class Chunk:
    block_materials = {}

    def __init__(self, world_pos):
        self._world_pos = world_pos
        self._blocks = {}
        self._generate_blocks()

        self.surf = pg.Surface((
                BLOCK_PIX_SIZE * CHUNK_SIZE[0],
                BLOCK_PIX_SIZE * CHUNK_SIZE[1],
            ))
        self.surf.set_colorkey(C_KEY)
        self._draw()

        self.colliders = Colliders()
        self._generate_colliders()

    def _generate_blocks(self):
        for world_shift_x in range(CHUNK_SIZE[0]):
            for world_shift_y in range(CHUNK_SIZE[1]):
                block_world_pos = WorldVec(self._world_pos.x + world_shift_x, self._world_pos.y + world_shift_y)
                test_height = WATER_HEIGHT + math.sin(block_world_pos.x/16)*4
                if block_world_pos.y >= test_height:
                    continue
                if block_world_pos.y >= test_height - 1:
                    material = Material.grass
                elif test_height - 1 > block_world_pos.y >= test_height - 4:
                    material = Material.dirt
                else:
                    material = Material.stone

                try:
                    block = self.block_materials[material]
                except KeyError:
                    block = Block(material)
                    self.block_materials[material] = block

                self._blocks[block_world_pos] = block

    def _generate_colliders(self):
        for block_world_pos in self._blocks:
            if not (block_world_pos[0]-1, block_world_pos[1]) in self._blocks:
                self.colliders.left.append(block_world_pos)
            if not (block_world_pos[0]+1, block_world_pos[1]) in self._blocks:
                self.colliders.right.append(block_world_pos)
            if not (block_world_pos[0], block_world_pos[1]-1) in self._blocks:
                self.colliders.bottom.append(block_world_pos)
            if not (block_world_pos[0], block_world_pos[1]+1) in self._blocks:
                self.colliders.top.append(block_world_pos)

    def _draw(self):
        self.surf.fill(C_KEY)
        blit_sequence = []
        for block_world_pos, block in self._blocks.items():
            world_shift = WorldVec(*(block_dim - chunk_dim
                for block_dim, chunk_dim in zip(block_world_pos, self._world_pos)))
            pix_shift = world_to_pix_shift(world_shift, (BLOCK_PIX_SIZE,) * 2, self.surf.get_size())
            blit_sequence.append((block.surf, pix_shift))
        self.surf.blits(blit_sequence, doreturn=False)


if __name__ == "__main__":
    from debug.display import Display
    from global_params import WATER_HEIGHT

    test_surf = Chunk(WorldVec(0, WATER_HEIGHT-4)).surf
    Display(test_surf)
