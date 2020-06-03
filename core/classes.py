from collections import namedtuple
from enum import Enum

from core.vec import Vec


class WVec(Vec): pass
class CVec(Vec): pass
class SVec(Vec): pass
class PixVec(Vec): pass


WView = namedtuple("WView", ("pos_0", "pos_1"))
CView = namedtuple("CView", ("pos_0", "pos_1"))

WBounds = namedtuple("WBounds", ("min", "max"))

BlockSelection = namedtuple("BlockSelection", ("block_w_pos", "space_w_pos_shift", "space_only"))


class Result(Enum):
    success = 0
    failure = -1


class Colliders:
    def __init__(self):
        self.left = []
        self.right = []
        self.bottom = []
        self.top = []

    def __repr__(self):
        return f"left: {self.left}, \nright: {self.right}, \nbottom: {self.bottom}, \ntop: {self.top}"

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        try:
            rtn = (self.left, self.right, self.bottom, self.top)[self.i]
        except IndexError:
            raise StopIteration
        else:
            self.i += 1
            return rtn
