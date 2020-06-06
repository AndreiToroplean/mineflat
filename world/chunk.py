from math import floor

import pygame as pg
import numpy as np

from core.funcs import w_to_pix_shift, color_float_to_int
from core.constants import BLOCK_PIX_SIZE, CHUNK_W_SIZE, C_KEY, CHUNK_PIX_SIZE, C_SKY, MAX_LIGHT_LEVEL
from core.classes import WVec, Colliders, Result
from world.generation import WorldGenerator, Material


class Chunk:
    _empty_block_surf = pg.Surface((BLOCK_PIX_SIZE, BLOCK_PIX_SIZE))
    _empty_block_surf.fill(C_SKY)

    def __init__(self, w_pos: WVec, seed, blocks_map=None):
        self._w_pos = w_pos

        self._seed = seed
        self._generator = WorldGenerator(self._seed)
        if blocks_map is None:
            self.blocks_map = self._generator.gen_chunk_blocks(self._w_pos)
        else:
            self.blocks_map = self._generator.load_chunk_blocks(blocks_map)

        self.sky_light_grid = np.zeros(CHUNK_W_SIZE, dtype=float)
        self.sky_light_surf = pg.Surface(CHUNK_W_SIZE)
        self.sky_light_surf_array = pg.surfarray.pixels2d(self.sky_light_surf)

        self._blocks_surf = pg.Surface(CHUNK_PIX_SIZE)
        self._draw_blocks_surf()

        self.surf = pg.Surface(CHUNK_PIX_SIZE)

        self.colliders = Colliders()
        self._update_colliders()

    # ==== GENERATE AND DRAW ====
    def _block_pos_to_pix_shift(self, block_w_pos: WVec):
        w_shift = block_w_pos - self._w_pos
        return w_to_pix_shift(w_shift, (BLOCK_PIX_SIZE,) * 2, self._blocks_surf.get_size())

    def _update_colliders(self):
        self.colliders = Colliders()
        for block_w_pos in self.blocks_map:
            if not (block_w_pos + WVec(-1, 0)) in self.blocks_map:
                self.colliders.left.append(block_w_pos)
            if not (block_w_pos + WVec(+1, 0)) in self.blocks_map:
                self.colliders.right.append(block_w_pos)
            if not (block_w_pos + WVec(0, -1)) in self.blocks_map:
                self.colliders.bottom.append(block_w_pos)
            if not (block_w_pos + WVec(0, +1)) in self.blocks_map:
                self.colliders.top.append(block_w_pos)

    def _draw_blocks_surf(self):
        """Draw the blocks, unlit.
        """
        self._blocks_surf.fill(C_SKY)
        blit_sequence = []
        for block_w_pos, block in self.blocks_map.items():
            pix_shift = self._block_pos_to_pix_shift(block_w_pos)
            blit_sequence.append((block.surf, pix_shift))
        self._blocks_surf.blits(blit_sequence, doreturn=False)

    def _update_sky_light(self):
        self.sky_light_grid.fill(MAX_LIGHT_LEVEL)

        with np.nditer(self.sky_light_surf_array, flags=["multi_index"], op_flags=["writeonly"]) as it:
            for cell in it:
                value = color_float_to_int(self.sky_light_grid[it.multi_index] / MAX_LIGHT_LEVEL)
                cell[...] = self.sky_light_surf.map_rgb((value, value, value))

    def draw(self, neighboring_chunks):
        """Update lighting and draw the chunk's surf.
        """
        self._update_sky_light()
        scaled_sky_light_surf = pg.transform.scale(self.sky_light_surf, CHUNK_PIX_SIZE)

        self.surf = self._blocks_surf.copy()
        self.surf.blit(scaled_sky_light_surf, (0, 0), special_flags=pg.BLEND_MULT)

        return ()

    def _draw_block(self, block_w_pos: WVec, block_surf):
        pix_shift = self._block_pos_to_pix_shift(block_w_pos)
        self._blocks_surf.blit(block_surf, pix_shift)

    # ==== MODIFY ====

    def req_break_block(self, block_w_pos: WVec):
        """
        Break block at block_w_pos if it exists and return result (success or failure).
        Then, update the chunk in consequence.
        """
        block = self.blocks_map[block_w_pos]
        if block.material == Material.bedrock:
            return Result.failure

        self.blocks_map.pop(block_w_pos, None)
        self._draw_block(block_w_pos, self._empty_block_surf)
        self._update_colliders()
        return Result.success

    def req_place_block(self, block_w_pos: WVec, material: Material):
        """
        Place block at block_w_pos if the space is free and return result (success or failure).
        Then, update the chunk in consequence.
        """
        # Don't replace existing blocks (by design this should already never happen):
        if block_w_pos in self.blocks_map:
            return Result.failure

        block = self._generator.get_block(material)
        self.blocks_map[block_w_pos] = block
        self._draw_block(block_w_pos, block.surf)
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
