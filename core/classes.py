from typing import NamedTuple
from enum import Enum

from core.vec import Vec


class WVec(Vec): pass


class CVec(Vec): pass


class PixVec(Vec): pass


class WBounds(NamedTuple):
    min: WVec = WVec()
    max: WVec = WVec()


class CBounds(NamedTuple):
    min: CVec = CVec()
    max: CVec = CVec()


class BlockSelection(NamedTuple):
    block_w_pos: WVec or None
    space_w_pos_shift: WVec or None
    space_only: bool = False


class Result(Enum):
    success = 0
    failure = -1


class LoadResult(Enum):
    success = 0
    no_file = -1
    incompatible = -2


class DirMeta(type):
    def __iter__(self):
        return iter((self.right, self.up, self.left, self.down))


class Dir(metaclass=DirMeta):
    right = WVec(1, 0)
    up = WVec(0, 1)
    left = WVec(-1, 0)
    down = WVec(0, -1)


class Colliders:
    def __init__(self):
        self.left = []
        self.right = []
        self.down = []
        self.up = []

    def __repr__(self):
        return f"left: {self.left}, \nright: {self.right}, \ndown: {self.down}, \nup: {self.up}"

    def __iter__(self):
        return iter((self.left, self.right, self.down, self.up))
