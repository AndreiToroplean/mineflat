from core import PixVec, ScreenVec, WorldVec, Color

# Technical dimensions
PLAYER_SCREEN_POS = ScreenVec(0.5, 0.5)
BLOCK_PIX_SIZE = 16
test = 15
CHUNK_SIZE = WorldVec(test, test)
CHUNK_PIX_SIZE = PixVec(*[BLOCK_PIX_SIZE * chunk_size_dim for chunk_size_dim in CHUNK_SIZE])

# Artistic dimensions
WORLD_MAX_HEIGHT = 2 ** 8
WATER_HEIGHT = 2 ** 6

# Colors
C_KEY = Color(255, 0, 0)
C_SKY = Color(100, 200, 230)

FPS = 30