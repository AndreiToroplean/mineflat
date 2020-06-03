from math import floor

from core.classes import CVec, WVec, PixVec, WBounds
from core.constants import CHUNK_W_SIZE, BLOCK_PIX_SIZE


def w_to_c_vec(w_vec: WVec):
    return floor(w_vec // CHUNK_W_SIZE)


def c_to_w_vec(c_vec: CVec):
    return c_vec * CHUNK_W_SIZE


def w_to_c_to_w_vec(w_vec: WVec):
    return floor(w_vec // CHUNK_W_SIZE) * CHUNK_W_SIZE


def w_to_pix_shift(w_shift, source_surf_pix_size, dest_surf_pix_size, source_pivot=(0, 0), dest_pivot=(0, 0), *, scale=BLOCK_PIX_SIZE):
    return PixVec(
        w_shift[0] * scale - source_pivot[0] + dest_pivot[0],
        dest_surf_pix_size[1] - w_shift[1] * scale - source_surf_pix_size[1] + source_pivot[1] - dest_pivot[1],
        )


def pix_to_w_shift(pix_shift, source_surf_pix_size, dest_surf_pix_size, source_pivot=(0, 0), dest_pivot=(0, 0), *, scale=BLOCK_PIX_SIZE):
    return WVec(
        (pix_shift[0] + source_pivot[0] - dest_pivot[0]) / scale,
        (-pix_shift[1] + dest_surf_pix_size[1] - source_surf_pix_size[1] + source_pivot[1] - dest_pivot[1]) / scale,
        )


def get_bounds(w_pos: WVec, bounds_w_shift: WBounds) -> WBounds:
    return WBounds(min=floor(w_pos + bounds_w_shift.min), max=floor(w_pos + bounds_w_shift.max))
