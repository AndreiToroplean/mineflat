from core import ChunkVec, WorldVec, PixVec
from global_params import CHUNK_SIZE, BLOCK_PIX_SIZE


def world_to_chunk_vec(world_vec):
    return ChunkVec(*(int(coord // chunk_size_dim) for coord, chunk_size_dim in zip(world_vec, CHUNK_SIZE)))


def chunk_to_world_vec(chunk_vec):
    return WorldVec(*(coord * chunk_size_dim for coord, chunk_size_dim in zip(chunk_vec, CHUNK_SIZE)))


def world_to_pix_shift(world_shift, dest_surf_pix_size, source_surf_pix_size):
    return PixVec(
        world_shift[0] * BLOCK_PIX_SIZE,
        dest_surf_pix_size[1] - (world_shift[1] * BLOCK_PIX_SIZE + source_surf_pix_size[1]),
        # world_shift[1] * BLOCK_PIX_SIZE,
        )
