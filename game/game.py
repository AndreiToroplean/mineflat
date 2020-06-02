import os
from enum import Enum

import pygame as pg

from core.constants import CURSOR, DEBUG, PLAYER_DEFAULT_SPAWN_POS, CURRENT_SAVE_PATH
from game.controls import Controls, Mods
from world.generation import Material
from graphics.camera import Camera
from player.player import Player
from world.world import World


class GameAction(Enum):
    play = 1
    respawn = 0
    quit = -1


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_cursor(*CURSOR)

        self.world = World()
        self.main_player = Player("main_player", spawn_pos=PLAYER_DEFAULT_SPAWN_POS)
        self.camera = Camera()

        self.action = GameAction.play

    def main_loop(self):
        while True:
            # Keyboard inputs
            keys_pressed = pg.key.get_pressed()
            mods_pressed = pg.key.get_mods()

            if keys_pressed[Controls.quit] or pg.event.peek(pg.QUIT) or self.action == GameAction.quit:
                return

            # Requesting horizontal movements
            does_horiz_movement = False
            if keys_pressed[Controls.move_left]:
                if mods_pressed == pg.KMOD_NONE:
                    self.main_player.req_move_left()
                else:
                    if mods_pressed & Mods.sprinting:
                        self.main_player.req_sprint_left()
                does_horiz_movement ^= True
            if keys_pressed[Controls.move_right]:
                if mods_pressed == pg.KMOD_NONE:
                    self.main_player.req_move_right()
                else:
                    if mods_pressed & Mods.sprinting:
                        self.main_player.req_sprint_right()
                does_horiz_movement ^= True
            if not does_horiz_movement:
                self.main_player.req_h_move_stop()

            # Requesting jumps
            if keys_pressed[Controls.jump]:
                self.main_player.req_jump()
            else:
                self.main_player.req_jump_stop()

            # Requesting camera zooms
            is_zooming = False
            if keys_pressed[Controls.zoom_in]:
                self.camera.req_zoom_in()
                is_zooming ^= True
            if keys_pressed[Controls.zoom_out]:
                self.camera.req_zoom_out()
                is_zooming ^= True
            if not is_zooming:
                self.camera.req_zoom_stop()

            # Mouse inputs
            mb_pressed = pg.mouse.get_pressed()

            # Breaking blocks
            if mb_pressed[Controls.break_block]:
                self.world.req_break_block(self.camera.selected_block_w_pos)

            # Placing blocks
            if mb_pressed[Controls.place_block]:
                self.world.req_place_block(
                    self.camera.selected_space_w_pos,
                    Material.dirt,
                    self.main_player.get_bounds()
                    )
                # TODO: choosing the material.

            # Applying movements
            self.main_player.move(self.world)
            self.camera.req_move(self.main_player.pos)
            self.camera.move()

            # Graphics
            self.draw_sky()
            self.world.draw_and_tick(self.camera)
            self.main_player.draw(self.camera)
            self.draw_gui()

            if DEBUG:
                self.camera.draw_debug_info()

            self.camera.display_flip_and_clock_tick()

            # Death
            if self.main_player.is_dead:
                self.death_loop()

    def death_loop(self):
        self.main_player.spawn()
        self.action = GameAction.quit

    def __enter__(self):
        # Create SAVES_CURRENT_DIR if it doesn't already exist.
        try:
            os.makedirs(CURRENT_SAVE_PATH)
        except FileExistsError:
            pass

        self.world.load_from_disk(CURRENT_SAVE_PATH)
        self.main_player.load_from_disk(CURRENT_SAVE_PATH)

        self.camera.set_transforms(self.main_player.pos)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.world.save_to_disk(CURRENT_SAVE_PATH)
        self.main_player.save_to_disk(CURRENT_SAVE_PATH)
        pg.quit()

    def draw_sky(self):
        self.camera.draw_sky()

    def draw_gui(self):
        self.camera.draw_block_selector(self.main_player.action_w_pos, self.world)
