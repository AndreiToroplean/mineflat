import os

import pygame as pg
from core.constants import BLOCK_PIX_SIZE, TEXTURES_PATH


class Block:
    _BLOCK_DIR = "block"

    _special_file_names = {"grass" : "grass_block_side"}

    def __init__(self, material):
        self.material = material
        self._pix_size = (BLOCK_PIX_SIZE,) * 2
        self.surf = None
        self._draw()

    def _draw(self):
        if (name := self.material.name) in self._special_file_names:
            file_name = self._special_file_names[name]
        else:
            file_name = name
        file_path = os.path.join(TEXTURES_PATH, self._BLOCK_DIR, f"{file_name}.png")
        self.surf = pg.transform.scale(pg.image.load(file_path), self._pix_size)

    def __repr__(self):
        return f"Block({self.material})"
