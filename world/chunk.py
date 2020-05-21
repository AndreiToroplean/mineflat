from math import floor

import pygame as pg

from core.funcs import w_to_pix_shift
from core.constants import BLOCK_PIX_SIZE, CHUNK_W_SIZE, C_KEY
from core.classes import WVec, Colliders, Result
from world.generation import WorldGenerator, Material


class Chunk:
    _empty_block_surf = pg.Surface((BLOCK_PIX_SIZE, BLOCK_PIX_SIZE))
    _empty_block_surf.fill(C_KEY)

    def __init__(self, w_pos, seed, blocks_data=None):
        self._w_pos = w_pos

        self._seed = seed
        self._generator = WorldGenerator(self._seed)
        if blocks_data is None:
            self.blocks = self._generator.gen_chunk_blocks(self._w_pos)
        else:
            self.blocks = self._generator.load_chunk_blocks(blocks_data)

        self.surf = pg.Surface((
            BLOCK_PIX_SIZE * CHUNK_W_SIZE[0],
            BLOCK_PIX_SIZE * CHUNK_W_SIZE[1],
            ))
        self.surf.set_colorkey(C_KEY)
        self._draw()

        self.colliders = Colliders()
        self._update_colliders()

    def _update_colliders(self):
        self.colliders = Colliders()
        for block_w_pos in self.blocks:
            if not (block_w_pos[0]-1, block_w_pos[1]) in self.blocks:
                self.colliders.left.append(block_w_pos)
            if not (block_w_pos[0]+1, block_w_pos[1]) in self.blocks:
                self.colliders.right.append(block_w_pos)
            if not (block_w_pos[0], block_w_pos[1]-1) in self.blocks:
                self.colliders.bottom.append(block_w_pos)
            if not (block_w_pos[0], block_w_pos[1]+1) in self.blocks:
                self.colliders.top.append(block_w_pos)

    def _block_pos_to_pix_shift(self, block_w_pos):
        w_shift = WVec(
            *(block_dim - chunk_dim for block_dim, chunk_dim in zip(block_w_pos, self._w_pos))
            )
        return w_to_pix_shift(w_shift, (BLOCK_PIX_SIZE,) * 2, self.surf.get_size())

    def _draw(self):
        self.surf.fill(C_KEY)
        blit_sequence = []
        for block_w_pos, block in self.blocks.items():
            pix_shift = self._block_pos_to_pix_shift(block_w_pos)
            blit_sequence.append((block.surf, pix_shift))
        self.surf.blits(blit_sequence, doreturn=False)

    def _redraw_block(self, block_w_pos, block_surf):
        pix_shift = self._block_pos_to_pix_shift(block_w_pos)
        self.surf.blit(block_surf, pix_shift)

    def req_break_block(self, w_pos):
        block_w_pos = WVec(*(floor(pos_dim) for pos_dim in w_pos))

        block = self.blocks[block_w_pos]
        if block.material == Material.bedrock:
            return Result.failure

        self.blocks.pop(block_w_pos, None)
        self._redraw_block(block_w_pos, self._empty_block_surf)
        self._update_colliders()
        return Result.success

    def req_place_block(self, w_pos, material):
        block_w_pos = WVec(*(floor(pos_dim) for pos_dim in w_pos))
        block = self._generator.get_block(material)
        self.blocks[block_w_pos] = block
        self._redraw_block(block_w_pos, block.surf)
        self._update_colliders()
        return Result.success

    def collect_chunk_data(self):
        blocks_data = {}
        for block_w_pos, block in self.blocks.items():
            blocks_data[str(block_w_pos)] = str(block.material)
        return {str(self._w_pos): blocks_data}
