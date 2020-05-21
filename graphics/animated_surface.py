import os
from enum import Enum
from math import floor

import pygame as pg

from core.classes import PixVec, WVec
from core.constants import C_KEY, CAM_FPS


class AnimAction(Enum):
    reset = -1
    pause = 0
    play = 1
    end = 2


class AnimatedSurface:
    def __init__(self, dir_path, w_height, neutrals=(), frame_rate=30):
        self.neutrals = neutrals

        self.images = []
        self.images_reversed = []
        for file in sorted(os.scandir(dir_path), key=lambda x: x.name):
            image = pg.image.load(file.path)
            image.set_colorkey(C_KEY)
            self.images.append(image)
            self.images_reversed.append(pg.transform.flip(image, True, False))

        self.pix_size = PixVec(*self.images[0].get_size())
        pix_to_w_factor = w_height / self.pix_size.y
        self.w_size = WVec(x=self.pix_size.x * pix_to_w_factor, y=w_height)

        self.action = AnimAction.pause
        self.frame = 0
        self.frame_rate = frame_rate
        self.is_reversed = False

    def _tick(self):
        if self.action == AnimAction.pause:
            return
        if self.action == AnimAction.reset:
            self.frame = 0
            return
        if self.action == AnimAction.play or (self.action == AnimAction.end and self.rtn_frame not in self.neutrals):
            self.frame = (self.frame + self.frame_rate/CAM_FPS) % len(self.images)

        if self.action == AnimAction.end and self.frame in self.neutrals:
            self.action = AnimAction.pause

    def get_surf_and_tick(self):
        if not self.is_reversed:
            rtn = self.images[self.rtn_frame]
        else:
            rtn = self.images_reversed[self.rtn_frame]
        self._tick()
        return rtn

    def sync(self, other):
        self.frame = len(self.images) * other.frame/len(other.images)

    @property
    def rtn_frame(self):
        return floor(self.frame)
