import pygame as pg

import globals
from player import Player
from world import World


class Game:
    C_SKY = 20, 230, 240

    def __init__(self):
        pg.init()
        self.main_player = Player()
        self.world = World()

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)

        self.clock = pg.time.Clock()

        # Game constants:
        self.RES = self.screen.get_size()
        self.BLOCKS_ON_SCREEN = tuple(x / globals.BLOCK_SCREEN_SIZE for x in self.RES)
        self.BLOCKS_VIEW_SHIFT = (
            self.BLOCKS_ON_SCREEN[0] * globals.PLAYER_SCREEN_RELATIVE_POS[0],
            self.BLOCKS_ON_SCREEN[1] * globals.PLAYER_SCREEN_RELATIVE_POS[1],
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
        rtn = pg.Rect(
            left=mp_pos[0]-self.BLOCKS_VIEW_SHIFT[0],
            top=mp_pos[1]-self.BLOCKS_VIEW_SHIFT[1],
            width=self.BLOCKS_ON_SCREEN[0],
            height=self.BLOCKS_ON_SCREEN[1],
            )
        return rtn

    def draw_sky(self):
        self.screen.fill(self.C_SKY)

    def draw_world(self):
        self.world.draw(self.view_rect)

    def quit(self):
        pg.quit()
