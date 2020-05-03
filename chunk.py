import pygame as pg

from core_funcs import chunk_to_world_pos, world_to_pix_shift
from global_params import BLOCK_PIX_SIZE, CHUNK_SIZE, WATER_HEIGHT
from core import PixVec, ChunkVec, WorldVec, ChunkData, Colliders, Material
from block import Block


class Chunk:
    block_materials = {}

    def __init__(self, world_pos):
        self.world_pos = world_pos
        self.blocks = self.generate_blocks()
        self.surface = pg.Surface((
                BLOCK_PIX_SIZE * CHUNK_SIZE[0],
                BLOCK_PIX_SIZE * CHUNK_SIZE[1],
            ))
        self.colliders = None
        self.draw()


    def generate_blocks(self):
        blocks = {}
        for world_shift_x in range(CHUNK_SIZE[0]):
            for world_shift_y in range(CHUNK_SIZE[1]):
                block_world_pos = WorldVec(self.world_pos.x+world_shift_x, self.world_pos.y+world_shift_y)
                if block_world_pos.y < WATER_HEIGHT:
                    try:
                        block = self.block_materials[Material.dirt]
                    except KeyError:
                        block = Block(Material.dirt)
                        self.block_materials[Material.dirt] = block

                    blocks[WorldVec(world_shift_x, world_shift_y)] = block
        return blocks

    def draw(self):
        blit_sequence = [(
            block.surface,
            world_to_pix_shift(world_shift, self.surface.get_size())
            ) for world_shift, block in self.blocks.items()]
        self.surface.blits(blit_sequence, doreturn=False)

    @property
    def data(self):
        return ChunkData(
            surface=self.surface,
            colliders=self.colliders,
            )
