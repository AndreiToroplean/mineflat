from enum import Enum

import pygame as pg


class Ctrls(Enum):
    right = 0
    left = 1
    up = 2
    down = 3
    jump = 4
    zoom_in = 5
    zoom_out = 6


CONTROLS = {
    Ctrls.right: pg.K_d,
    Ctrls.left: pg.K_a,
    Ctrls.up: pg.K_w,
    Ctrls.down: pg.K_s,
    Ctrls.jump: pg.K_SPACE,

    Ctrls.zoom_in: pg.K_KP_PLUS,
    Ctrls.zoom_out: pg.K_KP_MINUS,
    }
