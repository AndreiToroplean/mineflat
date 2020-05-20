import json
import os
from math import floor

import numpy as np

from core.constants import CAM_FPS, PLAYER_POS_DAMPING_FACTOR, CHUNK_W_SIZE, GRAVITY, CWD, PLAYER_POS_MIN_HEIGHT
from graphics.animated_surface import AnimAction, AnimatedSurface
from core.classes import WVec, Colliders
from core.funcs import w_to_c_to_w_vec


class Player:
    _acc = np.array(GRAVITY)

    def __init__(self, name, spawn_pos):
        self.name = name

        self._spawn_pos = np.array(spawn_pos)
        self.spawn()

        self._is_on_ground = False

        self._w_size = WVec(0.6, 1.8)

        self._anim_surf_walking = AnimatedSurface(
            os.path.join(CWD, "resources/steve/walking/"),
            w_height=self._w_size.y,
            neutrals=(0, 8),
            )
        self._anim_surf_sprinting = AnimatedSurface(
            os.path.join(CWD, "resources/steve/sprinting/"),
            w_height=self._w_size.y,
            neutrals=(0, 6),
            )
        self._anim_surf = self._anim_surf_walking

        self._walking_speed = 4.5 / CAM_FPS
        self._sprinting_speed = 7.5 / CAM_FPS
        self._jumping_speed = 7.75 / CAM_FPS

    def _collide(self, world, thresh=0.001):
        w_colliders = self._get_w_colliders(world)
        player_bound_shifts = ((-self._w_size[0] / 2, self._w_size[0] / 2), (0.0, self._w_size[1]))
        block_bound_shifts = ((0, 1), (0, 1))
        tested_horiz_pos_bounds = (
            (
                floor(self._req_pos[0] + player_bound_shifts[0][0]),
                floor(self._req_pos[0] + player_bound_shifts[0][1]),
                ),
            (
                floor(self.pos[1] + player_bound_shifts[1][0]),
                floor(self.pos[1] + player_bound_shifts[1][1]),
                ),
            )
        tested_vert_pos_bounds = (
            (
                floor(self.pos[0] + player_bound_shifts[0][0]),
                floor(self.pos[0] + player_bound_shifts[0][1]),
                ),
            (
                floor(self._req_pos[1] + player_bound_shifts[1][0]),
                floor(self._req_pos[1] + player_bound_shifts[1][1]),
                ),
            )

        self._is_on_ground = False
        for pos_x in range(tested_vert_pos_bounds[0][0], tested_vert_pos_bounds[0][1] + 1):
            if self._vel[1] < 0:
                pos_y = tested_vert_pos_bounds[1][0]
                if (pos_x, pos_y) in w_colliders.top:
                    self._req_pos[1] = pos_y + block_bound_shifts[1][1] - player_bound_shifts[1][0] + thresh
                    self._vel[1] = 0
                    self._is_on_ground = True
                    break

            else:
                pos_y = tested_vert_pos_bounds[1][1]
                if (pos_x, pos_y) in w_colliders.bottom:
                    self._req_pos[1] = pos_y + block_bound_shifts[1][0] - player_bound_shifts[1][1] - thresh
                    self._vel[1] = 0
                    break

        for pos_y in range(tested_horiz_pos_bounds[1][0], tested_horiz_pos_bounds[1][1]+1):
            if self._vel[0] < 0:
                pos_x = tested_horiz_pos_bounds[0][0]
                if (pos_x, pos_y) in w_colliders.right:
                    self._req_pos[0] = pos_x + block_bound_shifts[0][1] - player_bound_shifts[0][0] + thresh
                    self._vel[0] = 0
                    break

            else:
                pos_x = tested_horiz_pos_bounds[0][1]
                if (pos_x, pos_y) in w_colliders.left:
                    self._req_pos[0] = pos_x + block_bound_shifts[0][0] - player_bound_shifts[0][1] - thresh
                    self._vel[0] = 0
                    break

    def _get_w_colliders(self, world):
        cur_c_pos = w_to_c_to_w_vec(self.pos)
        w_colliders = Colliders()
        for pos_x in range(cur_c_pos.x - CHUNK_W_SIZE.x, cur_c_pos.x + 2 * CHUNK_W_SIZE.x, CHUNK_W_SIZE.x):
            for pos_y in range(cur_c_pos.y - CHUNK_W_SIZE.y, cur_c_pos.y + 2 * CHUNK_W_SIZE.y, CHUNK_W_SIZE.y):
                pos = WVec(pos_x, pos_y)
                try:
                    chunk = world.chunks_existing[pos]
                except KeyError:
                    pass
                else:
                    for w_colliders_dir, chunk_colliders_dir in zip(w_colliders, chunk.colliders):
                        w_colliders_dir += chunk_colliders_dir
        return w_colliders

    def draw(self, camera):
        camera.draw_player(self._anim_surf, self.pos)

    def req_move_right(self):
        self._anim_surf_walking.sync(self._anim_surf)
        self._anim_surf = self._anim_surf_walking
        self._anim_surf.action = AnimAction.play
        self._anim_surf.is_reversed = False
        self._req_vel[0] = self._walking_speed

    def req_move_left(self):
        self._anim_surf_walking.sync(self._anim_surf)
        self._anim_surf = self._anim_surf_walking
        self._anim_surf.action = AnimAction.play
        self._anim_surf.is_reversed = True
        self._req_vel[0] = -self._walking_speed

    def req_sprint_right(self):
        self._anim_surf_sprinting.sync(self._anim_surf)
        self._anim_surf = self._anim_surf_sprinting
        self._anim_surf.action = AnimAction.play
        self._anim_surf.is_reversed = False
        self._req_vel[0] = self._sprinting_speed

    def req_sprint_left(self):
        self._anim_surf_sprinting.sync(self._anim_surf)
        self._anim_surf = self._anim_surf_sprinting
        self._anim_surf.action = AnimAction.play
        self._anim_surf.is_reversed = True
        self._req_vel[0] = -self._sprinting_speed

    def req_h_move_stop(self):
        self._anim_surf.action = AnimAction.end
        self._req_vel[0] = 0

    def req_v_move_stop(self):
        self._req_vel[1] = 0

    def req_jump(self):
        if self._is_on_ground:
            self._req_vel[1] = self._jumping_speed
        else:
            self.req_jump_stop()

    def req_jump_stop(self):
        self._req_vel[1] = 0

    def move(self, world):
        self._vel[0] += (self._req_vel[0] - self._vel[0]) * PLAYER_POS_DAMPING_FACTOR
        self._vel[1] += self._req_vel[1]

        self._vel += self._acc
        self._req_pos[:] = self.pos
        # Making more collision steps when the player is moving faster than 1 block per frame:
        collision_steps = floor(np.linalg.norm(self._vel)) + 1
        for _ in range(collision_steps):
            self._req_pos += self._vel / collision_steps
            self._collide(world)
        self.pos[:] = self._req_pos

    @property
    def is_dead(self):
        return self.pos[1] < PLAYER_POS_MIN_HEIGHT

    def set_transforms(self, pos, vel=(0.0, 0.0)):
        self.pos = np.array(pos)
        self._req_pos = np.array(self.pos)

        self._vel = np.array(vel)
        self._req_vel = np.array(self._vel)

    def spawn(self):
        self.set_transforms(self._spawn_pos, (0.0, -200.0/CAM_FPS))

    def load_from_disk(self, dir_path):
        try:
            with open(os.path.join(dir_path, f"{self.name}.json")) as file:
                data = json.load(file)
        except FileNotFoundError:
            return

        self.set_transforms(data["pos"], data["vel"])
        self._is_on_ground = data["is_on_ground"]

    def save_to_disk(self, dir_path):
        data = {
            "pos": tuple(self.pos),
            "vel": tuple(self._vel),
            "is_on_ground": self._is_on_ground
            }
        with open(os.path.join(dir_path, f"{self.name}.json"), "w") as file:
            json.dump(data, file, indent=4)
