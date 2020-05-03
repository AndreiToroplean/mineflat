from collections import namedtuple
from enum import Enum

Color = namedtuple("Color", ("r", "g", "b"))


PixVec = namedtuple("PixVec", ("x", "y"))
ScreenVec = namedtuple("ScreenVec", ("x", "y"))
WorldVec = namedtuple("WorldVec", ("x", "y"))
ChunkVec = namedtuple("ChunkVec", ("x", "y"))

WorldViewRect = namedtuple("WorldViewRect", ("pos_0", "pos_1"))
ChunkViewRect = namedtuple("ChunkViewRect", ("pos_0", "pos_1"))

ChunkData = namedtuple("ChunkData", ("surface", "colliders"))
Colliders = namedtuple("Colliders", ("left", "right", "top", "bottom"))


class Material(Enum):
    air = "0"
    dirt = "3"
