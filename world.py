from itertools import product

import pygame as pg

from global_params import CHUNK_SIZE
from core import WorldViewRect, WorldVec, ChunkViewRect, ChunkVec, ChunkData, Colliders
from chunk import Chunk


class World:
    def __init__(self, game_params):
        self.chunks_existing = {}
        self.data = {}

        self.surface = pg.Surface((
            game_params.RES[0] + (
                    game_params.CHUNK_PADDING
                    * game_params.CHUNK_SIZE[0]
                    * game_params.BLOCK_PIX_SIZE
                    ),
            game_params.RES[1] + (
                    game_params.CHUNK_PADDING
                    * game_params.CHUNK_SIZE[1]
                    * game_params.BLOCK_PIX_SIZE
                    ),
            ))

    @staticmethod
    def world_to_chunk_pos(world_pos):
        rtn = [coord // chunk_dim_size for coord, chunk_dim_size in zip(world_pos, CHUNK_SIZE)]
        return ChunkVec(*rtn)

    def chunk_poss_in_view_rect(self, world_view_rect):
        chunk_view_rect = ChunkViewRect(
            self.world_to_chunk_pos(world_view_rect.pos_0),
            self.world_to_chunk_pos(world_view_rect.pos_1),
            )

        chunk_range_x = range(chunk_view_rect.pos_0.x, chunk_view_rect.pos_1.x + 1)
        chunk_range_y = range(chunk_view_rect.pos_0.y, chunk_view_rect.pos_1.y + 1)
        chunk_poss = product(chunk_range_x, chunk_range_y)
        return chunk_poss

    def load_chunks(self, chunk_poss):
        self.data = {}
        for chunk_pos in chunk_poss:
            if chunk_pos in self.chunks_existing:
                chunk_to_load = self.chunks_existing[chunk_pos]
            else:
                chunk_to_load = Chunk(chunk_pos)
                self.chunks_existing[chunk_pos] = chunk_to_load

            self.data[chunk_pos] = chunk_to_load.get_data()

    def update(self, view_rect):
        chunk_poss_needed = self.chunk_poss_in_view_rect(view_rect)
        self.load_chunks(chunk_poss_needed)

    def draw(self, view_rect):
        self.update(view_rect)
        # pygame logic to blit chunk_surface to self.surface
        # end of draw
