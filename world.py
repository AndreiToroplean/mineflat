from itertools import product
from math import floor

import pygame as pg

from core_funcs import world_to_chunk_pos, world_to_pix_shift
from global_params import CHUNK_SIZE, CHUNK_PADDING, BLOCK_PIX_SIZE, CHUNK_PIX_SIZE
from core import ChunkViewRect, WorldViewRect, PixVec, ChunkVec, WorldVec
from chunk import Chunk


class World:
    def __init__(self, game_params):
        self.chunks_existing = {}
        self.chunks_visible = {}

        self.surface = pg.Surface((
            game_params.RES[0] + (
                    CHUNK_PADDING
                    * CHUNK_SIZE[0]
                    * BLOCK_PIX_SIZE
                    ),
            game_params.RES[1] + (
                    CHUNK_PADDING
                    * CHUNK_SIZE[1]
                    * BLOCK_PIX_SIZE
                    ),
            ))
        self.surface_world_shift = WorldVec(0, 0)
        self.chunks_world_shift = ChunkVec(0, 0)

    def load_chunks(self, view_rect):
        self.chunks_visible = {}

        chunk_view_rect = ChunkViewRect(
            world_to_chunk_pos(view_rect.pos_0),
            world_to_chunk_pos(view_rect.pos_1),
            )

        max_view_rect = WorldViewRect(
            WorldVec(*[dim * chunk_size_dim for dim, chunk_size_dim in zip(chunk_view_rect.pos_0, CHUNK_SIZE)]),
            WorldVec(*[(dim+1) * chunk_size_dim for dim, chunk_size_dim in zip(chunk_view_rect.pos_0, CHUNK_SIZE)]),
            )

        self.surface_world_shift = WorldVec(
            *[view_dim - max_view_dim for view_dim, max_view_dim in zip(view_rect.pos_0, max_view_rect.pos_0)]
            )
        self.chunks_world_shift = max_view_rect.pos_0

        for chunk_world_pos_x in range(max_view_rect.pos_0.x, max_view_rect.pos_1.x, CHUNK_SIZE.x):
            for chunk_world_pos_y in range(max_view_rect.pos_0.y, max_view_rect.pos_1.y, CHUNK_SIZE.y):
                chunk_world_pos = WorldVec(chunk_world_pos_x, chunk_world_pos_y)
                if chunk_world_pos in self.chunks_existing:
                    chunk_to_load = self.chunks_existing[chunk_world_pos]
                else:
                    chunk_to_load = Chunk(chunk_world_pos)
                    self.chunks_existing[chunk_world_pos] = chunk_to_load

                self.chunks_visible[chunk_world_pos] = chunk_to_load.data

    def draw(self, view_rect):
        self.load_chunks(view_rect)
        world_pos_to_pix_shift = lambda world_pos: PixVec(
            *world_to_pix_shift([pos-shift for pos, shift in zip(world_pos, self.chunks_world_shift)], self.surface.get_size())
            )
        blit_sequence = [(
            chunk.surface,
            world_pos_to_pix_shift(world_pos)
            ) for world_pos, chunk in self.chunks_visible.items()]
        self.surface.blits(blit_sequence)

    def get_surface(self, view_rect, screen_res):
        self.draw(view_rect)
        return self.surface, world_to_pix_shift(self.surface_world_shift, screen_res)
