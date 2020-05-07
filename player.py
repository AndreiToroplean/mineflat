import numpy as np

from global_params import WATER_HEIGHT, CAM_FPS, PLAYER_DAMPING_FACTOR
from animated_surface import AnimAction, AnimatedSurface


class Player:

    def __init__(self, camera):
        self.camera = camera

        self.spawn_pos = np.array((0.5, float(WATER_HEIGHT)))
        self.pos = np.array(self.spawn_pos)

        self.vel = np.array((0.0, 0.0))
        self.req_vel = np.array((0.0, 0.0))

        self.acc = np.array((0.0, -22/(CAM_FPS**2)))

        self.anim_surf = AnimatedSurface("resources/steve/walking/", world_height=1.5, neutrals=(0, 8))

        self.walking_speed = 4.32 / CAM_FPS

    def draw(self):
        self.camera.draw_player(self.anim_surf, self.pos)

    def req_move_right(self):
        self.anim_surf.action = AnimAction.play
        self.anim_surf.is_reversed = False
        self.req_vel[0] = self.walking_speed

    def req_move_left(self):
        self.anim_surf.action = AnimAction.play
        self.anim_surf.is_reversed = True
        self.req_vel[0] = -self.walking_speed

    def req_move_up(self):
        self.req_vel[1] = self.walking_speed

    def req_move_down(self):
        self.req_vel[1] = -self.walking_speed

    def req_jump(self):
        self.vel[1] += 6 / CAM_FPS

    def req_h_move_stop(self):
        self.anim_surf.action = AnimAction.end
        self.req_vel[0] = 0

    def req_v_move_stop(self):
        self.req_vel[1] = 0

    def animate(self):
        self.vel[0] += (self.req_vel[0] - self.vel[0]) * PLAYER_DAMPING_FACTOR
        self.vel += self.acc
        self.pos += self.vel
        if self.pos[1] < WATER_HEIGHT:
            self.pos[1] = WATER_HEIGHT
            self.vel[1] = 0
