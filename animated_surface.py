import os
from enum import Enum

import pygame as pg

from core import PixVec, WorldVec
from global_params import C_KEY


class AnimAction(Enum):
    reset = -1
    pause = 0
    play = 1
    end = 2


class AnimatedSurface:
    def __init__(self, dir_path, world_height):
        self.images = []
        self.images_reversed = []
        for file in sorted(os.scandir(dir_path), key=lambda x: x.name):
            image = pg.image.load(file.path)
            image.set_colorkey(C_KEY)
            self.images.append(image)
            self.images_reversed.append(pg.transform.flip(image, True, False))

        self.pix_size = PixVec(*self.images[0].get_size())
        pix_to_world_factor = world_height / self.pix_size.y
        self.world_size = WorldVec(x=self.pix_size.x * pix_to_world_factor, y=world_height)

        self.action = AnimAction.pause
        self.frame = 0
        self.is_reversed = False

    def get_surf(self):
        if not self.is_reversed:
            rtn = self.images[self.frame]
        else:
            rtn = self.images_reversed[self.frame]
        self.advance_time()
        return rtn

    def advance_time(self):
        if self.action == AnimAction.pause:
            pass
        elif self.action == AnimAction.reset:
            self.frame = 0
        elif self.action == AnimAction.play or (self.action == AnimAction.end and self.frame != 0):
            self.frame = (self.frame + 1) % len(self.images)

        if self.action == AnimAction.end and self.frame == 0:
            self.action = AnimAction.pause
