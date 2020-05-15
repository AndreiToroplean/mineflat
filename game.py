import pygame as pg

from global_params import C_SKY, CAM_FPS, CURSOR
from controls import Controls, Mods
from camera import Camera
from player import Player
from world import World


class Game:
    def __init__(self):
        pg.init()
        pg.mouse.set_cursor((16, 16), (8, 8), *pg.cursors.compile(CURSOR))

        self.camera = Camera()

        self.clock = pg.time.Clock()

        self.world = World(self.camera)
        self.main_player = Player(self.camera, self.world)

    def main_loop(self):
        while True:
            keys_pressed = pg.key.get_pressed()
            mods_pressed = pg.key.get_mods()

            if keys_pressed[Controls.quit] or pg.event.peek(pg.QUIT):
                return

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

            if keys_pressed[Controls.jump]:
                self.main_player.req_jump()
            else:
                self.main_player.req_jump_stop()

            is_zooming = False
            if keys_pressed[Controls.zoom_in]:
                self.camera.req_zoom_in()
                is_zooming ^= True
            if keys_pressed[Controls.zoom_out]:
                self.camera.req_zoom_out()
                is_zooming ^= True
            if not is_zooming:
                self.camera.req_zoom_stop()

            # Movement
            self.main_player.move()
            self.camera.req_move(self.main_player.pos)
            self.camera.move()

            # Graphics
            self.draw_sky()
            self.world.draw()
            self.main_player.draw()

            pg.display.flip()
            self.clock.tick(CAM_FPS)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pg.quit()

    def draw_sky(self):
        self.camera.screen.fill(C_SKY)
