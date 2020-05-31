import os

import pygame as pg

from core.classes import PixVec, SVec, WVec, WBounds, WDimBounds

# ==== TECHNICAL DIMENSIONS ====
PLAYER_S_POS = SVec(0.5, 0.333)
BLOCK_PIX_SIZE = 16  # Should stay equal to block texture size resolution. That is, 16.
CHUNK_W_SIZE = WVec(8, 8)
CHUNK_PIX_SIZE = PixVec(*[BLOCK_PIX_SIZE * chunk_size_dim for chunk_size_dim in CHUNK_W_SIZE])
WORLD_HEIGHT_BOUNDS = (0, 2**8)
BLOCK_BOUND_SHIFTS = WBounds(WDimBounds(0, 1), WDimBounds(0, 1))

# ==== COLORS ====
C_KEY = pg.Color(255, 0, 0)

C_SKY = pg.Color(120, 190, 225)

# ==== CAM ====
CAM_FPS = 30
CAM_DEFAULT_SCALE = 64.0
CAM_SCALE_BOUNDS = (32.0, 128.0)

# ==== PLAYER PARAMS ====
PLAYER_DEFAULT_SPAWN_POS = (0.5, WORLD_HEIGHT_BOUNDS[1])
PLAYER_POS_DAMPING_FACTOR = 0.5
PLAYER_POS_MIN_HEIGHT = WORLD_HEIGHT_BOUNDS[0] - 50

# ==== CURSOR ====
CURSOR = (16, 16), (8, 8), *pg.cursors.compile((
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
    ))

# ==== GAME PARAMS ====
FULLSCREEN = True
DEBUG = True

# ==== PATHS ====
CWD = os.getcwd()
SAVES_DIR = "saves"
CURRENT_SAVE_DIR = "save_002"
CURRENT_SAVE_PATH = os.path.join(CWD, SAVES_DIR, CURRENT_SAVE_DIR)
RESOURCES_PATH = os.path.join(CWD, "resources")
TEXTURES_PATH = os.path.join(RESOURCES_PATH, "textures")
GUI_PATH = os.path.join(RESOURCES_PATH, "gui")

# ==== GAME DYNAMICS ====
GRAVITY = (0.0, -22 / (CAM_FPS ** 2))
ACTION_COOLDOWN_DELAY = 0.2 * CAM_FPS

# ==== UTILITIES ====
DIR_TO_ANGLE = {
    WVec(1, 0): 0,
    WVec(0, 1): 90,
    WVec(-1, 0): 180,
    WVec(0, -1): 270,
    }
