from math import floor

import pygame as pg

from global_params import BLOCK_PIX_SIZE, CHUNK_PIX_SIZE, CHUNK_SIZE, PLAYER_SCREEN_POS, WATER_HEIGHT
from core import WorldVec, ChunkVec, PixVec, WorldView, ChunkView
from core_funcs import world_to_pix_shift


class Camera:
    zoom_speed = 1.01

    def __init__(self):
        # transforms
        self.pos = WorldVec(0, WATER_HEIGHT)
        self.scale = 64
        self.zoom_vel = 1.0

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
        max_surf_scaled_pix_size = tuple(floor(dim * (self.scale / BLOCK_PIX_SIZE)) for dim in max_surf.get_size())
        max_surf_scaled = pg.transform.scale(max_surf, max_surf_scaled_pix_size)
        world_shift = WorldVec(
            *(max_pos_dim - pos_dim for pos_dim, max_pos_dim in zip(self.pos, max_view_pos))
            )
        pix_shift = world_to_pix_shift(world_shift, self.pix_size, max_surf_scaled_pix_size, self.scale)
        pix_shift = (
            pix_shift[0] + self.pix_size[0] * PLAYER_SCREEN_POS.x,
            pix_shift[1] - self.pix_size[1] * PLAYER_SCREEN_POS.y,
            )
        self.screen.blit(max_surf_scaled, pix_shift)

    def draw_player(self, anim_surf):
        surf = anim_surf.get_surf()

        surf_scaled_pix_size = tuple(floor(dim * self.scale) for dim in anim_surf.world_size)
        max_surf_scaled = pg.transform.scale(surf, surf_scaled_pix_size)
        pix_shift = (
            self.pix_size[0] * PLAYER_SCREEN_POS.x,
            self.pix_size[1] * PLAYER_SCREEN_POS.y,
            )
        self.screen.blit(max_surf_scaled, pix_shift)

    def update_pos(self, mp_pos):
        self.pos = mp_pos

    def zoom_in(self):
        self.zoom_vel = self.zoom_speed

    def zoom_out(self):
        self.zoom_vel = 1 / self.zoom_speed

    def zoom_stop(self):
        self.zoom_vel = 1.0

    def animate(self):
        self.scale *= self.zoom_vel
