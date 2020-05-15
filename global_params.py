from core import PixVec, ScreenVec, WorldVec, Color

# Game params
FULLSCREEN = True

# Technical dimensions
PLAYER_SCREEN_POS = ScreenVec(0.5, 0.333)
BLOCK_PIX_SIZE = 16
CHUNK_SIZE = WorldVec(8, 8)
CHUNK_PIX_SIZE = PixVec(*[BLOCK_PIX_SIZE * chunk_size_dim for chunk_size_dim in CHUNK_SIZE])

# Artistic dimensions
WORLD_MAX_HEIGHT = 2 ** 8
WATER_HEIGHT = 2 ** 6

# Colors
C_KEY = Color(255, 0, 0)

C_SKY = Color(120, 190, 225)

# Cam dynamics
CAM_FPS = 30
CAM_ZOOM_SPEED = 1.05
CAM_POS_DAMPING_FACTOR = 0.25
CAM_ZOOM_DAMPING_FACTOR = 0.15
CAM_SCALE_BOUNDS = (32, 128)

# Player dynamics
PLAYER_DAMPING_FACTOR = 0.5

# Cursor
CURSOR = (
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "XXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXX",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
    "       XX       ",
)