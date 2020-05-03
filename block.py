import pygame as pg

from core import Material
from global_params import BLOCK_PIX_SIZE


class Block:
    def __init__(self, material):
        self.material = material
        self.surface = None
        self.draw()

    def draw(self):
        size = (BLOCK_PIX_SIZE,) * 2
        file_path = f"res/textures/block/{self.material.name}.png"
        texture = pg.image.load(file_path)
        self.surface = pg.transform.scale(texture, size)
