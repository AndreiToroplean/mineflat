import pygame as pg

from core_funcs import world_to_chunk_pos, world_to_pix_shift
from global_params import CHUNK_SIZE, CHUNK_PIX_SIZE, CHUNK_PADDING, BLOCK_PIX_SIZE, PLAYER_SCREEN_POS, C_KEY
from core import ChunkViewRect, WorldViewRect, PixVec, ChunkVec, WorldVec
from chunk import Chunk


class World:
    def __init__(self, screen_res):
        self.chunks_existing = {}
        self.chunks_data = {}

        self.surface = None

        self.surface_world_shift = WorldVec(0, 0)
        self.chunks_world_shift = ChunkVec(0, 0)
        self.view_rect = WorldViewRect(
            WorldVec(0, 0),
            WorldVec(0, 0),
            )

        self.screen_res = screen_res
        self.BLOCKS_ON_SCREEN = tuple(x / BLOCK_PIX_SIZE for x in self.screen_res)
        self.BLOCKS_ON_EACH_SIDE = (
            self.BLOCKS_ON_SCREEN[0] * PLAYER_SCREEN_POS[0],
            self.BLOCKS_ON_SCREEN[1] * PLAYER_SCREEN_POS[1],
            self.BLOCKS_ON_SCREEN[0] * (1 - PLAYER_SCREEN_POS[0]),
            self.BLOCKS_ON_SCREEN[1] * (1 - PLAYER_SCREEN_POS[1]),
            )

    def update_view_rect(self, mp_pos):
        """World referred part of the world visible on screen. """
        self.view_rect = WorldViewRect(
            WorldVec(
                x=mp_pos[0] - self.BLOCKS_ON_EACH_SIDE[0],
                y=mp_pos[1] - self.BLOCKS_ON_EACH_SIDE[1],
                ),
            WorldVec(
                x=mp_pos[0] + self.BLOCKS_ON_EACH_SIDE[2],
                y=mp_pos[1] + self.BLOCKS_ON_EACH_SIDE[3],
                ),
            )

    def load_chunks(self):
        self.chunks_data = {}

        chunk_view_rect = ChunkViewRect(
            world_to_chunk_pos(self.view_rect.pos_0),
            world_to_chunk_pos(self.view_rect.pos_1),
            )

        res = PixVec(
            x=(1 + chunk_view_rect.pos_1.x - chunk_view_rect.pos_0.x) * CHUNK_PIX_SIZE.x,
            y=(1 + chunk_view_rect.pos_1.y - chunk_view_rect.pos_0.y) * CHUNK_PIX_SIZE.y,
            )

        self.surface = pg.Surface(res)  # FIXME: maybe don't recreate a surface every time...
        self.surface.set_colorkey(C_KEY)

        max_view_rect = WorldViewRect(
            WorldVec(*[dim * chunk_size_dim for dim, chunk_size_dim in zip(chunk_view_rect.pos_0, CHUNK_SIZE)]),
            WorldVec(*[(dim+1) * chunk_size_dim for dim, chunk_size_dim in zip(chunk_view_rect.pos_1, CHUNK_SIZE)]),
            )

        self.surface_world_shift = WorldVec(
            *(max_view_dim - view_dim for view_dim, max_view_dim in zip(self.view_rect.pos_0, max_view_rect.pos_0))
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

                self.chunks_data[chunk_world_pos] = chunk_to_load.data

    def draw(self):
        self.load_chunks()

        self.surface.fill(C_KEY)
        blit_sequence = []
        for world_pos, (surface, _) in self.chunks_data.items():
            world_shift = WorldVec(*(pos - shift for pos, shift in zip(world_pos, self.chunks_world_shift)))
            pix_shift = PixVec(*world_to_pix_shift(world_shift, self.surface.get_size(), CHUNK_PIX_SIZE))
            blit_sequence.append((surface, pix_shift))
        self.surface.blits(blit_sequence)

    def get_surface(self, mp_pos):
        self.update_view_rect(mp_pos)
        self.draw()
        return self.surface, world_to_pix_shift(self.surface_world_shift, self.screen_res, (0, 0))


if __name__ == "__main__":
    from debug.display import Display
    from global_params import WATER_HEIGHT

    def main():
        world = World((1920, 1080))
        test_surf, _ = world.get_surface((0, WATER_HEIGHT-10))
        Display(test_surf)
    main()
