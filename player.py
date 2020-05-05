import numpy as np

from global_params import WATER_HEIGHT
from core import WorldVec


class Player:
    move_speed = 0.25

    def __init__(self):
        self.spawn_pos = WorldVec(float(0), float(WATER_HEIGHT))
        self.pos = np.array(self.spawn_pos)
        self.vel = np.array((0.0, 0.0))

    def move_right(self):
        self.vel[0] = self.move_speed

    def move_left(self):
        self.vel[0] = -self.move_speed

    def move_up(self):
        self.vel[1] = self.move_speed

    def move_down(self):
        self.vel[1] = -self.move_speed

    def move_stop(self):
        self.vel[0] = 0
        self.vel[1] = 0

    def animate(self):
        self.pos += self.vel
