import pygame as pg
from core.constants import BLOCK_PIX_SIZE


class Block:
    special_file_names = {"grass" : "grass_block_side"}

    def __init__(self, material):
        self.material = material
        self._pix_size = (BLOCK_PIX_SIZE,) * 2
        self.surf = None
        self._draw()

    def _draw(self):
        if (name := self.material.name) in self.special_file_names:
            file_name = self.special_file_names[name]
        else:
            file_name = name
        file_path = f"resources/textures/block/{file_name}.png"
        self.surf = pg.transform.scale(pg.image.load(file_path), self._pix_size)

    def __repr__(self):
        return f"Block({self.material})"
