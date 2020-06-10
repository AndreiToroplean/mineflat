import os

import pygame as pg

from core.classes import PixVec
from core.constants import TEXTURES_PATH, PIX_ORIGIN, HOTBAR_ORIG_PIX_SIZE, HOTBAR_PIX_SIZE, BLOCK_PIX_SIZE, C_KEY
from item.block import BlockType, Block


class Hotbar:
    def __init__(self):
        self._items = [
            Block(BlockType.dirt),
            Block(BlockType.grass),
            Block(BlockType.stone),
            Block(BlockType.cobblestone),
            Block(BlockType.gravel),
            Block(BlockType.sand),
            Block(BlockType.sandstone),
            Block(BlockType.oak_log),
            Block(BlockType.oak_planks),
            ]

        self._selected_index = 0

        widget_surf = pg.image.load(os.path.join(TEXTURES_PATH, "gui", "widgets.png"))

        self._orig_pix_size = HOTBAR_ORIG_PIX_SIZE
        self._empty_surf = pg.Surface(self._orig_pix_size, flags=pg.SRCALPHA)
        self._empty_surf.blit(widget_surf, PIX_ORIGIN+1, (PIX_ORIGIN, self._orig_pix_size - 2))
        self._filled_surf = self._empty_surf.copy()
        self._selected_filled_surf = self._filled_surf.copy()

        self._pix_size = HOTBAR_PIX_SIZE
        self._surf = pg.Surface(self._pix_size, flags=pg.SRCALPHA)

        self._item_selector_pix_size = PixVec(24, 24)
        self._item_selector_surf = pg.Surface(self._item_selector_pix_size, flags=pg.SRCALPHA)
        self._item_selector_surf.blit(widget_surf, -PixVec(0, 22))

        self._draw_filled_surf()
        self._draw_surf()

    @property
    def selected_item(self):
        return self._items[self._selected_index]

    def req_select_index(self, index):
        self._selected_index = index
        self._draw_surf()

    @staticmethod
    def _index_to_pix_shift(index):
        return PixVec(index * (4 + BLOCK_PIX_SIZE.x), 0)

    def _draw_filled_surf(self):
        blit_sequence = []
        for index, item in enumerate(self._items):
            pix_shift = self._index_to_pix_shift(index) + 4
            blit_sequence.append((item.surf, pix_shift))

        self._filled_surf = self._empty_surf.copy()
        self._filled_surf.blits(blit_sequence, doreturn=False)

    def _draw_surf(self):
        selector_pix_shift = self._index_to_pix_shift(self._selected_index)
        self._selected_filled_surf = self._filled_surf.copy()
        self._selected_filled_surf.blit(self._item_selector_surf, selector_pix_shift)
        self._surf = pg.transform.scale(self._selected_filled_surf, self._pix_size, self._surf)

    def draw(self, camera):
        camera.draw_hotbar(self._surf, self._pix_size/2)
