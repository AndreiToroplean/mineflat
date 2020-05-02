import pygame as pg

from global_params import GlobalParams
from core import Color, WorldPos, WorldViewRect
from player import Player
from world import World


class Game:
    C_SKY = Color(20, 230, 240)

    def __init__(self):
        self.global_params = GlobalParams()

        pg.init()
        self.main_player = Player()
        self.world = World(self.global_params)

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        self.clock = pg.time.Clock()

        # Game constants:
        self.global_params.RES = self.screen.get_size()
        self.global_params.BLOCKS_ON_SCREEN = tuple(x / self.global_params.BLOCK_SCREEN_SIZE for x in self.global_params.RES)
        self.global_params.BLOCKS_ON_EACH_SIDE = (
            self.global_params.BLOCKS_ON_SCREEN[0] * self.global_params.PLAYER_SCREEN_RELATIVE_POS[0],
            self.global_params.BLOCKS_ON_SCREEN[1] * self.global_params.PLAYER_SCREEN_RELATIVE_POS[1],
            self.global_params.BLOCKS_ON_SCREEN[0] * (1-self.global_params.PLAYER_SCREEN_RELATIVE_POS[0]),
            self.global_params.BLOCKS_ON_SCREEN[1] * (1-self.global_params.PLAYER_SCREEN_RELATIVE_POS[1]),
            )

    def main_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return

            self.draw_sky()
            self.draw_world()

            self.clock.tick(60)

    @property
    def view_rect(self):
        """World referred part of the world visible on screen. """
        mp_pos = self.main_player.pos
        rtn = WorldViewRect(
            WorldPos(
                x=mp_pos[0] - self.global_params.BLOCKS_ON_EACH_SIDE[0],
                y=mp_pos[1] - self.global_params.BLOCKS_ON_EACH_SIDE[1],
                ),
            WorldPos(
                x=mp_pos[0] + self.global_params.BLOCKS_ON_EACH_SIDE[2],
                y=mp_pos[1] + self.global_params.BLOCKS_ON_EACH_SIDE[3],
                ),
            )
        return rtn

    def draw_sky(self):
        self.screen.fill(self.C_SKY)

    def draw_world(self):
        self.world.draw(self.view_rect)

    def quit(self):
        pg.quit()
