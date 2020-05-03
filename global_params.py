from core import PixVec, ScreenVec, WorldVec, Color

# Technical dimensions
PLAYER_SCREEN_POS = ScreenVec(0.5, 0.33)
BLOCK_PIX_SIZE = 50
CHUNK_SIZE = WorldVec(9, 9)
CHUNK_PIX_SIZE = PixVec(*[BLOCK_PIX_SIZE * chunk_size_dim for chunk_size_dim in CHUNK_SIZE])
CHUNK_PADDING = 1

# Artistic dimensions
WORLD_MAX_HEIGHT = 2 ** 8
WATER_HEIGHT = 2 ** 6

# Colors
C_KEY = Color(255, 0, 0)
C_SKY = Color(80, 220, 240)

