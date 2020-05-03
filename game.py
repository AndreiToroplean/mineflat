import pygame as pg

from global_params import C_SKY
from player import Player
from world import World


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.res = self.screen.get_size()
        self.clock = pg.time.Clock()

        self.main_player = Player()
        self.world = World(self.res)
        # self.world = World((1920, 1080))

    def main_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return

            self.draw_sky()
            self.draw_world()

            pg.display.flip()
            self.clock.tick(60)

    def draw_sky(self):
        self.screen.fill(C_SKY)

    def draw_world(self):
        surface, pix_shift = self.world.get_surface(self.main_player.pos)
        pix_shift = 0, 0  # FIXME
        self.screen.blit(surface, pix_shift)

    def quit(self):
        pg.quit()
