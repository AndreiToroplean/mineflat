from math import floor
import numpy as np

from global_params import WATER_HEIGHT, CAM_FPS, PLAYER_DAMPING_FACTOR, CHUNK_SIZE
from animated_surface import AnimAction, AnimatedSurface
from core import WorldVec, Colliders
from core_funcs import world_to_chunk_to_world_vec


class Player:

    def __init__(self, camera, world):
        self.camera = camera
        self.world = world

        self.spawn_pos = np.array((0.5, float(WATER_HEIGHT+0.1)))
        self.pos = np.array(self.spawn_pos)
        self.req_pos = np.array(self.spawn_pos)

        self.vel = np.array((0.0, 0.0))
        self.req_vel = np.array((0.0, 0.0))

        self.acc = np.array((0.0, -22/(CAM_FPS**2)))

        self.world_size = WorldVec(0.6, 1.8)

        self.anim_surf = AnimatedSurface("resources/steve/walking/", world_height=self.world_size.y, neutrals=(0, 8))

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
        self.req_vel[1] = 7.5 / CAM_FPS

    def req_h_move_stop(self):
        self.anim_surf.action = AnimAction.end
        self.req_vel[0] = 0

    def req_v_move_stop(self):
        self.req_vel[1] = 0

    def collide(self, thresh=0.001):
        world_colliders = self.get_world_colliders()
        player_bound_shifts = ((-self.world_size[0] / 2, self.world_size[0] / 2), (0.0, self.world_size[1]))
        block_bound_shifts = ((0, 1), (0, 1))
        tested_pos_bounds = (
            (
                floor(self.req_pos[0] + player_bound_shifts[0][0]),
                floor(self.req_pos[0] + player_bound_shifts[0][1]),
                ),
            (
                floor(self.req_pos[1] + player_bound_shifts[1][0]),
                floor(self.req_pos[1] + player_bound_shifts[1][1]),
                ),
            )

        # vel_dir = []
        # for vel_dir_dim in self.vel:
        #     try:
        #         vel_dir_dim_norm = int(abs(vel_dir_dim) / vel_dir_dim)
        #     except ZeroDivisionError:
        #         vel_dir_dim_norm = 0
        #     vel_dir.append(vel_dir_dim_norm)
        # vel_dir = tuple(vel_dir)

        for pos_y in range(tested_pos_bounds[1][0], tested_pos_bounds[1][1]+1):
            if self.vel[0] < 0:
                pos_x = tested_pos_bounds[0][0]
                if (pos_x, pos_y) in world_colliders.right:
                    self.req_pos[0] = pos_x + block_bound_shifts[0][1] - player_bound_shifts[0][0] + thresh
                    self.vel[0] = 0
                    break

            if self.vel[0] > 0:
                pos_x = tested_pos_bounds[0][1]
                if (pos_x, pos_y) in world_colliders.left:
                    self.req_pos[0] = pos_x + block_bound_shifts[0][0] - player_bound_shifts[0][1] - thresh
                    self.vel[0] = 0
                    break

        for pos_x in range(tested_pos_bounds[0][0], tested_pos_bounds[0][1] + 1):
            if self.vel[1] < 0:
                pos_y = tested_pos_bounds[1][0]
                if (pos_x, pos_y) in world_colliders.top:
                    self.req_pos[1] = pos_y + block_bound_shifts[1][1] - player_bound_shifts[1][0] + thresh
                    self.vel[1] = 0
                    break

            if self.vel[1] > 0:
                pos_y = tested_pos_bounds[1][1]
                if (pos_x, pos_y) in world_colliders.bottom:
                    self.req_pos[1] = pos_y + block_bound_shifts[1][0] - player_bound_shifts[1][1] - thresh
                    self.vel[1] = 0
                    break

    def get_world_colliders(self):
        cur_chunk_pos = world_to_chunk_to_world_vec(self.pos)
        world_colliders = Colliders()
        for pos_x in range(cur_chunk_pos.x-CHUNK_SIZE.x, cur_chunk_pos.x+2*CHUNK_SIZE.x, CHUNK_SIZE.x):
            for pos_y in range(cur_chunk_pos.y-CHUNK_SIZE.y, cur_chunk_pos.y+2*CHUNK_SIZE.y, CHUNK_SIZE.y):
                pos = WorldVec(pos_x, pos_y)
                try:
                    chunk = self.world.chunks_existing[pos]
                except KeyError:
                    pass
                else:
                    for world_colliders_dir, chunk_colliders_dir in zip(world_colliders, chunk.colliders):
                        world_colliders_dir += chunk_colliders_dir
        return world_colliders

    def animate(self):
        self.vel[0] += (self.req_vel[0] - self.vel[0]) * PLAYER_DAMPING_FACTOR
        self.vel[1] += self.req_vel[1]
        self.req_vel[1] = 0

        self.vel += self.acc
        self.req_pos = self.pos + self.vel
        self.collide()
        self.pos = self.req_pos
