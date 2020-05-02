from collections import namedtuple

Color = namedtuple("Color", ("r", "g", "b"))

WorldPos = namedtuple("WorldPos", ("x", "y"))
ChunkPos = namedtuple("ChunkPos", ("x", "y"))

WorldViewRect = namedtuple("WorldViewRect", ("pos_0", "pos_1"))
ChunkViewRect = namedtuple("ChunkViewRect", ("pos_0", "pos_1"))

ChunkData = namedtuple("ChunkData", ("surface", "colliders"))
Colliders = namedtuple("Colliders", ("left", "right", "top", "bottom"))
