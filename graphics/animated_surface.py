import os
from enum import Enum
from math import floor

import pygame as pg

from core.classes import PixVec, WVec
from core.constants import C_KEY, CAM_FPS, LIGHT_MAX_LEVEL, PIX_ORIGIN
from core.funcs import light_level_to_color_int


class AnimAction(Enum):
    reset = -1
    pause = 0
    play = 1
    end = 2


class AnimatedSurface:
    def __init__(self, dir_path, w_height, neutrals=(), frame_rate=30):
        self.neutrals = neutrals

        self._images = []
        self._images_flipped = []
        images_path = os.path.join(dir_path, "images")
        masks_path = os.path.join(dir_path, "masks")
        for image_file, mask_file in zip(sorted(os.scandir(images_path), key=lambda x: x.name), sorted(os.scandir(masks_path), key=lambda x: x.name)):
            image = pg.image.load(image_file.path).convert()
            mask = pg.image.load(mask_file.path).convert()
            self._images.append((image, mask))
            self._images_flipped.append((pg.transform.flip(image, True, False), pg.transform.flip(mask, True, False)))

        self.pix_size = PixVec(*self._images[0][0].get_size())
        pix_to_w_factor = w_height / self.pix_size.y
        self.w_size = WVec(x=self.pix_size.x * pix_to_w_factor, y=w_height)

        self.action = AnimAction.pause
        self._frame = 0
        self._frame_rate = frame_rate
        self.is_flipped = False

        self.surf = pg.Surface(self.pix_size)
        self._light_surf = pg.Surface(self.pix_size)

    def _tick(self):
        if self.action == AnimAction.pause:
            return
        if self.action == AnimAction.reset:
            self._frame = 0
            return
        if self.action == AnimAction.play or (self.action == AnimAction.end and self.rtn_frame not in self.neutrals):
            self._frame = (self._frame + self._frame_rate / CAM_FPS) % len(self._images)

        if self.action == AnimAction.end and self._frame in self.neutrals:
            self.action = AnimAction.pause

    def draw_and_tick(self, sky_light=LIGHT_MAX_LEVEL):
        if not self.is_flipped:
            surf_frame, surf_frame_mask = self._images[self.rtn_frame]
        else:
            surf_frame, surf_frame_mask = self._images_flipped[self.rtn_frame]

        sky_light_value = light_level_to_color_int(sky_light)
        self._light_surf.fill(self._light_surf.map_rgb((sky_light_value, sky_light_value, sky_light_value)))
        self.surf.blit(surf_frame, PIX_ORIGIN)
        self.surf.blit(self._light_surf, PIX_ORIGIN, special_flags=pg.BLEND_MULT)
        self.surf.blit(surf_frame_mask, PIX_ORIGIN, special_flags=pg.BLEND_ADD)

        self._tick()

    def sync(self, other):
        self._frame = len(self._images) * other._frame / len(other._images)

    @property
    def rtn_frame(self):
        return floor(self._frame)
