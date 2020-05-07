import numpy as np

from global_params import WATER_HEIGHT
from core import WorldVec
from animated_surface import AnimAction, AnimatedSurface


class Player:
    move_speed = 0.25

    def __init__(self, camera):
        self.camera = camera

        self.spawn_pos = np.array((float(0), float(WATER_HEIGHT)))
        self.pos = np.array(self.spawn_pos)
        self.vel = np.array((0.0, 0.0))

        self.anim_surf = AnimatedSurface("resources/steve/walking/", world_height=1.5)

    def draw(self):
        self.camera.draw_player(self.anim_surf)

    def move_right(self):
        self.anim_surf.action = AnimAction.play
        self.anim_surf.is_reversed = False
        self.vel[0] = self.move_speed

    def move_left(self):
        self.anim_surf.action = AnimAction.play
        self.anim_surf.is_reversed = True
        self.vel[0] = -self.move_speed

    def move_up(self):
        self.vel[1] = self.move_speed

    def move_down(self):
        self.vel[1] = -self.move_speed

    def move_stop(self):
        self.anim_surf.action = AnimAction.reset
        self.vel[0] = 0
        self.vel[1] = 0

    def animate(self):
        self.pos += self.vel
