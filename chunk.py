from global_params import CHUNK_SIZE
from core import WorldVec, ChunkVec, ChunkData, Colliders
from block import Block


class Chunk:
    def __init__(self, chunk_pos):
        self.chunk_pos = chunk_pos
        self.world_pos = self.chunk_to_world_pos(self.chunk_pos)
        self.blocks = self.generate()
        self.surface = None
        self.colliders = None
        self.update_data()

    @staticmethod
    def chunk_to_world_pos(chunk_pos):
        rtn = [coord * chunk_dim_size for coord, chunk_dim_size in zip(chunk_pos, CHUNK_SIZE)]
        return WorldVec(*rtn)

    def generate(self):

        return blocks

    def update_data(self):
        pass

    def update(self):
        pass

    def get_data(self):
        return self.data
