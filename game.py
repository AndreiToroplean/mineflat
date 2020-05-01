import pygame as pg


class Game:
    def __init__(self):
        pg.init()

        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()

    def main_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return

            self.screen.fill((255, 0, 0))
            pg.display.update()
            self.clock.tick(60)

    def exit(self):
        pg.quit()
