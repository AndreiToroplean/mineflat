import json
import random

import pygame as pg

from core.funcs import world_to_chunk_vec, world_to_pix_shift, world_to_chunk_to_world_vec
from core.constants import CHUNK_SIZE, CHUNK_PIX_SIZE, C_KEY
from core.classes import ChunkView, WorldView, ChunkVec, WorldVec
from world.chunk import Chunk
from world.generation import Material


class World:
    _empty_chunk_surf = pg.Surface(CHUNK_PIX_SIZE)
    _empty_chunk_surf.fill(C_KEY)

    def __init__(self):
        self._seed = random.randint(0, 2 ** 20) + 0.15681

        self.chunks_existing = {}
        self._chunks_visible = {}

        self._chunk_view = ChunkView(ChunkVec(0, 0), ChunkVec(0, 0))
        self._max_view = WorldView(WorldVec(0, 0), WorldVec(0, 0))

        self._max_surf = pg.Surface((1, 1))
        self._max_surf.set_colorkey(C_KEY)
        self._force_draw = True

    def _update_chunk_view(self, camera):
        """Updates chunk_view and returns True if there are new chunks to load, False otherwise. """
        new_chunk_view = ChunkView(
            world_to_chunk_vec(camera.world_view.pos_0),
            world_to_chunk_vec(camera.world_view.pos_1),
            )

        if new_chunk_view == self._chunk_view:
            return False

        self._chunk_view = new_chunk_view
        return True

    def _load_chunks(self):
        self._max_view = WorldView(
            WorldVec(*[dim * chunk_size_dim for dim, chunk_size_dim in zip(self._chunk_view.pos_0, CHUNK_SIZE)]),
            WorldVec(*[(dim+1) * chunk_size_dim for dim, chunk_size_dim in zip(self._chunk_view.pos_1, CHUNK_SIZE)]),
            )

        self._chunks_visible = {}
        for chunk_world_pos_x in range(self._max_view.pos_0.x, self._max_view.pos_1.x, CHUNK_SIZE.x):
            for chunk_world_pos_y in range(self._max_view.pos_0.y, self._max_view.pos_1.y, CHUNK_SIZE.y):
                chunk_world_pos = WorldVec(chunk_world_pos_x, chunk_world_pos_y)
                if chunk_world_pos in self.chunks_existing:
                    chunk_to_load = self.chunks_existing[chunk_world_pos]
                else:
                    chunk_to_load = Chunk(chunk_world_pos, self._seed)
                    self.chunks_existing[chunk_world_pos] = chunk_to_load

                self._chunks_visible[chunk_world_pos] = chunk_to_load

    def _chunk_pos_to_pix_shift(self, chunk_world_pos):
        max_view_world_shift = WorldVec(*(pos - shift for pos, shift in zip(chunk_world_pos, self._max_view.pos_0)))
        return world_to_pix_shift(max_view_world_shift, CHUNK_PIX_SIZE, self._max_surf.get_size())

    def _draw_max_surf(self):
        self._load_chunks()

        self._max_surf.fill(C_KEY)
        blit_sequence = []
        for chunk_world_pos, chunk in self._chunks_visible.items():
            pix_shift = self._chunk_pos_to_pix_shift(chunk_world_pos)
            blit_sequence.append((chunk.surf, pix_shift))
        self._max_surf.blits(blit_sequence, doreturn=False)

    def _resize_max_surf(self, camera):
        max_surf_pix_size = tuple(
            (dim + 2) * pix
            for dim, pix in zip(world_to_chunk_vec(camera.world_size), CHUNK_PIX_SIZE)
            )
        self._max_surf = pg.transform.scale(self._max_surf, max_surf_pix_size)

    def draw(self, camera):
        are_new_chunks = self._update_chunk_view(camera)
        if needs_redrawing := (camera.is_zooming or self._force_draw):
            self._resize_max_surf(camera)
            self._force_draw = False
        if are_new_chunks or needs_redrawing:
            self._draw_max_surf()
        camera.draw_world(self._max_surf, self._max_view.pos_0)

    def _get_chunk_at_pos(self, pos):
        chunk_world_pos = world_to_chunk_to_world_vec(pos)
        try:
            chunk = self.chunks_existing[chunk_world_pos]
        except KeyError:
            return None, None

        return chunk, chunk_world_pos

    def _redraw_chunk(self, chunk_world_pos, chunk_surf):
        pix_shift = self._chunk_pos_to_pix_shift(chunk_world_pos)
        self._max_surf.blit(self._empty_chunk_surf, pix_shift)
        self._max_surf.blit(chunk_surf, pix_shift)

    def req_break_block(self, world_pos):
        chunk, chunk_world_pos = self._get_chunk_at_pos(world_pos)
        if chunk is None:
            return
        chunk.req_break_block(world_pos)
        self._redraw_chunk(chunk_world_pos, chunk.surf)

    def req_place_block(self, world_pos, material):
        chunk, chunk_world_pos = self._get_chunk_at_pos(world_pos)
        if chunk is None:
            return
        chunk.req_place_block(world_pos, material=material)
        self._redraw_chunk(chunk_world_pos, chunk.surf)

    def load_from_disk(self, file_path):
        try:
            with open(file_path) as file:
                data = json.load(file)
        except FileNotFoundError:
            return
        self._seed = data["seed"]
        for chunk_world_pos_str, blocks_data_str in data["chunks_data"].items():
            chunk_world_pos = eval(chunk_world_pos_str)
            blocks_data = {}
            for block_world_pos_str, material_str in blocks_data_str.items():
                blocks_data[eval(block_world_pos_str)] = eval(material_str)
            self.chunks_existing[chunk_world_pos] = Chunk(chunk_world_pos, self._seed, blocks_data)

    def save_to_disk(self, file_path):
        data = {"seed": self._seed, "chunks_data": {}}
        for chunk in self.chunks_existing.values():
            data["chunks_data"].update(chunk.get_chunk_data())

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
