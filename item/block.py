import os
from enum import Enum

import pygame as pg
from core.constants import BLOCK_PIX_SIZE, TEXTURES_PATH


class BlockType(Enum):
    air = "0"
    stone = "1"
    grass = "2"
    dirt = "3"
    cobblestone = "4"
    oak_planks = "5"
    sand = "12"
    gravel = "13"
    oak_log = "17"
    oak_leaves = "18"

    bedrock = "7"


class Block:
    _BLOCK_DIR = "block"

    _special_file_names = {"grass": "grass_block_side"}

    _blocks = {}

    def __new__(cls, block_type, *args, **kwargs):
        try:
            return cls._blocks[block_type]
        except KeyError:
            pass

        new_block = super(Block, cls).__new__(cls, *args, **kwargs)
        cls._blocks[block_type] = new_block
        return new_block

    def __init__(self, block_type):
        self.block_type = block_type
        self._pix_size = BLOCK_PIX_SIZE
        self.surf = pg.Surface(self._pix_size)
        self._draw()

    def _draw(self):
        if (name := self.block_type.name) in self._special_file_names:
            file_name = self._special_file_names[name]
        else:
            file_name = name
        file_path = os.path.join(TEXTURES_PATH, self._BLOCK_DIR, f"{file_name}.png")
        self.surf = pg.transform.scale(pg.image.load(file_path).convert(), self._pix_size, self.surf)

    def __repr__(self):
        return f"{type(self).__name__}({self.block_type})"
