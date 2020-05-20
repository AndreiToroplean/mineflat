import math
from math import floor

import numpy as np
import pygame as pg

from core.classes import WVec, WView
from core.funcs import w_to_pix_shift, pix_to_w_shift
from core.constants import BLOCK_PIX_SIZE, PLAYER_S_POS, FULLSCREEN, C_KEY, CAM_FPS, C_SKY, CAM_DEFAULT_SCALE, \
    CAM_SCALE_BOUNDS


class Camera:
    _ZOOM_SPEED = 1.05
    _VEL_DAMPING_FACTOR = 0.5
    _POS_DAMPING_FACTOR = 0.1
    _ZOOM_VEL_DAMPING_FACTOR = 0.1
    _SCALE_COLLISION_DAMPING_FACTOR = 0.75

    def __init__(self):
        self._pos = np.array((0.0, 0.0))
        self._req_pos = np.array(self._pos)

        self._vel = np.array((0.0, 0.0))
        self._req_vel = np.array(self._vel)

        self._zoom_vel = 1.0
        self._req_zoom_vel = 1.0

        self._scale = CAM_DEFAULT_SCALE

        self.selected_block_w_pos = np.array(self._pos)
        self.selected_space_w_pos = np.array(self._pos)
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
    def w_size(self):
        # TODO: add memoization
        return WVec(*(dim / self._scale for dim in self._pix_size))

    @property
    def w_view(self):
        """World referred part of the world visible on screen. """
        return WView(
            pos_0=WVec(
                x=self._pos[0] - self.w_size.x * PLAYER_S_POS.x,
                y=self._pos[1] - self.w_size.y * PLAYER_S_POS.y,
                ),
            pos_1=WVec(
                x=self._pos[0] + self.w_size.x * (1 - PLAYER_S_POS.x),
                y=self._pos[1] + self.w_size.y * (1 - PLAYER_S_POS.y),
                ),
            )

    def draw_sky(self):
        self._screen.fill(C_SKY)

    def draw_world(self, max_surf, max_view_pos):
        max_surf_scaled_pix_size = tuple(floor(dim * (self._scale / BLOCK_PIX_SIZE)) for dim in max_surf.get_size())
        max_surf_scaled = pg.transform.scale(max_surf, max_surf_scaled_pix_size)
        w_shift = WVec(
            *(max_pos_dim - pos_dim for pos_dim, max_pos_dim in zip(self._pos, max_view_pos))
            )
        pix_shift = w_to_pix_shift(
            w_shift,
            max_surf_scaled_pix_size,
            self._pix_size,
            dest_pivot=(self._pix_size[0] * PLAYER_S_POS.x, self._pix_size[1] * PLAYER_S_POS.y),
            scale=self._scale
            )

        self._screen.blit(max_surf_scaled, pix_shift)

    def draw_player(self, anim_surf, player_pos):
        surf = anim_surf.get_surf_and_advance()

        surf_scaled_pix_size = tuple(floor(dim * self._scale) for dim in anim_surf.w_size)
        surf_scaled = pg.transform.scale(surf, surf_scaled_pix_size)

        w_shift = WVec(
            *(player_pos_dim - pos_dim for player_pos_dim, pos_dim in zip(player_pos, self._pos))
            )
        pix_shift = w_to_pix_shift(
            w_shift,
            surf_scaled_pix_size,
            self._pix_size,
            source_pivot=(surf_scaled_pix_size[0] / 2, 0),
            dest_pivot=(self._pix_size[0] * PLAYER_S_POS.x, self._pix_size[1] * PLAYER_S_POS.y),
            scale=self._scale
            )

        self._screen.blit(surf_scaled, pix_shift)

    def _select_block(self, action_w_pos, world, threshold=0.01):
        mouse_pix_shift = pg.mouse.get_pos()
        mouse_w_shift = pix_to_w_shift(
            mouse_pix_shift,
            (0, 0),
            self._pix_size,
            dest_pivot=(self._pix_size[0] * PLAYER_S_POS.x, self._pix_size[1] * PLAYER_S_POS.y),
            scale=self._scale,
            )
        mouse_w_pos = np.array(
            tuple(w_shift_dim + cam_pos_dim for w_shift_dim, cam_pos_dim in zip(mouse_w_shift, self._pos))
            )

        selection = world.intersect_block(action_w_pos, mouse_w_pos, threshold=threshold)

        return selection

    def draw_gui_block_selector(self, action_w_pos, world, threshold=0.01):
        selection = self._select_block(action_w_pos, world, threshold)
        if selection is None:
            self.selected_block_w_pos = None
            self.selected_space_w_pos = None
            return
        selected_block, selected_space = selection
        self.selected_block_w_pos = selected_block[0]
        self.selected_space_w_pos = selected_space[0]

        surf_pix_size = (floor(self._scale), floor(self._scale))
        surf = pg.transform.scale(self._block_selector_surf, surf_pix_size)

        w_shift = np.array(
            tuple(floor(mouse_pos_dim) - pos_dim for mouse_pos_dim, pos_dim in zip(
                self.selected_block_w_pos,
                self._pos
                ))
            )
        pix_shift = w_to_pix_shift(
            w_shift,
            surf_pix_size,
            self._pix_size,
            source_pivot=(-1, 1),
            dest_pivot=(self._pix_size[0] * PLAYER_S_POS.x, self._pix_size[1] * PLAYER_S_POS.y),
            scale=self._scale)

        self._screen.blit(surf, pix_shift)

    def req_zoom_in(self):
        self._req_zoom_vel = self._ZOOM_SPEED

    def req_zoom_out(self):
        self._req_zoom_vel = 1 / self._ZOOM_SPEED

    def req_zoom_stop(self):
        self._req_zoom_vel = 1.0

    @property
    def is_zooming(self):
        return not math.isclose(self._zoom_vel, 1)

    def req_move(self, pos):
        self._req_vel = pos - self._pos

    def set_transforms(self, pos, vel=(0.0, 0.0)):
        self._pos = np.array(pos)
        self._req_pos = np.array(self._pos)

        self._vel = np.array(vel)
        self._req_vel = np.array(self._vel)

    def move(self, threshold=0.001):
        self._vel += (self._req_vel - self._vel) * self._VEL_DAMPING_FACTOR
        self._pos += [vel_dim * self._POS_DAMPING_FACTOR ** (1 / (1 + abs(vel_dim))) for vel_dim in self._vel]
        # (1/(1+speed)) is 1 when speed is 0 and is 0 when speed is +inf.
        # This is so that the CAM_POS_DAMPING_FACTOR is only applied at low speeds.

        self._zoom_vel *= (self._req_zoom_vel / self._zoom_vel) ** self._ZOOM_VEL_DAMPING_FACTOR
        if CAM_SCALE_BOUNDS[0] > self._scale:
            self._zoom_vel = 1.0
            self._scale = CAM_SCALE_BOUNDS[0] * (1+threshold)
        if self._scale > CAM_SCALE_BOUNDS[1]:
            self._zoom_vel = 1.0
            self._scale = CAM_SCALE_BOUNDS[1] / (1+threshold)
        self._scale *= self._zoom_vel

    def draw_debug_info(self):
        fps_surf = self._font.render(f"{self._clock.get_fps():.1f}", True, (255, 255, 255))
        self._screen.blit(fps_surf, (20, 20))

    def display_flip_and_clock_tick(self):
        pg.display.flip()
        self._clock.tick(CAM_FPS)
