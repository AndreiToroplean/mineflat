import json
import os
import random
from math import floor

import pygame as pg
import numpy as np

from core.funcs import w_to_c_vec, w_to_pix_shift, w_to_c_to_w_vec
from core.constants import CHUNK_W_SIZE, CHUNK_PIX_SIZE, C_KEY, ACTION_COOLDOWN_DELAY
from core.classes import CView, WView, CVec, WVec, Colliders, Result, WBounds, WDimBounds
from world.chunk import Chunk
from world.generation import Material


class World:
    _SAVE_FILE_NAME = "world.json"

    _empty_chunk_surf = pg.Surface(CHUNK_PIX_SIZE)
    _empty_chunk_surf.fill(C_KEY)

    def __init__(self):
        self._seed = random.randint(0, 2 ** 20) + 0.15681

        self.chunks_existing = {}
        self._chunks_visible = {}

        self._c_view = CView(CVec(0, 0), CVec(0, 0))
        self._max_view = WView(WVec(0, 0), WVec(0, 0))

        self._max_surf = pg.Surface((1, 1))
        self._max_surf.set_colorkey(C_KEY)
        self._force_draw = True

        self._action_cooldown_remaining = 0

    # ==== TIME ====

    def _tick(self):
        if self._action_cooldown_remaining > 0:
            self._action_cooldown_remaining -= 1

    # ==== GET DATA ====

    def _get_chunk_data_at_pos(self, w_pos):
        chunk_w_pos = w_to_c_to_w_vec(w_pos)
        try:
            chunk = self.chunks_existing[chunk_w_pos]
        except KeyError:
            return None

        return chunk_w_pos, chunk

    def _get_chunks_around(self, w_pos, *, c_radius=1):
        chunks = {}
        for pos_x in range(
                floor(w_pos[0] - c_radius * CHUNK_W_SIZE.x),
                floor(w_pos[0] + (c_radius+1) * CHUNK_W_SIZE.x),
                CHUNK_W_SIZE.x
                ):
            for pos_y in range(
                    floor(w_pos[1] - c_radius * CHUNK_W_SIZE.y),
                    floor(w_pos[1] + (c_radius+1) * CHUNK_W_SIZE.y),
                    CHUNK_W_SIZE.y
                    ):
                chunk_w_pos = WVec(pos_x, pos_y)
                chunk_data = self._get_chunk_data_at_pos(chunk_w_pos)
                if chunk_data is None:
                    continue
                chunks.update((chunk_data,))
        return chunks

    def _get_blocks_around(self, w_pos, *, c_radius=1):
        blocks = {}
        for chunk in self._get_chunks_around(w_pos, c_radius=c_radius).values():
            blocks.update(chunk.blocks)
        return blocks

    def get_colliders_around(self, w_pos, *, c_radius=1):
        colliders = Colliders()
        for chunk in self._get_chunks_around(w_pos, c_radius=c_radius).values():
            for colliders_dir, chunk_colliders_dir in zip(colliders, chunk.colliders):
                colliders_dir += chunk_colliders_dir
        return colliders

    def get_intersected_block(self, start_w_pos, end_w_pos, max_distance, *, c_radius=1, threshold=0.01, substeps=5):
        blocks = self._get_blocks_around(start_w_pos, c_radius=c_radius)
        w_vel = end_w_pos - start_w_pos
        w_speed = np.linalg.norm(w_vel)
        w_vel_step = w_vel / (w_speed * (1 + threshold) * substeps)
        max_mult = max_distance * substeps
        for mult in range(max_mult):
            w_pos = WVec(*(np.floor(start_w_pos + w_vel_step * mult)))
            if w_pos in blocks:
                prev_w_pos = WVec(*(np.floor(start_w_pos + w_vel_step * (mult-1))))
                return (w_pos, blocks[w_pos]), (prev_w_pos, )

        # If no block has been intersected up to max_distance:
        return None

    # ==== CHECK BOOLEANS ====

    @staticmethod
    def _is_pos_in_bounds(w_pos, bounds: WBounds(WDimBounds, WDimBounds)):
        return (bounds.x.min <= w_pos[0] <= bounds.x.max
                and bounds.y.min <= w_pos[1] <= bounds.y.max)

    # ==== GENERATION AND DRAWING ====

    def _update_c_view(self, camera):
        """Updates c_view and returns True if there are new chunks to load, False otherwise. """
        new_c_view = CView(
            w_to_c_vec(camera.w_view.pos_0),
            w_to_c_vec(camera.w_view.pos_1),
            )

        if new_c_view == self._c_view:
            return False

        self._c_view = new_c_view
        return True

    def _update_chunks_visible(self):
        self._max_view = WView(
            WVec(*[dim * chunk_size_dim for dim, chunk_size_dim in zip(self._c_view.pos_0, CHUNK_W_SIZE)]),
            WVec(*[(dim + 1) * chunk_size_dim for dim, chunk_size_dim in zip(self._c_view.pos_1, CHUNK_W_SIZE)]),
            )

        self._chunks_visible = {}
        for chunk_w_pos_x in range(self._max_view.pos_0.x, self._max_view.pos_1.x, CHUNK_W_SIZE.x):
            for chunk_w_pos_y in range(self._max_view.pos_0.y, self._max_view.pos_1.y, CHUNK_W_SIZE.y):
                chunk_w_pos = WVec(chunk_w_pos_x, chunk_w_pos_y)
                if chunk_w_pos in self.chunks_existing:
                    chunk_to_load = self.chunks_existing[chunk_w_pos]
                else:
                    chunk_to_load = Chunk(chunk_w_pos, self._seed)
                    self.chunks_existing[chunk_w_pos] = chunk_to_load

                self._chunks_visible[chunk_w_pos] = chunk_to_load

    def _chunk_w_pos_to_pix_shift(self, chunk_w_pos):
        max_view_w_shift = WVec(*(pos - shift for pos, shift in zip(chunk_w_pos, self._max_view.pos_0)))
        return w_to_pix_shift(max_view_w_shift, CHUNK_PIX_SIZE, self._max_surf.get_size())

    def _draw_max_surf(self):
        self._update_chunks_visible()

        self._max_surf.fill(C_KEY)
        blit_sequence = []
        for chunk_w_pos, chunk in self._chunks_visible.items():
            pix_shift = self._chunk_w_pos_to_pix_shift(chunk_w_pos)
            blit_sequence.append((chunk.surf, pix_shift))
        self._max_surf.blits(blit_sequence, doreturn=False)

    def _resize_max_surf(self, camera):
        max_surf_pix_size = tuple(
            (dim + 2) * pix
            for dim, pix in zip(w_to_c_vec(camera.w_size), CHUNK_PIX_SIZE)
            )
        self._max_surf = pg.transform.scale(self._max_surf, max_surf_pix_size)

    def draw_and_tick(self, camera):
        are_new_chunks = self._update_c_view(camera)
        if needs_redrawing := (camera.is_zooming or self._force_draw):
            self._resize_max_surf(camera)
            self._force_draw = False
        if are_new_chunks or needs_redrawing:
            self._draw_max_surf()
        camera.draw_world(self._max_surf, self._max_view.pos_0)
        self._tick()

    def _redraw_chunk(self, chunk_w_pos, chunk_surf):
        pix_shift = self._chunk_w_pos_to_pix_shift(chunk_w_pos)
        self._max_surf.blit(self._empty_chunk_surf, pix_shift)
        self._max_surf.blit(chunk_surf, pix_shift)

    # ==== MODIFICATION ====

    def req_break_block(self, w_pos):
        """Check whether a block can be broken at w_pos and if so, break it.
        """
        # Case where the block selector hasn't reached a block
        if w_pos is None:
            return

        if self._action_cooldown_remaining > 0:
            return

        block_w_pos = WVec(*(floor(pos_dim) for pos_dim in w_pos))

        self._action_cooldown_remaining = ACTION_COOLDOWN_DELAY
        self._break_block(block_w_pos)

    def req_place_block(self, w_pos, material, player_bounds):
        """Check whether a block can be placed at w_pos and if so, place it.
        """
        # Case where the block selector hasn't reached a block
        if w_pos is None:
            return

        if self._action_cooldown_remaining > 0:
            return

        block_w_pos = WVec(*(floor(pos_dim) for pos_dim in w_pos))

        if self._is_pos_in_bounds(block_w_pos, player_bounds):
            return

        self._action_cooldown_remaining = ACTION_COOLDOWN_DELAY
        self._place_block(block_w_pos, material)

    def _break_block(self, block_w_pos):
        """Request breaking of the block at block_w_pos to the relevant chunk.
        Then update the world in consequence.
        """
        chunk_data = self._get_chunk_data_at_pos(block_w_pos)
        if chunk_data is None:
            return

        chunk_w_pos, chunk = chunk_data
        result = chunk.req_break_block(block_w_pos)
        if result == Result.failure:
            return

        self._redraw_chunk(chunk_w_pos, chunk.surf)

    def _place_block(self, block_w_pos, material):
        """Request placing of the block of the given material at block_w_pos to the relevant chunk.
        Then update the world in consequence.
        """
        chunk_data = self._get_chunk_data_at_pos(block_w_pos)
        if chunk_data is None:
            return

        chunk_w_pos, chunk = chunk_data
        result = chunk.req_place_block(block_w_pos, material=material)
        if result == Result.failure:
            return

        self._redraw_chunk(chunk_w_pos, chunk.surf)

    # ==== SAVING AND LOADING ====

    def load_from_disk(self, dir_path):
        try:
            with open(os.path.join(dir_path, self._SAVE_FILE_NAME)) as file:
                data = json.load(file)
        except FileNotFoundError:
            return
        self._seed = data["seed"]
        for chunk_w_pos_str, blocks_data_str in data["chunks_data"].items():
            chunk_w_pos = eval(chunk_w_pos_str)
            blocks_data = {}
            for block_w_pos_str, material_str in blocks_data_str.items():
                blocks_data[eval(block_w_pos_str)] = eval(material_str)
            self.chunks_existing[chunk_w_pos] = Chunk(chunk_w_pos, self._seed, blocks_data)

    def save_to_disk(self, dir_path):
        data = {"seed": self._seed, "chunks_data": {}}
        for chunk in self.chunks_existing.values():
            data["chunks_data"].update(chunk.collect_chunk_data())

        with open(os.path.join(dir_path, self._SAVE_FILE_NAME), "w") as file:
            json.dump(data, file, indent=4)
