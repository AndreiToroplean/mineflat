from core import ChunkVec, WorldVec, PixVec
from global_params import CHUNK_SIZE, BLOCK_PIX_SIZE


def world_to_chunk_pos(world_pos):
    return ChunkVec(*(int(coord // chunk_size_dim) for coord, chunk_size_dim in zip(world_pos, CHUNK_SIZE)))


def chunk_to_world_pos(chunk_pos):
    return WorldVec(*(coord * chunk_size_dim for coord, chunk_size_dim in zip(chunk_pos, CHUNK_SIZE)))


def world_to_pix_shift(world_shift, surface_res, world_shift_inc):
    return PixVec(*(
        world_shift[0] * BLOCK_PIX_SIZE,
        surface_res[1] - (world_shift[1] * BLOCK_PIX_SIZE + world_shift_inc[1]),
        ))
