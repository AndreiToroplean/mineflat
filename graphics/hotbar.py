import os

import pygame as pg

from core.constants import TEXTURES_PATH, PIX_ORIGIN, HOTBAR_ORIG_PIX_SIZE, HOTBAR_PIX_SIZE
from item.block import BlockType


class Hotbar:
    def __init__(self):
        self._items = [
            BlockType.dirt,
            BlockType.grass,
            BlockType.stone,
            BlockType.cobblestone,
            BlockType.gravel,
            BlockType.sand,
            BlockType.oak_log,
            BlockType.oak_leaves,
            BlockType.oak_planks,
            ]
        self._selected_index = 0

        widget_surf = pg.image.load(os.path.join(TEXTURES_PATH, "gui", "widgets.png"))

        self._empty_surf = pg.Surface(HOTBAR_ORIG_PIX_SIZE, flags=pg.SRCALPHA)
        self._empty_surf.blit(widget_surf, PIX_ORIGIN)
        self._pix_size = HOTBAR_PIX_SIZE
        self._empty_surf = pg.transform.scale(self._empty_surf, self._pix_size)
        self._surf = self._empty_surf.copy()

        self._update_surf()

    @property
    def selected_item(self):
        return self._items[self._selected_index]

    def req_select_prev(self):
        self._selected_index -= 1

    def req_select_next(self):
        self._selected_index += 1

    def req_select_index(self, index):
        self._selected_index = index

    def _update_surf(self):
        ...

    def draw(self, camera):
        camera.draw_hotbar(self._surf, self._pix_size/2)
