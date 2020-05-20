from core.classes import ChunkVec, WorldVec, PixVec
from core.constants import CHUNK_SIZE, BLOCK_PIX_SIZE


def w_to_chunk_vec(w_vec):
    return ChunkVec(*(int(dim // chunk_size_dim) for dim, chunk_size_dim in zip(w_vec, CHUNK_SIZE)))


def chunk_to_w_vec(chunk_vec):
    return WorldVec(*(dim * chunk_size_dim for dim, chunk_size_dim in zip(chunk_vec, CHUNK_SIZE)))


def w_to_chunk_to_w_vec(w_vec):
    return WorldVec(*(int(dim//chunk_size_dim) * chunk_size_dim for dim, chunk_size_dim in zip(w_vec, CHUNK_SIZE)))


def w_to_pix_shift(w_shift, source_surf_pix_size, dest_surf_pix_size, source_pivot=(0, 0), dest_pivot=(0, 0), *, scale=BLOCK_PIX_SIZE):
    return PixVec(
        w_shift[0] * scale - source_pivot[0] + dest_pivot[0],
        dest_surf_pix_size[1] - w_shift[1] * scale - source_surf_pix_size[1] + source_pivot[1] - dest_pivot[1],
        )


def pix_to_w_shift(pix_shift, source_surf_pix_size, dest_surf_pix_size, source_pivot=(0, 0), dest_pivot=(0, 0), *, scale=BLOCK_PIX_SIZE):
    return WorldVec(
        (pix_shift[0] + source_pivot[0] - dest_pivot[0]) / scale,
        (-pix_shift[1] + dest_surf_pix_size[1] - source_surf_pix_size[1] + source_pivot[1] - dest_pivot[1]) / scale,
        )
