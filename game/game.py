import os
from enum import Enum

import pygame as pg

from core.classes import LoadResult
from core.constants import DEBUG, PLAYER_DEFAULT_SPAWN_POS, CURRENT_SAVE_PATH, LOAD, SAVE
from graphics.cursor import CURSOR
from game.controls import Controls, Mods
from graphics.hotbar import Hotbar
from item.block import BlockType
from graphics.camera import Camera
from player.player import Player
from world.world import World


class GameAction(Enum):
    play = 1
    respawn = 0
    quit = -1
    quit_without_saving = -2


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_cursor(*CURSOR)

        self._camera = Camera()
        self._hotbar = Hotbar()
        self._world = World()
        self._main_player = Player("main_player", spawn_pos=PLAYER_DEFAULT_SPAWN_POS)

        self._action = GameAction.play

    def main_loop(self):
        while True:
            # Keyboard inputs
            keys_pressed = pg.key.get_pressed()
            mods_pressed = pg.key.get_mods()

            if (keys_pressed[Controls.quit]
                    or pg.event.peek(pg.QUIT)
                    or self._action == GameAction.quit
                    or self._action == GameAction.quit_without_saving):
                return

            # Requesting horizontal movements
            does_horiz_movement = False
            if keys_pressed[Controls.move_left]:
                if mods_pressed == pg.KMOD_NONE:
                    self._main_player.req_move_left()
                else:
                    if mods_pressed & Mods.sprinting:
                        self._main_player.req_sprint_left()
                does_horiz_movement ^= True
            if keys_pressed[Controls.move_right]:
                if mods_pressed == pg.KMOD_NONE:
                    self._main_player.req_move_right()
                else:
                    if mods_pressed & Mods.sprinting:
                        self._main_player.req_sprint_right()
                does_horiz_movement ^= True
            if not does_horiz_movement:
                self._main_player.req_h_move_stop()

            # Requesting jumps
            if keys_pressed[Controls.jump]:
                self._main_player.req_jump()
            else:
                self._main_player.req_jump_stop()

            # Requesting camera zooms
            is_zooming = False
            if keys_pressed[Controls.zoom_in]:
                self._camera.req_zoom_in()
                is_zooming ^= True
            if keys_pressed[Controls.zoom_out]:
                self._camera.req_zoom_out()
                is_zooming ^= True
            if not is_zooming:
                self._camera.req_zoom_stop()

            # Mouse inputs
            mb_pressed = pg.mouse.get_pressed()

            # Breaking blocks
            if mb_pressed[Controls.break_block]:
                self._world.req_break_block(self._camera.selected_block_w_pos)

            # Placing blocks
            if mb_pressed[Controls.place_block]:
                self._world.req_place_block(
                    self._camera.selected_space_w_pos,
                    BlockType.dirt,
                    self._main_player.get_bounds()
                    )
                # TODO: choosing the block_type.

            # Applying movements
            self._main_player.move(self._world)
            self._camera.req_move(self._main_player.pos)
            self._camera.move()

            # Graphics
            self._world.draw_and_tick(self._camera)
            self._main_player.draw(self._camera, self._world)
            self.draw_gui()

            if DEBUG:
                self._camera.draw_debug_info()

            self._camera.display_flip_and_clock_tick()

            # Death
            if self._main_player.is_dead:
                self.death_loop()

    def death_loop(self):
        self._main_player.spawn()
        self._action = GameAction.quit

    def __enter__(self):
        if LOAD:
            # Create SAVES_CURRENT_DIR if it doesn't already exist.
            try:
                os.makedirs(CURRENT_SAVE_PATH)
            except FileExistsError:
                pass

            world_load_result = self._world.load_from_disk(CURRENT_SAVE_PATH)
            player_load_result = self._main_player.load_from_disk(CURRENT_SAVE_PATH)

            if world_load_result == LoadResult.incompatible or player_load_result == LoadResult.incompatible:
                self._action = GameAction.quit_without_saving
                print("Error: incompatible save file.")

        self._camera.set_transforms(self._main_player.pos)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if SAVE and not self._action == GameAction.quit_without_saving:
            self._world.save_to_disk(CURRENT_SAVE_PATH)
            self._main_player.save_to_disk(CURRENT_SAVE_PATH)

        pg.quit()

    def draw_gui(self):
        self._camera.draw_block_selector(self._main_player.action_w_pos, self._world)
        self._hotbar.draw(self._camera)
