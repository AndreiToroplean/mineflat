from collections import namedtuple
from enum import Enum


Color = namedtuple("Color", ("r", "g", "b"))

PixVec = namedtuple("PixVec", ("x", "y"))
ScreenVec = namedtuple("ScreenVec", ("x", "y"))
WorldVec = namedtuple("WorldVec", ("x", "y"))
ChunkVec = namedtuple("ChunkVec", ("x", "y"))

WorldView = namedtuple("WorldView", ("pos_0", "pos_1"))
ChunkView = namedtuple("ChunkView", ("pos_0", "pos_1"))

ChunkData = namedtuple("ChunkData", ("surf", "colliders"))
Colliders = namedtuple("Colliders", ("left", "right", "top", "bottom"))


class Material(Enum):
    stone = "1"
    grass = "2"
    dirt = "3"
