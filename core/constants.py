import os

import pygame as pg

from core.classes import PixVec, WVec, WBounds, Dir

# ==== TECHNICAL DIMENSIONS ====
PLAYER_S_POS = PixVec(0.5, 0.333)
HOTBAR_S_POS = PixVec(0.5, 0.1)
HOTBAR_ORIG_PIX_SIZE = PixVec(184, 24)
HOTBAR_PIX_SIZE = HOTBAR_ORIG_PIX_SIZE * 4
BLOCK_PIX_SIZE = PixVec(16, 16)  # Should stay equal to block texture size resolution. That is, 16.
CHUNK_W_SIZE = WVec(8, 8)
CHUNK_PIX_SIZE = BLOCK_PIX_SIZE * CHUNK_W_SIZE
WORLD_HEIGHT_BOUNDS = WVec(0, 2**8)
BLOCK_BOUND_SHIFTS = WBounds(WVec(0, 0), WVec(1, 1))

# ==== COLORS ====
C_KEY = pg.Color(255, 0, 0)

C_BLACK = pg.Color(0, 0, 0)
C_WHITE = pg.Color(255, 255, 255)
C_SKY = pg.Color(120, 190, 225)

# ==== CAM ====
CAM_FPS = 60
CAM_DEFAULT_SCALE = 64.0
CAM_SCALE_BOUNDS = (16.0, 128.0)

# ==== GAME DYNAMICS ====
GRAVITY = WVec(0.0, -22 / (CAM_FPS ** 2))
PLAYER_ABILITY_FACTOR = 1
ACTION_MAX_DISTANCE = PLAYER_ABILITY_FACTOR * 5
ACTION_COOLDOWN_DELAY = 0.2 * CAM_FPS

# ==== PLAYER PARAMS ====
PLAYER_DEFAULT_SPAWN_POS = WVec(0.5, WORLD_HEIGHT_BOUNDS.y)
PLAYER_POS_DAMPING_FACTOR = 0.5
PLAYER_POS_MIN_HEIGHT = WORLD_HEIGHT_BOUNDS.x - 50

# ==== GAME PARAMS ====
DEBUG = False

FULLSCREEN = False
WHITE_WORLD = False
CHUNK_BORDERS = False
SAVE = True
LOAD = True

if not DEBUG:
    FULLSCREEN = True
    WHITE_WORLD = False
    CHUNK_BORDERS = False
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

# ==== LIGHT DYNAMICS ====
LIGHT_MAX_LEVEL = 15
LIGHT_BLOCK_ATTENUATION = 5
LIGHT_MAX_RECURSION = 3

# ==== UTILITIES ====
DIR_TO_ANGLE = {
    Dir.right: 0,
    Dir.up: 90,
    Dir.left: 180,
    Dir.down: 270,
    }
PIX_ORIGIN = PixVec()
