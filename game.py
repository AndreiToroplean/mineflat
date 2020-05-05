import pygame as pg

from global_params import C_SKY
from camera import Camera
from player import Player
from world import World


class Game:
    def __init__(self):
        pg.init()

        self.camera = Camera()

        self.clock = pg.time.Clock()

        self.main_player = Player()
        self.world = World(self.camera)

    def main_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
                    elif event.key == pg.K_d:
                        self.main_player.move_right()
                    elif event.key == pg.K_a:
                        self.main_player.move_left()
                    elif event.key == pg.K_w:
                        self.main_player.move_up()
                    elif event.key == pg.K_s:
                        self.main_player.move_down()
                    elif event.key == pg.K_KP_PLUS:
                        self.camera.zoom_in()
                    elif event.key == pg.K_KP_MINUS:
                        self.camera.zoom_out()
                elif event.type == pg.KEYUP:
                    self.main_player.move_stop()
                    self.camera.zoom_stop()

            # Movement
            self.main_player.animate()
            self.camera.animate()

            # Graphics
            self.draw_sky()
            self.camera.update_pos(self.main_player.pos)
            self.world.draw()

            pg.display.flip()
            self.clock.tick(60)

    def draw_sky(self):
        self.camera.screen.fill(C_SKY)

    def quit(self):
        pg.quit()
