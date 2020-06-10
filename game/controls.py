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

    select_item_0 = pg.K_1
    select_item_1 = pg.K_2
    select_item_2 = pg.K_3
    select_item_3 = pg.K_4
    select_item_4 = pg.K_5
    select_item_5 = pg.K_6
    select_item_6 = pg.K_7
    select_item_7 = pg.K_8
    select_item_8 = pg.K_9

    break_block = 0
    place_block = 2


class Mods:
    sprinting = pg.KMOD_CTRL
    sneaking = pg.KMOD_SHIFT
