from collections import namedtuple


PixVec = namedtuple("PixVec", ("x", "y"))
ScreenVec = namedtuple("ScreenVec", ("x", "y"))
WorldVec = namedtuple("WorldVec", ("x", "y"))
ChunkVec = namedtuple("ChunkVec", ("x", "y"))

WorldView = namedtuple("WorldView", ("pos_0", "pos_1"))
ChunkView = namedtuple("ChunkView", ("pos_0", "pos_1"))

ChunkData = namedtuple("ChunkData", ("surf", "colliders"))


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
