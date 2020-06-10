import json
import os
import random
from math import floor

import pygame as pg

from core.funcs import w_to_c_vec, w_to_pix_shift, w_to_c_to_w_vec
from core.constants import CHUNK_W_SIZE, CHUNK_PIX_SIZE, C_KEY, ACTION_COOLDOWN_DELAY, BLOCK_BOUND_SHIFTS, DEBUG, \
    LIGHT_MAX_RECURSION
from core.classes import CBounds, CVec, WVec, Colliders, Result, WBounds, BlockSelection, Dir, LoadResult, PixVec
from world.chunk import Chunk
from item.block import BlockType, Block


class World:
    _SAVE_FILE_NAME = "world.json"

    _empty_chunk_surf = pg.Surface(CHUNK_PIX_SIZE)
    _empty_chunk_surf.fill(C_KEY)

    def __init__(self):
        self._seed = random.randint(0, 2 ** 20) + 0.15681

        self.chunks_existing_map = {}
        self._chunks_visible_map = {}

        self._c_view = CBounds(CVec(0, 0), CVec(0, 0))  # Needs to keep the arguments, in order to remain of type int.
        self._max_view = WBounds(WVec(0, 0), WVec(0, 0))  # This too.

        self._max_surf = pg.Surface((0, 0))
        self._force_draw = True

        self._action_cooldown_remaining = 0

    # ==== ADVANCE TIME ====

    def _tick(self):
        if self._action_cooldown_remaining > 0:
            self._action_cooldown_remaining -= 1

    # ==== GET DATA ====

    def _get_chunk_map_at_w_pos(self, w_pos: WVec):
        chunk_w_pos = w_to_c_to_w_vec(w_pos)
        try:
            chunk = self.chunks_existing_map[chunk_w_pos]
        except KeyError:
            return None

        return chunk_w_pos, chunk

    def _get_chunk_map_in_dir(self, w_pos: WVec, dir_):
        return self._get_chunk_map_at_w_pos(w_pos + dir_ * CHUNK_W_SIZE)

    def _get_neighboring_sky_light_data(self, chunk_w_pos: WVec):
        neighboring_sky_light = {}
        for dir_ in Dir:
            dir_chunk_map = self._get_chunk_map_in_dir(chunk_w_pos, dir_)
            if dir_chunk_map is None:
                continue

            _, dir_chunk = dir_chunk_map
            neighboring_sky_light[dir_] = dir_chunk.get_sky_light_border_for(dir_)

        return neighboring_sky_light

    def get_sky_light_at_w_pos(self, w_pos: WVec):
        _, chunk = self._get_chunk_map_at_w_pos(w_pos)
        return chunk.get_sky_light_at_w_pos(w_pos)

    def _get_chunk_maps_around(self, w_pos: WVec, c_radius):
        chunks_map = {}
        for pos_x in range(
                floor(w_pos.x - c_radius * CHUNK_W_SIZE.x),
                floor(w_pos.x + (c_radius+1) * CHUNK_W_SIZE.x),
                CHUNK_W_SIZE.x
                ):
            for pos_y in range(
                    floor(w_pos.y - c_radius * CHUNK_W_SIZE.y),
                    floor(w_pos.y + (c_radius+1) * CHUNK_W_SIZE.y),
                    CHUNK_W_SIZE.y
                    ):
                chunk_map = self._get_chunk_map_at_w_pos(WVec(pos_x, pos_y))
                if chunk_map is None:
                    continue
                chunks_map.update((chunk_map,))
        return chunks_map

    def _get_blocks_map_around(self, w_pos: WVec, c_radius):
        blocks_map = {}
        for chunk in self._get_chunk_maps_around(w_pos, c_radius).values():
            blocks_map.update(chunk.blocks_map)
        return blocks_map

    def get_colliders_around(self, w_pos: WVec, c_radius):
        colliders = Colliders()
        for chunk in self._get_chunk_maps_around(w_pos, c_radius).values():
            for colliders_dir, chunk_colliders_dir in zip(colliders, chunk.colliders):
                colliders_dir += chunk_colliders_dir
        return colliders

    def get_block_pos_and_space_pos(self, start_w_pos: WVec, end_w_pos: WVec, max_distance, *, substeps=5, max_rays=3) -> BlockSelection:
        w_vel = end_w_pos - start_w_pos
        w_speed = w_vel.norm()
        w_dir = w_vel.dir_()
        w_dirs = w_vel.dirs_()

        c_radius = min(w_speed, max_distance) // max(CHUNK_W_SIZE) + 1

        block_w_pos: WVec
        block_w_pos = floor(end_w_pos)

        blocks_map = self._get_blocks_map_around(end_w_pos, c_radius)

        got_block = True
        if block_w_pos not in blocks_map:
            got_block = False
            for dir_ in w_dirs:
                if block_w_pos + dir_ in blocks_map:
                    break
            else:
                # Return early if there's no block at or next to block_w_pos:
                return BlockSelection(None, None)

        ray_origin_shift = WVec()
        w_dir_horiz, w_dir_vert = w_dirs
        if (w_dir_horiz == Dir.right) ^ (not got_block):
            ray_origin_shift.x = BLOCK_BOUND_SHIFTS.min.x
        else:
            ray_origin_shift.x = BLOCK_BOUND_SHIFTS.max.x
        if (w_dir_vert == Dir.up) ^ (not got_block):
            ray_origin_shift.y = BLOCK_BOUND_SHIFTS.min.y
        else:
            ray_origin_shift.y = BLOCK_BOUND_SHIFTS.max.y

        poss_to_check = set()
        for ray_index in range(max_rays):
            poss_to_check.add(
                block_w_pos + WVec(ray_origin_shift.x, ray_index / (max_rays-1))
                )
            poss_to_check.add(
                block_w_pos + WVec(ray_index / (max_rays-1), ray_origin_shift.y)
                )

        hits = 0
        found_path = False
        for pos_to_check in poss_to_check:
            w_vel_iter = pos_to_check - start_w_pos
            w_speed_iter = w_vel_iter.norm()
            w_vel_step = w_vel_iter / (w_speed_iter * substeps)
            max_mult = floor(w_speed_iter * substeps)
            for mult in range(max_mult + 1):
                w_pos = floor(start_w_pos + w_vel_step * mult)
                if w_pos in blocks_map and not w_pos == block_w_pos:
                    break
            else:
                hits += 1
                if hits < 2:  # This is to avoid selecting blocks for which only 1 corner is visible.
                    continue
                found_path = True
                break

        if not found_path:
            return BlockSelection(None, None)

        if got_block:
            block_w_pos_shifts = [-w_dir_horiz, -w_dir_vert]
        else:
            block_w_pos_shifts = [w_dir_vert, w_dir_horiz]
        block_center_rel_w_pos = end_w_pos - block_w_pos - WVec(0.5, 0.5)
        if -w_dir.y * block_center_rel_w_pos.y > -w_dir.x * block_center_rel_w_pos.x:
            block_w_pos_shifts.reverse()

        block_w_pos_shift = block_w_pos_shifts[0]
        if got_block:
            if block_w_pos + block_w_pos_shift in blocks_map:
                block_w_pos_shift = block_w_pos_shifts[1]
            return BlockSelection(block_w_pos, block_w_pos_shift, space_only=False)
        else:  # got space:
            if block_w_pos + block_w_pos_shift not in blocks_map:
                block_w_pos_shift = block_w_pos_shifts[1]
            return BlockSelection(block_w_pos + block_w_pos_shift, -block_w_pos_shift, space_only=True)

    def get_intersected_block_pos_and_space_pos(self, start_w_pos: WVec, end_w_pos: WVec, max_distance, *, substeps=5) -> BlockSelection:
        w_vel = end_w_pos - start_w_pos
        w_speed = w_vel.norm()
        w_dir = w_vel.dir_()
        w_vel_step = w_vel / (w_speed * substeps)
        max_mult = max_distance * substeps

        c_radius = min(w_speed, max_distance) // max(CHUNK_W_SIZE) + 1

        blocks_map = self._get_blocks_map_around(start_w_pos, c_radius)

        for mult in range(max_mult + 1):
            w_pos = floor(start_w_pos + w_vel_step * mult)
            if w_pos in blocks_map:
                break
        else:
            # If no block has been intersected up to max_distance:
            return BlockSelection(None, None)

        w_dir_horiz, w_dir_vert = w_vel.dirs_()
        block_w_pos_shifts = [-w_dir_horiz, -w_dir_vert]
        if abs(w_vel.y) > abs(w_vel.x):
            block_w_pos_shifts.reverse()

        space_only = w_vel_step.norm() * mult > w_speed
        block_w_pos_shift = block_w_pos_shifts[0]
        if w_pos + block_w_pos_shift in blocks_map:
            block_w_pos_shift = block_w_pos_shifts[1]
        return BlockSelection(w_pos, block_w_pos_shift, space_only=space_only)

    # ==== CHECK BOOLEANS ====

    @staticmethod
    def _is_pos_in_bounds(w_pos: WVec, bounds: WBounds) -> bool:
        return (bounds.min.x <= w_pos.x <= bounds.max.x
                and bounds.min.y <= w_pos.y <= bounds.max.y)

    # ==== GENERATE AND DRAW ====

    def _update_c_view(self, camera):
        """Updates c_view and returns True if there are new chunks to load, False otherwise. """
        new_c_view = CBounds(
            w_to_c_vec(camera.w_view.min),
            w_to_c_vec(camera.w_view.max),
            )

        if new_c_view == self._c_view:
            return False

        self._c_view = new_c_view
        return True

    def _light_chunk(self, chunk_map, recursion_level=0):
        """Lights the chunk and recursively calls itself to light surrounding chunks if needed.
        """
        chunk_w_pos, chunk = chunk_map

        updated_chunk_poss = {chunk_w_pos}

        if recursion_level > LIGHT_MAX_RECURSION:
            if DEBUG:
                print("Max lighting recursion reached.")
            return updated_chunk_poss

        req_relight = chunk.light(self._get_neighboring_sky_light_data(chunk_w_pos))
        for dir_ in req_relight:
            neighbor_chunk_map = self._get_chunk_map_in_dir(chunk_w_pos, dir_)
            if neighbor_chunk_map is not None:
                recursively_updated_chunk_poss = self._light_chunk(neighbor_chunk_map, recursion_level+1)
                updated_chunk_poss.update(recursively_updated_chunk_poss)
        return updated_chunk_poss

    def _draw_chunk(self, chunk_map):
        updated_chunk_poss = self._light_chunk(chunk_map)
        for chunk_w_pos in updated_chunk_poss:
            self.chunks_existing_map[chunk_w_pos].draw()

    def _create_chunk(self, chunk_w_pos, blocks_map=None):
        """Instantiates a new Chunk, draws it, lights it, updates surrounding chunks' lighting if needed and returns it.
        """
        chunk = Chunk(chunk_w_pos, self._seed, blocks_map)
        self.chunks_existing_map[chunk_w_pos] = chunk
        self._draw_chunk((chunk_w_pos, chunk))
        return chunk

    def _update_chunks_visible(self):
        self._max_view = WBounds(
            self._c_view.min * CHUNK_W_SIZE,
            (self._c_view.max+1) * CHUNK_W_SIZE,
            )

        self._chunks_visible_map = {}
        for chunk_w_pos_x in range(self._max_view.min.x, self._max_view.max.x, CHUNK_W_SIZE.x):
            for chunk_w_pos_y in range(self._max_view.min.y, self._max_view.max.y, CHUNK_W_SIZE.y):
                chunk_w_pos = WVec(chunk_w_pos_x, chunk_w_pos_y)
                if chunk_w_pos in self.chunks_existing_map:
                    chunk_visible = self.chunks_existing_map[chunk_w_pos]
                else:
                    chunk_visible = self._create_chunk(chunk_w_pos)

                self._chunks_visible_map[chunk_w_pos] = chunk_visible

    def _chunk_w_pos_to_pix_shift(self, chunk_w_pos: WVec):
        max_view_w_shift = chunk_w_pos - self._max_view.min
        return w_to_pix_shift(max_view_w_shift, CHUNK_PIX_SIZE, PixVec(self._max_surf.get_size()))

    def _draw_max_surf(self):
        self._update_chunks_visible()

        self._max_surf.fill(C_KEY)
        blit_sequence = []
        for chunk_w_pos, chunk in self._chunks_visible_map.items():
            pix_shift = self._chunk_w_pos_to_pix_shift(chunk_w_pos)
            blit_sequence.append((chunk.surf, pix_shift))
        self._max_surf.blits(blit_sequence, doreturn=False)

    def _resize_max_surf(self, camera):
        max_surf_pix_size = (w_to_c_vec(camera.w_size) + 2) * CHUNK_PIX_SIZE
        self._max_surf = pg.transform.scale(self._max_surf, max_surf_pix_size)

    def draw_and_tick(self, camera):
        are_new_chunks = self._update_c_view(camera)
        if needs_redrawing := (camera.is_zooming or self._force_draw):
            self._resize_max_surf(camera)
            self._force_draw = False
        if are_new_chunks or needs_redrawing:
            self._draw_max_surf()
        camera.draw_world(self._max_surf, self._max_view.min)
        self._tick()

    def _redraw_chunk(self, chunk_map):
        self._draw_chunk(chunk_map)
        self._force_draw = True

    # ==== MODIFY ====

    def req_break_block(self, w_pos: WVec):
        """Check whether a block can be broken at w_pos and if so, break it.
        """
        # Case where the block selector hasn't reached a block
        if w_pos is None:
            return

        if self._action_cooldown_remaining > 0:
            return

        block_w_pos = floor(w_pos)

        self._action_cooldown_remaining = ACTION_COOLDOWN_DELAY
        self._break_block(block_w_pos)

    def req_place_block(self, w_pos: WVec, block: Block, player_bounds: WBounds):
        """Check whether a block can be placed at w_pos and if so, place it.
        """
        # Case where the block selector hasn't reached a block
        if w_pos is None:
            return

        if self._action_cooldown_remaining > 0:
            return

        block_w_pos = floor(w_pos)

        if self._is_pos_in_bounds(block_w_pos, player_bounds):
            return

        self._action_cooldown_remaining = ACTION_COOLDOWN_DELAY
        self._place_block(block_w_pos, block)

    def _break_block(self, block_w_pos: WVec):
        """Request breaking of the block at block_w_pos to the relevant chunk.
        Then update the world in consequence.
        """
        chunk_map = self._get_chunk_map_at_w_pos(block_w_pos)
        if chunk_map is None:
            return

        chunk_w_pos, chunk = chunk_map
        result = chunk.req_break_block(block_w_pos)
        if result == Result.failure:
            return

        self._redraw_chunk(chunk_map)

    def _place_block(self, block_w_pos: WVec, block: Block):
        """Request placing of the block of the given block_type at block_w_pos to the relevant chunk.
        Then update the world in consequence.
        """
        chunk_map = self._get_chunk_map_at_w_pos(block_w_pos)
        if chunk_map is None:
            return

        chunk_w_pos, chunk = chunk_map
        result = chunk.req_place_block(block_w_pos, block=block)
        if result == Result.failure:
            return

        self._redraw_chunk(chunk_map)

    # ==== SAVE AND LOAD ====

    def load_from_disk(self, dir_path) -> LoadResult:
        try:
            with open(os.path.join(dir_path, self._SAVE_FILE_NAME)) as file:
                data = json.load(file)
        except FileNotFoundError:
            return LoadResult.no_file

        if data["chunk_w_size"] != CHUNK_W_SIZE:
            return LoadResult.incompatible

        self._seed = data["seed"]

        chunks_map = {}
        for chunk_w_pos_str, blocks_data_str in data["chunks_data"].items():
            chunk_w_pos = eval(chunk_w_pos_str)
            blocks_map = {}
            for block_w_pos_str, block_type_str in blocks_data_str.items():
                blocks_map[eval(block_w_pos_str)] = eval(block_type_str)
            chunks_map[chunk_w_pos] = blocks_map

        for chunk_w_pos, blocks_map in sorted(chunks_map.items(), key=lambda x: -x[0][1]):
            self.chunks_existing_map[chunk_w_pos] = self._create_chunk(chunk_w_pos, blocks_map)
        return LoadResult.success

    def save_to_disk(self, dir_path):
        data = {
            "seed": self._seed,
            "chunk_w_size": tuple(int(x) for x in CHUNK_W_SIZE),
            "chunks_data": {},
            }
        for chunk in self.chunks_existing_map.values():
            data["chunks_data"].update(chunk.collect_data())

        with open(os.path.join(dir_path, self._SAVE_FILE_NAME), "w") as file:
            json.dump(data, file, indent=4)
