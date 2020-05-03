from core import ChunkVec, WorldVec, PixVec
from global_params import CHUNK_SIZE, BLOCK_PIX_SIZE


def world_to_chunk_pos(world_pos):
    rtn = [int(coord // chunk_size_dim) for coord, chunk_size_dim in zip(world_pos, CHUNK_SIZE)]
    return ChunkVec(*rtn)


def chunk_to_world_pos(chunk_pos):
    rtn = [coord * chunk_size_dim for coord, chunk_size_dim in zip(chunk_pos, CHUNK_SIZE)]
    return WorldVec(*rtn)


def world_to_pix_shift(world_shift, surface_res):
    rtn = [
        world_shift[0] * BLOCK_PIX_SIZE,
        surface_res - ((1+world_shift[1]) * BLOCK_PIX_SIZE),
        ]
    return PixVec(*rtn)
