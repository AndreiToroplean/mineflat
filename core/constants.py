import os

import pygame as pg

from core.classes import PixVec, SVec, WVec, WBounds, Dir

# ==== TECHNICAL DIMENSIONS ====
PLAYER_S_POS = SVec(0.5, 0.333)
BLOCK_PIX_SIZE = 16  # Should stay equal to block texture size resolution. That is, 16.
CHUNK_W_SIZE = WVec(8, 8)
CHUNK_PIX_SIZE = PixVec(CHUNK_W_SIZE * BLOCK_PIX_SIZE)
WORLD_HEIGHT_BOUNDS = WVec(0, 2**8)
BLOCK_BOUND_SHIFTS = WBounds(WVec(0, 0), WVec(1, 1))

# ==== COLORS ====
C_KEY = pg.Color(255, 0, 0)

C_SKY = pg.Color(120, 190, 225)

# ==== CAM ====
CAM_FPS = 60
CAM_DEFAULT_SCALE = 64.0
CAM_SCALE_BOUNDS = (32.0, 128.0)

# ==== PLAYER PARAMS ====
PLAYER_DEFAULT_SPAWN_POS = WVec(0.5, WORLD_HEIGHT_BOUNDS.y)
PLAYER_POS_DAMPING_FACTOR = 0.5
PLAYER_POS_MIN_HEIGHT = WORLD_HEIGHT_BOUNDS.x - 50

# ==== GAME PARAMS ====
FULLSCREEN = True
DEBUG = True
SAVE = True
LOAD = True

# ==== PATHS ====
CWD = os.getcwd()
SAVES_DIR = "saves"
CURRENT_SAVE_DIR = "save_002"
CURRENT_SAVE_PATH = os.path.join(CWD, SAVES_DIR, CURRENT_SAVE_DIR)
RESOURCES_PATH = os.path.join(CWD, "resources")
TEXTURES_PATH = os.path.join(RESOURCES_PATH, "textures")
GUI_PATH = os.path.join(RESOURCES_PATH, "gui")

# ==== GAME DYNAMICS ====
GRAVITY = WVec(0.0, -22 / (CAM_FPS ** 2))
ACTION_COOLDOWN_DELAY = 0.2 * CAM_FPS
MAX_LIGHT_LEVEL = 15

# ==== UTILITIES ====

DIR_TO_ANGLE = {
    Dir.right: 0,
    Dir.top: 90,
    Dir.left: 180,
    Dir.bottom: 270,
    }
