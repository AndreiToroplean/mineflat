from math import floor

from core.classes import CVec, WVec, PixVec, WBounds
from core.constants import CHUNK_W_SIZE, BLOCK_PIX_SIZE, LIGHT_MAX_LEVEL


def w_to_c_vec(w_vec: WVec):
    return floor(w_vec // CHUNK_W_SIZE)


def c_to_w_vec(c_vec: CVec):
    return c_vec * CHUNK_W_SIZE


def w_to_c_to_w_vec(w_vec: WVec):
    return floor(w_vec // CHUNK_W_SIZE) * CHUNK_W_SIZE


def w_to_pix_shift(w_shift: WVec, source_surf_pix_size: PixVec, dest_surf_pix_size: PixVec, source_pivot: PixVec = PixVec(), dest_pivot: PixVec = PixVec(), *, scale=BLOCK_PIX_SIZE.x):
    return PixVec(
        w_shift.x * scale - source_pivot.x + dest_pivot.x,
        dest_surf_pix_size.y - w_shift.y * scale - source_surf_pix_size.y + source_pivot.y - dest_pivot.y,
        )


def pix_to_w_shift(pix_shift: PixVec, source_surf_pix_size: PixVec, dest_surf_pix_size: PixVec, source_pivot: PixVec = PixVec(), dest_pivot: PixVec = PixVec(), *, scale=BLOCK_PIX_SIZE.x):
    return WVec(
        (pix_shift.x + source_pivot.x - dest_pivot.x) / scale,
        (-pix_shift.y + dest_surf_pix_size.y - source_surf_pix_size.y + source_pivot.y - dest_pivot.y) / scale,
        )


def get_bounds(w_pos: WVec, bounds_w_shift: WBounds) -> WBounds:
    return WBounds(min=floor(w_pos + bounds_w_shift.min), max=floor(w_pos + bounds_w_shift.max))


def color_float_to_int(color_float):
    return min(floor(color_float * 256), 255)


def light_level_to_color_int(light_level):
    return color_float_to_int(light_level / LIGHT_MAX_LEVEL)
