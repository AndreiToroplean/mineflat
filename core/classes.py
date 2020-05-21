from collections import namedtuple
from enum import Enum

PixVec = namedtuple("PixVec", ("x", "y"))
SVec = namedtuple("SVec", ("x", "y"))
WVec = namedtuple("WVec", ("x", "y"))
CVec = namedtuple("CVec", ("x", "y"))

WView = namedtuple("WView", ("pos_0", "pos_1"))
CView = namedtuple("CView", ("pos_0", "pos_1"))

WDimBounds = namedtuple("WDimBounds", ("min", "max"))
WBounds = namedtuple("WBounds", ("x", "y"))


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
