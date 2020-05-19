import os

import pygame as pg

from core.classes import PixVec, ScreenVec, WorldVec

# Technical dimensions
PLAYER_SCREEN_POS = ScreenVec(0.5, 0.333)
BLOCK_PIX_SIZE = 16  # Should stay equal to block texture size resolution. That is, 16.
CHUNK_SIZE = WorldVec(8, 8)
CHUNK_PIX_SIZE = PixVec(*[BLOCK_PIX_SIZE * chunk_size_dim for chunk_size_dim in CHUNK_SIZE])
WORLD_HEIGHT_BOUNDS = (0, 2**8)

# Colors
C_KEY = pg.Color(255, 0, 0)

C_SKY = pg.Color(120, 190, 225)

# Cam
CAM_FPS = 30
CAM_DEFAULT_SCALE = 64.0
CAM_SCALE_BOUNDS = (32.0, 128.0)

# Player params
PLAYER_DEFAULT_SPAWN_POS = (0.5, WORLD_HEIGHT_BOUNDS[1])
PLAYER_POS_DAMPING_FACTOR = 0.5

# Cursor
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

# Game params
FULLSCREEN = True
DEBUG = True

CWD = os.getcwd()
SAVE_PATH = os.path.join(CWD, "save/world_01.json")

# Game dynamics
GRAVITY = (0.0, -22 / (CAM_FPS ** 2))
