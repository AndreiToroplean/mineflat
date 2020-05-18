from enum import Enum

import pygame as pg


class Controls:
    move_right = pg.K_d
    move_left = pg.K_a
    move_up = pg.K_w
    move_down = pg.K_s
    jump = pg.K_SPACE
    zoom_in = pg.K_KP_PLUS
    zoom_out = pg.K_KP_MINUS
    quit = pg.K_ESCAPE

    break_block = 0
    place_block = 2


class Mods:
    sprinting = pg.KMOD_CTRL
    sneaking = pg.KMOD_SHIFT
