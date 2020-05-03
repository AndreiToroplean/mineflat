import pygame as pg


class Display:
    def __init__(self, pg_surf):
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.screen.blit(pg_surf, (0, 0))
        pg.display.flip()
        self.loop()
        pg.quit()

    def loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        return
            self.clock.tick(60)
