from math import sin, floor

import pygame as pg

from core.funcs import world_to_pix_shift
from core.consts import BLOCK_PIX_SIZE, CHUNK_SIZE, WATER_HEIGHT, C_KEY
from core.classes import WorldVec, Colliders
from world.generation import WorldGenerator, Material


class Chunk:
    _block_materials = {}
    _empty_block_surf = pg.Surface((BLOCK_PIX_SIZE, BLOCK_PIX_SIZE))
    _empty_block_surf.fill(C_KEY)

    def __init__(self, world_pos):
        self._world_pos = world_pos

        self._generator = WorldGenerator()
        self._blocks = {}
        self._generate_blocks()

        self.surf = pg.Surface((
                BLOCK_PIX_SIZE * CHUNK_SIZE[0],
                BLOCK_PIX_SIZE * CHUNK_SIZE[1],
            ))
        self.surf.set_colorkey(C_KEY)
        self._draw()

        self.colliders = Colliders()
        self._update_colliders()

    def _generate_blocks(self):
        self._blocks = self._generator.gen_chunk_blocks(self._world_pos)

    def _update_colliders(self):
        self.colliders = Colliders()
        for block_world_pos in self._blocks:
            if not (block_world_pos[0]-1, block_world_pos[1]) in self._blocks:
                self.colliders.left.append(block_world_pos)
            if not (block_world_pos[0]+1, block_world_pos[1]) in self._blocks:
                self.colliders.right.append(block_world_pos)
            if not (block_world_pos[0], block_world_pos[1]-1) in self._blocks:
                self.colliders.bottom.append(block_world_pos)
            if not (block_world_pos[0], block_world_pos[1]+1) in self._blocks:
                self.colliders.top.append(block_world_pos)

    def _block_pos_to_pix_shift(self, block_world_pos):
        world_shift = WorldVec(
            *(block_dim - chunk_dim for block_dim, chunk_dim in zip(block_world_pos, self._world_pos))
            )
        return world_to_pix_shift(world_shift, (BLOCK_PIX_SIZE,) * 2, self.surf.get_size())

    def _draw(self):
        self.surf.fill(C_KEY)
        blit_sequence = []
        for block_world_pos, block in self._blocks.items():
            pix_shift = self._block_pos_to_pix_shift(block_world_pos)
            blit_sequence.append((block.surf, pix_shift))
        self.surf.blits(blit_sequence, doreturn=False)

    def _redraw_block(self, block_world_pos, block_surf):
        pix_shift = self._block_pos_to_pix_shift(block_world_pos)
        self.surf.blit(block_surf, pix_shift)

    def req_break_block(self, world_pos):
        block_world_pos = WorldVec(*(floor(pos_dim) for pos_dim in world_pos))
        self._break_block(block_world_pos)

    def _break_block(self, block_world_pos):
        self._blocks.pop(block_world_pos, None)
        self._redraw_block(block_world_pos, self._empty_block_surf)
        self._update_colliders()

    def req_place_block(self, world_pos, material):
        block_world_pos = WorldVec(*(floor(pos_dim) for pos_dim in world_pos))
        self._place_block(block_world_pos, material)

    def _place_block(self, block_world_pos, material):
        block = self._generator.get_block(material)
        self._blocks[block_world_pos] = block
        self._redraw_block(block_world_pos, block.surf)
        self._update_colliders()
