import pygame as pg

from core import Material
from global_params import BLOCK_PIX_SIZE


class Block:
    special_file_names = {"grass" : "grass_block_side"}

    def __init__(self, material):
        self.material = material
        self.surface = None
        self.draw()

    def draw(self):
        size = (BLOCK_PIX_SIZE,) * 2
        if (name := self.material.name) in self.special_file_names:
            file_name = self.special_file_names[name]
        else:
            file_name = name
        file_path = f"res/textures/block/{file_name}.png"
        texture = pg.image.load(file_path)
        self.surface = pg.transform.scale(texture, size)


if __name__ == "__main__":
    from debug.display import Display

    Display(Block(Material.dirt).surface)
    Display(Block(Material.grass).surface)
