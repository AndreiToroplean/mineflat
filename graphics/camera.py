import math
import os
from math import floor

import pygame as pg

from core.classes import WVec, BlockSelection, WBounds, PixVec
from core.funcs import w_to_pix_shift, pix_to_w_shift, light_level_to_color_int
from core.constants import BLOCK_PIX_SIZE, PLAYER_S_POS, FULLSCREEN, C_KEY, CAM_FPS, CAM_DEFAULT_SCALE, \
    CAM_SCALE_BOUNDS, DIR_TO_ANGLE, GUI_PATH, ACTION_MAX_DISTANCE, PIX_ORIGIN


class Camera:
    _ZOOM_SPEED = 1.05
    _VEL_DAMPING_FACTOR = 0.5
    _POS_DAMPING_FACTOR = 0.1
    _ZOOM_VEL_DAMPING_FACTOR = 0.1
    _SCALE_COLLISION_DAMPING_FACTOR = 0.75

    def __init__(self):
        self._pos = WVec()
        self._req_pos = WVec(self._pos)

        self._vel = WVec()
        self._req_vel = WVec(self._vel)

        self._zoom_vel = 1.0
        self._req_zoom_vel = 1.0

        self._scale = CAM_DEFAULT_SCALE

        if FULLSCREEN:
            self._screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        else:
            self._screen = pg.display.set_mode((1280, 720))
        self._pix_size = PixVec(self._screen.get_size())

        self.selected_block_w_pos = WVec(self._pos)
        self.selected_space_w_pos = WVec(self._pos)
        self._block_selector_surf = pg.image.load(os.path.join(GUI_PATH, "block_selector.png")).convert()
        self._block_selector_space_only_surf = pg.image.load(os.path.join(GUI_PATH, "block_selector_space_only.png")).convert()

        # Surfs to reuse
        self._world_max_surf_scaled = pg.Surface((0, 0))
        self._player_surf_scaled = pg.Surface((0, 0))
        self._player_surf_scaled.set_colorkey(C_KEY)
        self._block_selector_surf_scaled = pg.Surface((0, 0))
        self._block_selector_surf_scaled.set_colorkey(C_KEY)

        self._clock = pg.time.Clock()
        self._font = pg.font.SysFont(pg.font.get_default_font(), 24)

    # ==== GET DATA ====

    @property
    def w_size(self):
        return self._pix_size / self._scale

    @property
    def w_view(self):
        """World referred part of the world visible on screen. """
        return WBounds(
            min=self._pos - self.w_size * PLAYER_S_POS,
            max=self._pos + self.w_size * (1-PLAYER_S_POS),
            )

    @property
    def _mouse_w_pos(self):
        mouse_pix_shift = PixVec(pg.mouse.get_pos())
        mouse_w_shift = pix_to_w_shift(
            mouse_pix_shift,
            (0, 0),
            self._pix_size,
            dest_pivot=(self._pix_size.x * PLAYER_S_POS.x, self._pix_size.y * PLAYER_S_POS.y),
            scale=self._scale,
            )
        mouse_w_pos = mouse_w_shift + self._pos
        return mouse_w_pos

    @property
    def is_zooming(self):
        return not math.isclose(self._zoom_vel, 1)

    def _select_block(self, action_w_pos: WVec, world, *, substeps=5, max_rays=3) -> BlockSelection:
        """Return selection based on player position and mouse position.
        Selection is one selected block and one selected space.
        """
        selection: BlockSelection
        selection = world.get_block_pos_and_space_pos(
            action_w_pos,
            self._mouse_w_pos,
            ACTION_MAX_DISTANCE,
            substeps=substeps,
            max_rays=max_rays,
            )

        if selection.block_w_pos is not None:
            return selection
        else:
            space_only = selection.space_only

        selection = world.get_intersected_block_pos_and_space_pos(
            action_w_pos,
            self._mouse_w_pos,
            ACTION_MAX_DISTANCE,
            substeps=substeps,
            )

        return BlockSelection(selection.block_w_pos, selection.space_w_pos_shift, space_only)

    # ==== DRAW ====

    def draw_world(self, max_surf, max_view_pos: WVec):
        max_surf_scaled_pix_size = floor(PixVec(max_surf.get_size()) * (self._scale / BLOCK_PIX_SIZE))
        if self._world_max_surf_scaled.get_size() != max_surf_scaled_pix_size:
            self._world_max_surf_scaled = pg.transform.scale(self._world_max_surf_scaled, max_surf_scaled_pix_size)
        self._world_max_surf_scaled = pg.transform.scale(max_surf, max_surf_scaled_pix_size, self._world_max_surf_scaled)

        w_shift = max_view_pos - self._pos
        pix_shift = w_to_pix_shift(
            w_shift,
            max_surf_scaled_pix_size,
            self._pix_size,
            dest_pivot=(self._pix_size.x * PLAYER_S_POS.x, self._pix_size.y * PLAYER_S_POS.y),
            scale=self._scale
            )

        self._screen.blit(self._world_max_surf_scaled, pix_shift)

    def draw_player(self, anim_surf, player_pos: WVec, sky_light):
        anim_surf.draw_and_tick(sky_light)

        surf_scaled_pix_size = floor(anim_surf.w_size * self._scale)
        if self._player_surf_scaled.get_size() != surf_scaled_pix_size:
            self._player_surf_scaled = pg.transform.scale(self._player_surf_scaled, surf_scaled_pix_size)
        self._player_surf_scaled = pg.transform.scale(anim_surf.surf, surf_scaled_pix_size, self._player_surf_scaled)

        w_shift = player_pos - self._pos
        pix_shift = w_to_pix_shift(
            w_shift,
            surf_scaled_pix_size,
            self._pix_size,
            source_pivot=(surf_scaled_pix_size.x / 2, 0),
            dest_pivot=(self._pix_size.x * PLAYER_S_POS.x, self._pix_size.y * PLAYER_S_POS.y),
            scale=self._scale
            )

        self._screen.blit(self._player_surf_scaled, pix_shift)

    def draw_block_selector(self, action_w_pos: WVec, world):
        selection: BlockSelection
        selection = self._select_block(action_w_pos, world)
        if selection.block_w_pos is None:
            self.selected_block_w_pos = None
            self.selected_space_w_pos = None
            return

        self.selected_block_w_pos = selection.block_w_pos
        self.selected_space_w_pos = self.selected_block_w_pos + selection.space_w_pos_shift

        surf_pix_size = (floor(self._scale), floor(self._scale))
        if not selection.space_only:
            surf = self._block_selector_surf
        else:
            surf = self._block_selector_space_only_surf

        if self._block_selector_surf_scaled.get_size() != surf_pix_size:
            self._block_selector_surf_scaled = pg.transform.scale(self._block_selector_surf_scaled, surf_pix_size)
        self._block_selector_surf_scaled = pg.transform.scale(surf, surf_pix_size, self._block_selector_surf_scaled)
        self._block_selector_surf_scaled = pg.transform.rotate(self._block_selector_surf_scaled, DIR_TO_ANGLE[selection.space_w_pos_shift])

        w_shift = floor(self.selected_block_w_pos) - self._pos

        if selection.space_only:
            self.selected_block_w_pos = None

        pix_shift = w_to_pix_shift(
            w_shift,
            surf_pix_size,
            self._pix_size,
            source_pivot=(-1, 1),
            dest_pivot=(self._pix_size.x * PLAYER_S_POS.x, self._pix_size.y * PLAYER_S_POS.y),
            scale=self._scale)

        self._screen.blit(self._block_selector_surf_scaled, pix_shift)

    def draw_debug_info(self):
        fps_surf = self._font.render(f"{self._clock.get_fps():.1f}", True, (255, 255, 255))
        self._screen.blit(fps_surf, (20, 20))

    def display_flip_and_clock_tick(self):
        pg.display.flip()
        self._clock.tick(CAM_FPS)

    # ==== REQUEST MOVEMENTS ====

    def req_zoom_in(self):
        self._req_zoom_vel = self._ZOOM_SPEED

    def req_zoom_out(self):
        self._req_zoom_vel = 1 / self._ZOOM_SPEED

    def req_zoom_stop(self):
        self._req_zoom_vel = 1.0

    def req_move(self, pos):
        self._req_vel = pos - self._pos

    # ==== APPLY MOVEMENTS ====

    def set_transforms(self, pos: WVec, vel: WVec = WVec()):
        self._pos = WVec(pos)
        self._req_pos = WVec(self._pos)

        self._vel = WVec(vel)
        self._req_vel = WVec(self._vel)

    def move(self, threshold=0.001):
        self._vel += (self._req_vel - self._vel) * self._VEL_DAMPING_FACTOR
        self._pos += self._vel * self._POS_DAMPING_FACTOR ** (1 / (1 + abs(self._vel)))
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
