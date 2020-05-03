from itertools import product

import pygame as pg

from core_funcs import world_to_chunk_pos
from global_params import CHUNK_SIZE, CHUNK_PADDING, BLOCK_PIX_SIZE
from core import WorldViewRect, WorldVec, ChunkViewRect, ChunkVec, ChunkData, Colliders
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

    def chunk_poss_in_view_rect(self, world_view_rect):
        chunk_view_rect = ChunkViewRect(
            world_to_chunk_pos(world_view_rect.pos_0),
            world_to_chunk_pos(world_view_rect.pos_1),
            )

        chunk_range_x = range(chunk_view_rect.pos_0.x, chunk_view_rect.pos_1.x + 1)
        chunk_range_y = range(chunk_view_rect.pos_0.y, chunk_view_rect.pos_1.y + 1)
        chunk_poss = product(chunk_range_x, chunk_range_y)
        return chunk_poss

    def load_chunks(self, chunk_poss):
        self.chunks_visible = {}
        for chunk_pos in chunk_poss:
            if chunk_pos in self.chunks_existing:
                chunk_to_load = self.chunks_existing[chunk_pos]
            else:
                chunk_to_load = Chunk(chunk_pos)
                self.chunks_existing[chunk_pos] = chunk_to_load

            self.chunks_visible[chunk_pos] = chunk_to_load.data

    def update(self, view_rect):
        chunk_poss_needed = self.chunk_poss_in_view_rect(view_rect)
        self.load_chunks(chunk_poss_needed)

    def draw(self, view_rect):
        self.update(view_rect)
        blit_sequence = []
        self.surface.blit()
