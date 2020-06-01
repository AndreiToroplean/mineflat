import json
import os
from math import floor
from copy import copy

# import numpy as np

from core.constants import CAM_FPS, PLAYER_POS_DAMPING_FACTOR, GRAVITY, PLAYER_POS_MIN_HEIGHT, RESOURCES_PATH, \
    BLOCK_BOUND_SHIFTS
from core.funcs import get_bounds
from graphics.animated_surface import AnimAction, AnimatedSurface
from core.classes import WVec, WBounds, WDimBounds


class Player:
    _ACC = copy(GRAVITY)
    _ACTION_POS_RATIO = 0.75
    _MAIN_PLAYER_DIR = "steve"

    def __init__(self, name, spawn_pos):
        self.name = name

        self._spawn_pos = copy(spawn_pos)

        self.pos = WVec()
        self._req_pos = WVec()
        self._vel = WVec()
        self._req_vel = WVec()

        self.spawn()

        self._is_on_ground = False

        self._w_size = WVec(0.6, 1.8)
        self._bounds_w_shift = WBounds(
            x=WDimBounds(-self._w_size[0] / 2, self._w_size[0] / 2),
            y=WDimBounds(0.0, self._w_size[1]),
            )

        self._anim_surf_walking = AnimatedSurface(
            os.path.join(RESOURCES_PATH, self._MAIN_PLAYER_DIR, "walking"),
            w_height=self._w_size.y,
            neutrals=(0, 8),
            )
        self._anim_surf_sprinting = AnimatedSurface(
            os.path.join(RESOURCES_PATH, self._MAIN_PLAYER_DIR, "sprinting"),
            w_height=self._w_size.y,
            neutrals=(0, 6),
            )
        self._anim_surf = self._anim_surf_walking

        self._walking_speed = 4.5 / CAM_FPS
        self._sprinting_speed = 7.5 / CAM_FPS
        self._jumping_speed = 7.75 / CAM_FPS

    # ==== GET DATA ====

    def get_bounds(self, w_pos=None) -> WBounds:
        """Return the boundaries of the Player at its current position, or at w_pos if the argument has been passed.
        """
        if w_pos is None:
            w_pos = self.pos

        return get_bounds(w_pos, self._bounds_w_shift)

    @property
    def is_dead(self):
        return self.pos[1] < PLAYER_POS_MIN_HEIGHT

    @property
    def action_w_pos(self):
        """Getter for the position from which the player acts upon its environment.
        """
        action_w_pos = WVec(self.pos)
        action_w_pos[1] += self._w_size[1] * self._ACTION_POS_RATIO
        return action_w_pos

    # ==== DRAW ====

    def draw(self, camera):
        camera.draw_player(self._anim_surf, self.pos)

    # ==== REQUEST MOVEMENTS ====

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

    # ==== APPLY MOVEMENTS ====

    def set_transforms(self, pos, vel=(0.0, 0.0)):
        """Set the transforms directly without going through a request.
        """
        self.pos = WVec(pos)
        self._req_pos = WVec(self.pos)

        self._vel = WVec(vel)
        self._req_vel = WVec(self._vel)

    def spawn(self):
        """Set or reset the player to its spawning state.
        """
        self.set_transforms(self._spawn_pos, (0.0, -200.0/CAM_FPS))

    def _collide(self, world, threshold=0.001):
        """Check for collisions with the world and update the transforms accordingly.
        """
        world_colliders = world.get_colliders_around(self.pos)

        tested_horiz_pos = (self._req_pos[0], self.pos[1])
        tested_horiz_pos_bounds = self.get_bounds(tested_horiz_pos)

        tested_vert_pos = (self.pos[0], self._req_pos[1])
        tested_vert_pos_bounds = self.get_bounds(tested_vert_pos)

        self._is_on_ground = False
        for pos_x in range(tested_vert_pos_bounds.x.min, tested_vert_pos_bounds.x.max+1):
            if self._vel[1] < 0:
                pos_y = tested_vert_pos_bounds.y.min
                if (pos_x, pos_y) in world_colliders.top:
                    self._req_pos[1] = pos_y + BLOCK_BOUND_SHIFTS.y.max - self._bounds_w_shift.y.min + threshold
                    self._vel[1] = 0
                    self._is_on_ground = True
                    break

            else:
                pos_y = tested_vert_pos_bounds.y.max
                if (pos_x, pos_y) in world_colliders.bottom:
                    self._req_pos[1] = pos_y + BLOCK_BOUND_SHIFTS.y.min - self._bounds_w_shift.y.max - threshold
                    self._vel[1] = 0
                    break

        for pos_y in range(tested_horiz_pos_bounds.y.min, tested_horiz_pos_bounds.y.max+1):
            if self._vel[0] < 0:
                pos_x = tested_horiz_pos_bounds.x.min
                if (pos_x, pos_y) in world_colliders.right:
                    self._req_pos[0] = pos_x + BLOCK_BOUND_SHIFTS.x.max - self._bounds_w_shift.x.min + threshold
                    self._vel[0] = 0
                    break

            else:
                pos_x = tested_horiz_pos_bounds.x.max
                if (pos_x, pos_y) in world_colliders.left:
                    self._req_pos[0] = pos_x + BLOCK_BOUND_SHIFTS.x.min - self._bounds_w_shift.x.max - threshold
                    self._vel[0] = 0
                    break

    def move(self, world):
        """Apply requested and physics-induced movements.
        """
        self._vel[0] += (self._req_vel[0] - self._vel[0]) * PLAYER_POS_DAMPING_FACTOR
        self._vel[1] += self._req_vel[1]

        self._vel += self._ACC
        self._req_pos = WVec(self.pos)
        # Making more collision steps when the player is moving faster than 1 block per frame:
        collision_steps = floor(self._vel.norm()) + 1
        for _ in range(collision_steps):
            self._req_pos += self._vel / collision_steps
            self._collide(world)
        self.pos = WVec(self._req_pos)

    # ==== SAVE AND LOAD ====

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
