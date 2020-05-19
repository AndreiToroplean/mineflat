import math
from math import floor

import numpy as np
import pygame as pg

from core.classes import WorldVec, WorldView
from core.funcs import world_to_pix_shift, pix_to_world_shift
from core.constants import BLOCK_PIX_SIZE, PLAYER_SCREEN_POS, CAM_POS_DAMPING_FACTOR, CAM_ZOOM_DAMPING_FACTOR, \
    CAM_SCALE_BOUNDS, CAM_ZOOM_SPEED, FULLSCREEN, CAM_DEFAULT_SCALE, C_KEY, CAM_FPS, C_SKY, CAM_VEL_DAMPING_FACTOR, \
    CAM_SCALE_COLLISION_DAMPING_FACTOR


class Camera:
    def __init__(self, pos):
        self._pos = np.array(pos)
        self._req_pos = np.array(self._pos)

        self._vel = np.array((0.0, 0.0))
        self._req_vel = np.array((0.0, 0.0))

        self._zoom_vel = 1.0
        self._req_zoom_vel = 1.0

        self._scale = CAM_DEFAULT_SCALE

        self.mouse_world_pos = np.array(self._pos)
        self._block_selector_surf = pg.image.load("resources/gui/block_selector.png")
        self._block_selector_surf.set_colorkey(C_KEY)

        if FULLSCREEN:
            self._screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self._screen = pg.display.set_mode((1280, 720))
        self._pix_size = self._screen.get_size()

        self._clock = pg.time.Clock()
        self._font = pg.font.SysFont(pg.font.get_default_font(), 24)

    @property
    def world_size(self):
        # TODO: add memoization
        return WorldVec(*(dim / self._scale for dim in self._pix_size))

    @property
    def world_view(self):
        """World referred part of the world visible on screen. """
        return WorldView(
            pos_0=WorldVec(
                x=self._pos[0] - self.world_size.x * PLAYER_SCREEN_POS.x,
                y=self._pos[1] - self.world_size.y * PLAYER_SCREEN_POS.y,
                ),
            pos_1=WorldVec(
                x=self._pos[0] + self.world_size.x * (1 - PLAYER_SCREEN_POS.x),
                y=self._pos[1] + self.world_size.y * (1 - PLAYER_SCREEN_POS.y),
                ),
            )

    def draw_sky(self):
        self._screen.fill(C_SKY)

    def draw_world(self, max_surf, max_view_pos):
        max_surf_scaled_pix_size = tuple(floor(dim * (self._scale / BLOCK_PIX_SIZE)) for dim in max_surf.get_size())
        max_surf_scaled = pg.transform.scale(max_surf, max_surf_scaled_pix_size)
        world_shift = WorldVec(
            *(max_pos_dim - pos_dim for pos_dim, max_pos_dim in zip(self._pos, max_view_pos))
            )
        pix_shift = world_to_pix_shift(
            world_shift,
            max_surf_scaled_pix_size,
            self._pix_size,
            dest_pivot=(self._pix_size[0] * PLAYER_SCREEN_POS.x, self._pix_size[1] * PLAYER_SCREEN_POS.y),
            scale=self._scale
            )

        self._screen.blit(max_surf_scaled, pix_shift)

    def draw_player(self, anim_surf, player_pos):
        surf = anim_surf.get_surf_and_advance()

        surf_scaled_pix_size = tuple(floor(dim * self._scale) for dim in anim_surf.world_size)
        surf_scaled = pg.transform.scale(surf, surf_scaled_pix_size)

        world_shift = WorldVec(
            *(player_pos_dim - pos_dim for player_pos_dim, pos_dim in zip(player_pos, self._pos))
            )
        pix_shift = world_to_pix_shift(
            world_shift,
            surf_scaled_pix_size,
            self._pix_size,
            source_pivot=(surf_scaled_pix_size[0] / 2, 0),
            dest_pivot=(self._pix_size[0] * PLAYER_SCREEN_POS.x, self._pix_size[1] * PLAYER_SCREEN_POS.y),
            scale=self._scale
            )

        self._screen.blit(surf_scaled, pix_shift)

    def _update_mouse_world_pos(self):
        mouse_pix_shift = pg.mouse.get_pos()
        mouse_world_shift = pix_to_world_shift(
            mouse_pix_shift,
            (0, 0),
            self._pix_size,
            dest_pivot=(self._pix_size[0] * PLAYER_SCREEN_POS.x, self._pix_size[1] * PLAYER_SCREEN_POS.y),
            scale=self._scale,
            )
        mouse_world_pos = WorldVec(
            *(world_shift_dim + cam_pos_dim for world_shift_dim, cam_pos_dim in zip(mouse_world_shift, self._pos))
            )
        self.mouse_world_pos = mouse_world_pos

    def draw_gui_block_selector(self):
        self._update_mouse_world_pos()
        surf_pix_size = (floor(self._scale), floor(self._scale))
        surf = pg.transform.scale(self._block_selector_surf, surf_pix_size)
        world_shift = WorldVec(
            *(floor(mouse_pos_dim) - pos_dim for mouse_pos_dim, pos_dim in zip(self.mouse_world_pos, self._pos))
            )
        pix_shift = world_to_pix_shift(
            world_shift,
            surf_pix_size,
            self._pix_size,
            source_pivot=(-1, 1),
            dest_pivot=(self._pix_size[0] * PLAYER_SCREEN_POS.x, self._pix_size[1] * PLAYER_SCREEN_POS.y),
            scale=self._scale)

        self._screen.blit(surf, pix_shift)

    def req_zoom_in(self):
        self._req_zoom_vel = CAM_ZOOM_SPEED

    def req_zoom_out(self):
        self._req_zoom_vel = 1 / CAM_ZOOM_SPEED

    def req_zoom_stop(self):
        self._req_zoom_vel = 1.0

    @property
    def is_zooming(self):
        return not math.isclose(self._zoom_vel, 1)

    def req_move(self, pos):
        self._req_vel = pos - self._pos

    def move(self):
        self._vel += (self._req_vel - self._vel) * CAM_VEL_DAMPING_FACTOR
        self._pos += [vel_dim * CAM_POS_DAMPING_FACTOR**(1/(1+abs(vel_dim))) for vel_dim in self._vel]
        # (1/(1+speed)) is 1 when speed is 0 and is 0 when speed is +inf.
        # This is so that the CAM_POS_DAMPING_FACTOR is only applied at low speeds.

        self._zoom_vel *= (self._req_zoom_vel / self._zoom_vel) ** CAM_ZOOM_DAMPING_FACTOR
        threshold = 1.001
        if CAM_SCALE_BOUNDS[0] > self._scale:
            self._zoom_vel = (1 / self._zoom_vel) ** CAM_SCALE_COLLISION_DAMPING_FACTOR
            self._scale = CAM_SCALE_BOUNDS[0] * threshold
        if self._scale > CAM_SCALE_BOUNDS[1]:
            self._zoom_vel = (1 / self._zoom_vel) ** CAM_SCALE_COLLISION_DAMPING_FACTOR
            self._scale = CAM_SCALE_BOUNDS[1] / threshold
        self._scale *= self._zoom_vel

    def draw_debug_info(self):
        fps_surf = self._font.render(f"{self._clock.get_fps():.1f}", True, (255, 255, 255))
        self._screen.blit(fps_surf, (20, 20))

    def display_flip_and_clock_tick(self):
        pg.display.flip()
        self._clock.tick(CAM_FPS)
