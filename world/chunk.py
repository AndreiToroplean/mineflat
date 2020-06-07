from heapq import heappush, heappop
from math import floor

import pygame as pg
import numpy as np

from core.funcs import w_to_pix_shift, color_float_to_int
from core.constants import BLOCK_PIX_SIZE, CHUNK_W_SIZE, C_KEY, CHUNK_PIX_SIZE, C_SKY, LIGHT_MAX_LEVEL, \
    LIGHT_BLOCK_ATTENUATION
from core.classes import WVec, Colliders, Result, Dir
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

        self._is_block_grid = np.zeros(CHUNK_W_SIZE + 2, dtype=bool)
        self._sky_light_grid = np.zeros(CHUNK_W_SIZE + 2, dtype=int)
        self._sky_light_surf = pg.Surface(CHUNK_W_SIZE)
        self._sky_light_surf_array = pg.surfarray.pixels2d(self._sky_light_surf)

        self._blocks_surf = pg.Surface(CHUNK_PIX_SIZE)
        self._draw_blocks_surf()

        self.surf = pg.Surface(CHUNK_PIX_SIZE)

        self.colliders = Colliders()
        self._update_colliders()

    # ==== GET DATA ====

    def is_block_at_w_shift(self, w_shift):
        return self._w_shift_to_block_w_pos(w_shift) in self.blocks_map

    def get_sky_light_border_for(self, dir_):
        if dir_ == Dir.right:
            return self._sky_light_grid[1:-1, 1], [self.is_block_at_w_shift(WVec(0, y_shift)) for y_shift in range(CHUNK_W_SIZE.y)]
        elif dir_ == Dir.up:
            return self._sky_light_grid[-2, 1:-1], [self.is_block_at_w_shift(WVec(x_shift, 0)) for x_shift in range(CHUNK_W_SIZE.x)]
        elif dir_ == Dir.left:
            return self._sky_light_grid[1:-1, -2], [self.is_block_at_w_shift(WVec(CHUNK_W_SIZE.x-1, y_shift)) for y_shift in range(CHUNK_W_SIZE.y)]
        else:  # if dir_ == Dir.bottom:
            return self._sky_light_grid[1, 1:-1], [self.is_block_at_w_shift(WVec(x_shift, CHUNK_W_SIZE.y-1)) for x_shift in range(CHUNK_W_SIZE.x)]

    def cell_index_to_block_w_pos(self, ij):
        w_shift = WVec(ij[1] - 1, CHUNK_W_SIZE.y - ij[0])
        return self._w_shift_to_block_w_pos(w_shift)

    def block_w_pos_to_cell_index(self, block_w_pos):
        w_shift = self._block_w_pos_to_w_shift(block_w_pos)
        return CHUNK_W_SIZE.y - w_shift.y, w_shift.x + 1

    @staticmethod
    def _border_indices_gen(dir_):
        if dir_ == Dir.right:
            for i in range(CHUNK_W_SIZE.y):
                index = i+1, CHUNK_W_SIZE.x+2-1
                yield index
        if dir_ == Dir.up:
            for j in range(CHUNK_W_SIZE.x):
                index = 0, j+1
                yield index
        if dir_ == Dir.left:
            for i in range(CHUNK_W_SIZE.y):
                index = i+1, 0
                yield index
        if dir_ == Dir.down:
            for j in range(CHUNK_W_SIZE.x):
                index = CHUNK_W_SIZE.y+2-1, j+1
                yield index

    def _block_w_pos_to_w_shift(self, block_w_pos: WVec):
        return block_w_pos - self._w_pos

    def _w_shift_to_block_w_pos(self, block_w_pos: WVec):
        return block_w_pos + self._w_pos

    def _block_w_pos_to_pix_shift(self, block_w_pos: WVec):
        w_shift = self._block_w_pos_to_w_shift(block_w_pos)
        return w_to_pix_shift(w_shift, (BLOCK_PIX_SIZE,) * 2, self._blocks_surf.get_size())

    # ==== GENERATE AND DRAW ====

    def _update_colliders(self):
        self.colliders = Colliders()
        for block_w_pos in self.blocks_map:
            if not (block_w_pos + WVec(-1, 0)) in self.blocks_map:
                self.colliders.left.append(block_w_pos)
            if not (block_w_pos + WVec(+1, 0)) in self.blocks_map:
                self.colliders.right.append(block_w_pos)
            if not (block_w_pos + WVec(0, -1)) in self.blocks_map:
                self.colliders.down.append(block_w_pos)
            if not (block_w_pos + WVec(0, +1)) in self.blocks_map:
                self.colliders.up.append(block_w_pos)

    def _draw_blocks_surf(self):
        """Draw the blocks, unlit.
        """
        self._blocks_surf.fill(C_SKY)
        blit_sequence = []
        for block_w_pos, block in self.blocks_map.items():
            pix_shift = self._block_w_pos_to_pix_shift(block_w_pos)
            blit_sequence.append((block.surf, pix_shift))
        self._blocks_surf.blits(blit_sequence, doreturn=False)

    def _apply_sky_light_grid(self):
        with np.nditer(self._sky_light_surf_array, flags=["multi_index"], op_flags=["writeonly"]) as it:
            for cell in it:
                value = color_float_to_int(self._sky_light_grid[it.multi_index[1] + 1, it.multi_index[0] + 1] / LIGHT_MAX_LEVEL)
                cell[...] = self._sky_light_surf.map_rgb((value, value, value))

    def light(self, neighboring_sky_light_data):
        visited_cells = []
        cells_priority_queue = []
        neighbors_to_update = set()

        def cell_neigh_gen(ij):
            candidates = (
                ((ij[0], ij[1] + 1), Dir.right),
                ((ij[0] - 1, ij[1]), Dir.up),
                ((ij[0], ij[1] - 1), Dir.left),
                ((ij[0] + 1, ij[1]), Dir.down),
                )

            for candidate in candidates:
                if candidate[0] in visited_cells:
                    continue
                if not (0 <= candidate[0][0] < CHUNK_W_SIZE.y + 2
                        and 0 <= candidate[0][1] < CHUNK_W_SIZE.x + 2):
                    continue

                visited_cells.append(candidate[0])
                yield candidate

        # Filling borders
        for dir_ in Dir:
            for neigh_index, index in enumerate(self._border_indices_gen(dir_)):
                if dir_ in neighboring_sky_light_data:
                    neighboring_sky_light, neighboring_is_block = neighboring_sky_light_data[dir_]
                    value = neighboring_sky_light[neigh_index]
                    is_block = neighboring_is_block[neigh_index]
                else:
                    value = LIGHT_MAX_LEVEL if dir_ == Dir.up else 0
                    is_block = False if dir_ == Dir.up else True

                self._sky_light_grid[index] = value
                self._is_block_grid[index] = is_block
                if value == LIGHT_MAX_LEVEL:
                    visited_cells.append(index)
                if value > 1:
                    heappush(cells_priority_queue, (-value, index))

        # Filling is_bloc_grid:
        for block_w_pos in self.blocks_map:
            self._is_block_grid[self.block_w_pos_to_cell_index(block_w_pos)] = True

        # Computing lighting
        while len(cells_priority_queue) > 0:
            source_value, index = heappop(cells_priority_queue)
            source_value *= -1

            for cell_index, dir_ in cell_neigh_gen(index):
                # Computing light value in cell
                if self._is_block_grid[index]:
                    cell_value = max(0, source_value - LIGHT_BLOCK_ATTENUATION)
                elif dir_ == Dir.down and source_value == LIGHT_MAX_LEVEL:
                    cell_value = LIGHT_MAX_LEVEL
                else:
                    cell_value = source_value - 1
                if cell_value > self._sky_light_grid[cell_index]:
                    self._sky_light_grid[cell_index] = cell_value
                    if cell_value > 1:
                        heappush(cells_priority_queue, (-cell_value, cell_index))

                    if (cell_index[1] == CHUNK_W_SIZE.x+2-1
                            and 1 <= cell_index[0] < CHUNK_W_SIZE.y+2-1
                            and Dir.right in neighboring_sky_light_data):
                        neighbors_to_update.add(Dir.right)
                    if (cell_index[0] == 0
                            and 1 <= cell_index[1] < CHUNK_W_SIZE.x+2-1
                            and Dir.up in neighboring_sky_light_data):
                        neighbors_to_update.add(Dir.up)
                    if (cell_index[1] == 0
                            and 1 <= cell_index[0] < CHUNK_W_SIZE.y+2-1
                            and Dir.left in neighboring_sky_light_data):
                        neighbors_to_update.add(Dir.left)
                    if (cell_index[0] == CHUNK_W_SIZE.y+2-1
                            and 1 <= cell_index[1] < CHUNK_W_SIZE.x+2-1
                            and Dir.down in neighboring_sky_light_data):
                        neighbors_to_update.add(Dir.down)

        self._apply_sky_light_grid()

        return neighbors_to_update

    def draw(self):
        """Update lighting and draw the chunk's surf.
        """
        scaled_sky_light_surf = pg.transform.scale(self._sky_light_surf, CHUNK_PIX_SIZE)
        self.surf = self._blocks_surf.copy()
        self.surf.blit(scaled_sky_light_surf, (0, 0), special_flags=pg.BLEND_MULT)

    def _draw_block(self, block_w_pos: WVec, block_surf):
        pix_shift = self._block_w_pos_to_pix_shift(block_w_pos)
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
