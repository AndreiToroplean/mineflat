from collections import namedtuple

Color = namedtuple("Color", ("r", "g", "b"))

PixVec = namedtuple("PixVec", ("x", "y"))
ScreenVec = namedtuple("ScreenVec", ("x", "y"))
WorldVec = namedtuple("WorldVec", ("x", "y"))
ChunkVec = namedtuple("ChunkVec", ("x", "y"))

WorldView = namedtuple("WorldView", ("pos_0", "pos_1"))
ChunkView = namedtuple("ChunkView", ("pos_0", "pos_1"))

ChunkData = namedtuple("ChunkData", ("surf", "colliders"))


def get_empty_colliders():
    left = []
    right = []
    bottom = []
    top = []
    return {
        (+1, 0): left,
        (+1, +1): left,
        (+1, -1): left,

        (-1, 0): right,
        (-1, +1): right,
        (-1, -1): right,

        (0, +1): bottom,
        (+1, +1): bottom,
        (-1, +1): bottom,

        (0, -1): top,
        (+1, -1): top,
        (-1, -1): top,
        }


COLLIDERS_DIRS = ((+1, 0), (-1, 0), (0, +1), (0, -1),)

# class Colliders:
#     def __init__(self):
#         self.left = []
#         self.right = []
#         self.bottom = []
#         self.top = []
