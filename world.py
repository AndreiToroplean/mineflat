from itertools import product

import pygame as pg

from core import WorldViewRect, WorldPos, ChunkViewRect, ChunkPos, ChunkData, Colliders
from chunk import Chunk


class World:
    def __init__(self, global_params):
        self.global_params = global_params

        self.data = {}

        self.surface = pg.Surface((
            self.global_params.RES[0] + (
                    self.global_params.WORLD_PADDING_IN_CHUNKS
                    * self.global_params.CHUNK_SIZE[0]
                    * self.global_params.BLOCK_SCREEN_SIZE
                    ),
            self.global_params.RES[1] + (
                    self.global_params.WORLD_PADDING_IN_CHUNKS
                    * self.global_params.CHUNK_SIZE[1]
                    * self.global_params.BLOCK_SCREEN_SIZE
                    ),
            ))

    def world_to_chunk_pos(self, world_pos):
        return [coord // chunk_dim_size for coord, chunk_dim_size in zip(world_pos, self.global_params.CHUNK_SIZE)]

    def chunks_in_view_rect(self, world_view_rect):
        chunk_view_rect = ChunkViewRect(
            ChunkPos(*self.world_to_chunk_pos(world_view_rect.pos_0)),
            ChunkPos(*self.world_to_chunk_pos(world_view_rect.pos_1)),
            )

        chunk_range_x = range(chunk_view_rect.pos_0.x, chunk_view_rect.pos_1.x + 1)
        chunk_range_y = range(chunk_view_rect.pos_0.y, chunk_view_rect.pos_1.y + 1)
        chunks = product(chunk_range_x, chunk_range_y)
        return chunks

    def load_chunks(self, chunks):
        for chunk in chunks:
            if chunk not in self.data:
                self.data.append()

    def update(self, view_rect):
        chunks_needed = self.chunks_in_view_rect(view_rect)
        self.load_chunks(chunks_needed)

    def draw(self, view_rect):
        self.update(view_rect)
