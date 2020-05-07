from enum import Enum

import pygame as pg
from global_params import BLOCK_PIX_SIZE


class Material(Enum):
    stone = "1"
    grass = "2"
    dirt = "3"


class Block:
    special_file_names = {"grass" : "grass_block_side"}

    def __init__(self, material):
        self.material = material
        self.surf = None
        self.draw()

    def draw(self):
        size = (BLOCK_PIX_SIZE,) * 2
        if (name := self.material.name) in self.special_file_names:
            file_name = self.special_file_names[name]
        else:
            file_name = name
        file_path = f"resources/textures/block/{file_name}.png"
        self.surf = pg.image.load(file_path)


if __name__ == "__main__":
    from debug.display import Display

    Display(Block(Material.dirt).surf)
    Display(Block(Material.grass).surf)
