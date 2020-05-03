import pygame as pg

from global_params import BLOCK_PIX_SIZE, PLAYER_SCREEN_POS, C_SKY
from game_params import GameParams
from core import Color, WorldVec, WorldViewRect
from player import Player
from world import World


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()

        self.params = GameParams()
        self.params.RES = self.screen.get_size()
        # self.params.RES = 1920, 1080  # prov
        self.params.BLOCKS_ON_SCREEN = tuple(x / BLOCK_PIX_SIZE for x in self.params.RES)
        self.params.BLOCKS_ON_EACH_SIDE = (
            self.params.BLOCKS_ON_SCREEN[0] * PLAYER_SCREEN_POS[0],
            self.params.BLOCKS_ON_SCREEN[1] * PLAYER_SCREEN_POS[1],
            self.params.BLOCKS_ON_SCREEN[0] * (1 - PLAYER_SCREEN_POS[0]),
            self.params.BLOCKS_ON_SCREEN[1] * (1 - PLAYER_SCREEN_POS[1]),
            )

        self.main_player = Player()
        self.world = World(self.params)

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

    @property
    def view_rect(self):
        """World referred part of the world visible on screen. """
        mp_pos = self.main_player.pos
        rtn = WorldViewRect(
            WorldVec(
                x=mp_pos[0] - self.params.BLOCKS_ON_EACH_SIDE[0],
                y=mp_pos[1] - self.params.BLOCKS_ON_EACH_SIDE[1],
                ),
            WorldVec(
                x=mp_pos[0] + self.params.BLOCKS_ON_EACH_SIDE[2],
                y=mp_pos[1] + self.params.BLOCKS_ON_EACH_SIDE[3],
                ),
            )
        return rtn

    def draw_sky(self):
        self.screen.fill(C_SKY)

    def draw_world(self):
        self.world.draw(self.view_rect)
        # compute the displacement of self.world.surface relative to self.screen
        # blit self.world.surface to self.screen in the computed position

    def quit(self):
        pg.quit()
