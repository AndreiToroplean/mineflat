from math import floor

import pygame as pg

from core.funcs import w_to_pix_shift
from core.constants import BLOCK_PIX_SIZE, CHUNK_W_SIZE, C_KEY
from core.classes import WVec, Colliders, Result
from world.generation import WorldGenerator, Material


class Chunk:
    _empty_block_surf = pg.Surface((BLOCK_PIX_SIZE, BLOCK_PIX_SIZE))
    _empty_block_surf.fill(C_KEY)

    def __init__(self, w_pos, seed, blocks_map=None):
        self._w_pos = w_pos

        self._seed = seed
        self._generator = WorldGenerator(self._seed)
        if blocks_map is None:
            self.blocks_map = self._generator.gen_chunk_blocks(self._w_pos)
        else:
            self.blocks_map = self._generator.load_chunk_blocks(blocks_map)

        self.surf = pg.Surface((
            BLOCK_PIX_SIZE * CHUNK_W_SIZE[0],
            BLOCK_PIX_SIZE * CHUNK_W_SIZE[1],
            ))
        self.surf.set_colorkey(C_KEY)
        self._draw()

        self.colliders = Colliders()
        self._update_colliders()

    # ==== GENERATE AND DRAW ====

    def _update_colliders(self):
        self.colliders = Colliders()
        for block_w_pos in self.blocks_map:
            if not WVec(block_w_pos[0]-1, block_w_pos[1]) in self.blocks_map:
                self.colliders.left.append(block_w_pos)
            if not WVec(block_w_pos[0]+1, block_w_pos[1]) in self.blocks_map:
                self.colliders.right.append(block_w_pos)
            if not WVec(block_w_pos[0], block_w_pos[1]-1) in self.blocks_map:
                self.colliders.bottom.append(block_w_pos)
            if not WVec(block_w_pos[0], block_w_pos[1]+1) in self.blocks_map:
                self.colliders.top.append(block_w_pos)

    def _block_pos_to_pix_shift(self, block_w_pos):
        w_shift = WVec(
            *(block_dim - chunk_dim for block_dim, chunk_dim in zip(block_w_pos, self._w_pos))
            )
        return w_to_pix_shift(w_shift, (BLOCK_PIX_SIZE,) * 2, self.surf.get_size())

    def _draw(self):
        self.surf.fill(C_KEY)
        blit_sequence = []
        for block_w_pos, block in self.blocks_map.items():
            pix_shift = self._block_pos_to_pix_shift(block_w_pos)
            blit_sequence.append((block.surf, tuple(pix_shift)))
        self.surf.blits(blit_sequence, doreturn=False)

    def _redraw_block(self, block_w_pos, block_surf):
        pix_shift = self._block_pos_to_pix_shift(block_w_pos)
        self.surf.blit(block_surf, tuple(pix_shift))

    # ==== MODIFY ====

    def req_break_block(self, block_w_pos):
        """
        Break block at block_w_pos if it exists and return result (success or failure).
        Then, update the chunk in consequence.
        """
        block = self.blocks_map[block_w_pos]
        if block.material == Material.bedrock:
            return Result.failure

        self.blocks_map.pop(block_w_pos, None)
        self._redraw_block(block_w_pos, self._empty_block_surf)
        self._update_colliders()
        return Result.success

    def req_place_block(self, block_w_pos, material):
        """
        Place block at block_w_pos if the space is free and return result (success or failure).
        Then, update the chunk in consequence.
        """
        # Don't replace existing blocks (by design this should already never happen):
        if block_w_pos in self.blocks_map:
            return Result.failure

        block = self._generator.get_block(material)
        self.blocks_map[block_w_pos] = block
        self._redraw_block(block_w_pos, block.surf)
        self._update_colliders()
        return Result.success

    # ==== COLLECT DATA ====

    def collect_data(self):
        """
        Return all the data necessary to recreate the chunk's current state.
        """
        blocks_data = {}
        for block_w_pos, block in self.blocks_map.items():
            blocks_data[str(block_w_pos)] = str(block.material)
        return {str(self._w_pos): blocks_data}
