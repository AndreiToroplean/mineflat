from math import floor

import pygame as pg

from global_params import BLOCK_PIX_SIZE, PLAYER_SCREEN_POS, WATER_HEIGHT
from core import WorldVec, ChunkVec, PixVec, WorldView, ChunkView
from core_funcs import world_to_pix_shift


class Camera:
    def __init__(self):
        # transforms
        self.pos = WorldVec(0, WATER_HEIGHT)
        self.scale = 50

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.pix_size = self.screen.get_size()

    @property
    def world_size(self):
        # TODO: add memoization
        return WorldVec(*(dim / self.scale for dim in self.pix_size))

    @property
    def world_view(self):
        """World referred part of the world visible on screen. """
        return WorldView(
            pos_0=WorldVec(
                x=self.pos[0] - self.world_size.x * PLAYER_SCREEN_POS.x,
                y=self.pos[1] - self.world_size.y * PLAYER_SCREEN_POS.y,
                ),
            pos_1=WorldVec(
                x=self.pos[0] + self.world_size.x * (1 - PLAYER_SCREEN_POS.x),
                y=self.pos[1] + self.world_size.y * (1 - PLAYER_SCREEN_POS.y),
                ),
            )

    def draw_world(self, max_surf, max_view_pos):
        new_size = tuple(floor(dim * (self.scale / BLOCK_PIX_SIZE)) for dim in max_surf.get_size())
        max_surf_scaled = pg.transform.scale(max_surf, new_size)
        world_shift = WorldVec(
            *(pos_dim - max_pos_dim for pos_dim, max_pos_dim in zip(self.pos, max_view_pos))
            )
        pix_shift = world_to_pix_shift(world_shift, self.pix_size, max_surf_scaled.get_size())
        self.screen.blit(max_surf_scaled, pix_shift)

    def update_pos(self, mp_pos):
        self.pos = mp_pos
