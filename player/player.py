import os
from math import floor

import numpy as np

from core.global_params import CAM_FPS, PLAYER_DAMPING_FACTOR, CHUNK_SIZE, GRAVITY
from core.animated_surface import AnimAction, AnimatedSurface
from core.core import WorldVec, Colliders
from core.core_funcs import world_to_chunk_to_world_vec


class Player:

    def __init__(self, spawn_pos):
        self._spawn_pos = np.array(spawn_pos)
        self.pos = np.array(self._spawn_pos)
        self._req_pos = np.array(self._spawn_pos)

        self._is_on_ground = False

        self._vel = np.array((0.0, 0.0))
        self._req_vel = np.array((0.0, 0.0))

        self._acc = np.array(GRAVITY)

        self._world_size = WorldVec(0.6, 1.8)

        cwd = os.getcwd()
        self._anim_surf_walking = AnimatedSurface(
            os.path.join(cwd, "resources/steve/walking/"),
            world_height=self._world_size.y,
            neutrals=(0, 8),
            )
        self._anim_surf_sprinting = AnimatedSurface(
            os.path.join(cwd, "resources/steve/sprinting/"),
            world_height=self._world_size.y,
            neutrals=(0, 6),
            )
        self._anim_surf = self._anim_surf_walking

        self._walking_speed = 4.5 / CAM_FPS
        self._sprinting_speed = 7.5 / CAM_FPS
        self._jumping_speed = 7.75 / CAM_FPS

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
        self._vel[0] += (self._req_vel[0] - self._vel[0]) * PLAYER_DAMPING_FACTOR
        self._vel[1] += self._req_vel[1]

        self._vel += self._acc
        self._req_pos[:] = self.pos
        # Making more collision steps when the player is moving faster than 1 block per frame:
        collision_steps = floor(np.linalg.norm(self._vel)) + 1
        for _ in range(collision_steps):
            self._req_pos += self._vel / collision_steps
            self._collide(world)
        self.pos[:] = self._req_pos

    def _collide(self, world, thresh=0.001):
        world_colliders = self._get_world_colliders(world)
        player_bound_shifts = ((-self._world_size[0] / 2, self._world_size[0] / 2), (0.0, self._world_size[1]))
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

        for pos_y in range(tested_horiz_pos_bounds[1][0], tested_horiz_pos_bounds[1][1]+1):
            if self._vel[0] < 0:
                pos_x = tested_horiz_pos_bounds[0][0]
                if (pos_x, pos_y) in world_colliders.right:
                    self._req_pos[0] = pos_x + block_bound_shifts[0][1] - player_bound_shifts[0][0] + thresh
                    self._vel[0] = 0
                    break

            if self._vel[0] > 0:
                pos_x = tested_horiz_pos_bounds[0][1]
                if (pos_x, pos_y) in world_colliders.left:
                    self._req_pos[0] = pos_x + block_bound_shifts[0][0] - player_bound_shifts[0][1] - thresh
                    self._vel[0] = 0
                    break

        self._is_on_ground = False
        for pos_x in range(tested_vert_pos_bounds[0][0], tested_vert_pos_bounds[0][1] + 1):
            if self._vel[1] < 0:
                pos_y = tested_vert_pos_bounds[1][0]
                if (pos_x, pos_y) in world_colliders.top:
                    self._req_pos[1] = pos_y + block_bound_shifts[1][1] - player_bound_shifts[1][0] + thresh
                    self._vel[1] = 0
                    self._is_on_ground = True
                    break

            if self._vel[1] > 0:
                pos_y = tested_vert_pos_bounds[1][1]
                if (pos_x, pos_y) in world_colliders.bottom:
                    self._req_pos[1] = pos_y + block_bound_shifts[1][0] - player_bound_shifts[1][1] - thresh
                    self._vel[1] = 0
                    break

    def _get_world_colliders(self, world):
        cur_chunk_pos = world_to_chunk_to_world_vec(self.pos)
        world_colliders = Colliders()
        for pos_x in range(cur_chunk_pos.x-CHUNK_SIZE.x, cur_chunk_pos.x+2*CHUNK_SIZE.x, CHUNK_SIZE.x):
            for pos_y in range(cur_chunk_pos.y-CHUNK_SIZE.y, cur_chunk_pos.y+2*CHUNK_SIZE.y, CHUNK_SIZE.y):
                pos = WorldVec(pos_x, pos_y)
                try:
                    chunk = world.chunks_existing[pos]
                except KeyError:
                    pass
                else:
                    for world_colliders_dir, chunk_colliders_dir in zip(world_colliders, chunk.colliders):
                        world_colliders_dir += chunk_colliders_dir
        return world_colliders
