import math
from math import floor

import pygame as pg
import numpy as np

from global_params import BLOCK_PIX_SIZE, PLAYER_SCREEN_POS, WATER_HEIGHT, \
    CAM_POS_DAMPING_FACTOR, CAM_ZOOM_DAMPING_FACTOR, CAM_SCALE_BOUNDS, CAM_ZOOM_SPEED, FULLSCREEN
from core import WorldVec, WorldView
from core_funcs import world_to_pix_shift


class Camera:
    def __init__(self):
        self.pos = np.array((0.5, float(WATER_HEIGHT)))
        self.req_pos = self.pos

        self.zoom_vel = 1.0
        self.req_zoom_vel = 1.0

        self.scale = 64

        if FULLSCREEN:
            self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self.screen = pg.display.set_mode((1280, 720))
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
                x=self.pos[0] + self.world_size.x * (1-PLAYER_SCREEN_POS.x),
                y=self.pos[1] + self.world_size.y * (1-PLAYER_SCREEN_POS.y),
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

    def draw_player(self, anim_surf, player_pos):
        surf = anim_surf.get_surf()

        surf_scaled_pix_size = tuple(floor(dim * self.scale) for dim in anim_surf.world_size)
        max_surf_scaled = pg.transform.scale(surf, surf_scaled_pix_size)

        world_shift = WorldVec(
            *(player_pos_dim - pos_dim for pos_dim, player_pos_dim in zip(self.pos, player_pos))
            )
        pix_shift = world_to_pix_shift(world_shift, self.pix_size, surf_scaled_pix_size, self.scale)
        pix_shift = (
            pix_shift[0] + self.pix_size[0] * PLAYER_SCREEN_POS.x - surf_scaled_pix_size[0]/2,
            pix_shift[1] - self.pix_size[1] * PLAYER_SCREEN_POS.y,
            )

        self.screen.blit(max_surf_scaled, pix_shift)

    def req_zoom_in(self):
        self.req_zoom_vel = CAM_ZOOM_SPEED

    def req_zoom_out(self):
        self.req_zoom_vel = 1 / CAM_ZOOM_SPEED

    def req_zoom_stop(self):
        self.req_zoom_vel = 1.0

    @property
    def is_zooming(self):
        return not math.isclose(self.zoom_vel, 1)

    def req_update_pos(self, pos):
        self.req_pos = pos

    def animate(self):
        self.pos += (self.req_pos - self.pos) * CAM_POS_DAMPING_FACTOR

        self.zoom_vel *= (self.req_zoom_vel / self.zoom_vel) ** CAM_ZOOM_DAMPING_FACTOR
        if not(CAM_SCALE_BOUNDS[0] < self.scale < CAM_SCALE_BOUNDS[1]):
            self.zoom_vel = 1 / self.zoom_vel
        self.scale *= self.zoom_vel
