import pygame as pg

from global_params import C_SKY, CAM_FPS
from controls import Ctrls, CONTROLS
from camera import Camera
from player import Player
from world import World


class Game:
    def __init__(self):
        pg.init()

        self.camera = Camera()

        self.clock = pg.time.Clock()

        self.world = World(self.camera)
        self.main_player = Player(self.camera, self.world)

    def main_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return

                    elif event.key == CONTROLS[Ctrls.right]:
                        self.main_player.req_move_right()
                    elif event.key == CONTROLS[Ctrls.left]:
                        self.main_player.req_move_left()
                    elif event.key == CONTROLS[Ctrls.up]:
                        self.main_player.req_move_up()
                    elif event.key == CONTROLS[Ctrls.down]:
                        self.main_player.req_move_down()
                    elif event.key == CONTROLS[Ctrls.jump]:
                        self.main_player.req_jump()

                    elif event.key == CONTROLS[Ctrls.zoom_in]:
                        self.camera.req_zoom_in()
                    elif event.key == CONTROLS[Ctrls.zoom_out]:
                        self.camera.req_zoom_out()

                elif event.type == pg.KEYUP:
                    if event.key == CONTROLS[Ctrls.right] or event.key == CONTROLS[Ctrls.left]:
                        self.main_player.req_h_move_stop()
                    elif event.key == CONTROLS[Ctrls.up] or event.key == CONTROLS[Ctrls.down]:
                        self.main_player.req_v_move_stop()
                    elif event.key == CONTROLS[Ctrls.zoom_in] or event.key == CONTROLS[Ctrls.zoom_out]:
                        self.camera.req_zoom_stop()

            # Movement
            self.main_player.animate()
            self.camera.req_update_pos(self.main_player.pos)
            self.camera.animate()

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