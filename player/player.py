import json
import os
from math import floor

from core.constants import CAM_FPS, PLAYER_POS_DAMPING_FACTOR, GRAVITY, PLAYER_POS_MIN_HEIGHT, RESOURCES_PATH, \
    BLOCK_BOUND_SHIFTS
from core.funcs import get_bounds
from graphics.animated_surface import AnimAction, AnimatedSurface
from core.classes import WVec, WBounds, LoadResult


class Player:
    _ACC = WVec(GRAVITY)
    _ACTION_POS_RATIO = 0.75
    _MAIN_PLAYER_DIR = "steve"

    def __init__(self, name, spawn_pos):
        self.name = name

        self._spawn_pos = WVec(spawn_pos)

        self.pos = WVec()
        self._req_pos = WVec()
        self._vel = WVec()
        self._req_vel = WVec()

        self.spawn()

        self._is_on_ground = False

        self._w_size = WVec(0.6, 1.8)
        self._bounds_w_shift = WBounds(
            min=WVec(-self._w_size.x / 2, 0.0),
            max=WVec(self._w_size.x / 2, self._w_size.y),
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
        return self.pos.y < PLAYER_POS_MIN_HEIGHT

    @property
    def action_w_pos(self):
        """Getter for the position from which the player acts upon its environment.
        """
        action_w_pos = WVec(self.pos)
        action_w_pos.y += self._w_size.y * self._ACTION_POS_RATIO
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
        self._req_vel.x = self._walking_speed

    def req_move_left(self):
        self._anim_surf_walking.sync(self._anim_surf)
        self._anim_surf = self._anim_surf_walking
        self._anim_surf.action = AnimAction.play
        self._anim_surf.is_reversed = True
        self._req_vel.x = -self._walking_speed

    def req_sprint_right(self):
        self._anim_surf_sprinting.sync(self._anim_surf)
        self._anim_surf = self._anim_surf_sprinting
        self._anim_surf.action = AnimAction.play
        self._anim_surf.is_reversed = False
        self._req_vel.x = self._sprinting_speed

    def req_sprint_left(self):
        self._anim_surf_sprinting.sync(self._anim_surf)
        self._anim_surf = self._anim_surf_sprinting
        self._anim_surf.action = AnimAction.play
        self._anim_surf.is_reversed = True
        self._req_vel.x = -self._sprinting_speed

    def req_h_move_stop(self):
        self._anim_surf.action = AnimAction.end
        self._req_vel.x = 0

    def req_v_move_stop(self):
        self._req_vel.y = 0

    def req_jump(self):
        if self._is_on_ground:
            self._req_vel.y = self._jumping_speed
        else:
            self.req_jump_stop()

    def req_jump_stop(self):
        self._req_vel.y = 0

    # ==== APPLY MOVEMENTS ====

    def set_transforms(self, pos, vel=WVec()):
        """Set the transforms directly without going through a request.
        """
        self.pos = WVec(pos)
        self._req_pos = WVec(self.pos)

        self._vel = WVec(vel)
        self._req_vel = WVec(self._vel)

    def spawn(self):
        """Set or reset the player to its spawning state.
        """
        self.set_transforms(self._spawn_pos, (0.0, -100.0 / CAM_FPS))

    def _collide(self, world, threshold=0.001):
        """Check for collisions with the world and update the transforms accordingly.
        """
        world_colliders = world.get_colliders_around(self.pos, c_radius=1)

        tested_horiz_pos = (self._req_pos.x, self.pos.y)
        tested_horiz_pos_bounds = self.get_bounds(tested_horiz_pos)

        tested_vert_pos = (self.pos.x, self._req_pos.y)
        tested_vert_pos_bounds = self.get_bounds(tested_vert_pos)

        for pos_x in range(tested_vert_pos_bounds.min.x, tested_vert_pos_bounds.max.x+1):
            if self._vel.y < 0:
                pos_y = tested_vert_pos_bounds.min.y
                if (pos_x, pos_y) in world_colliders.top:
                    self._req_pos.y = pos_y + BLOCK_BOUND_SHIFTS.max.y - self._bounds_w_shift.min.y + threshold
                    self._vel.y = 0
                    self._is_on_ground = True
                    break

            else:
                pos_y = tested_vert_pos_bounds.max.y
                if (pos_x, pos_y) in world_colliders.bottom:
                    self._req_pos.y = pos_y + BLOCK_BOUND_SHIFTS.min.y - self._bounds_w_shift.max.y - threshold
                    self._vel.y = 0
                    break

        for pos_y in range(tested_horiz_pos_bounds.min.y, tested_horiz_pos_bounds.max.y+1):
            if self._vel.x <= 0:
                pos_x = tested_horiz_pos_bounds.min.x
                if (pos_x, pos_y) in world_colliders.right:
                    self._req_pos.x = pos_x + BLOCK_BOUND_SHIFTS.max.x - self._bounds_w_shift.min.x + threshold
                    self._vel.x = 0
                    break

            else:
                pos_x = tested_horiz_pos_bounds.max.x
                if (pos_x, pos_y) in world_colliders.left:
                    self._req_pos.x = pos_x + BLOCK_BOUND_SHIFTS.min.x - self._bounds_w_shift.max.x - threshold
                    self._vel.x = 0
                    break

    def move(self, world, substeps=1):
        """Apply requested and physics-induced movements.
        """
        self._vel.x += (self._req_vel.x - self._vel.x) * PLAYER_POS_DAMPING_FACTOR
        self._vel.y += self._req_vel.y

        self._vel += self._ACC

        self._is_on_ground = False  # Assumption, to be corrected inside self._collide.

        collision_steps = (floor(self._vel.norm()) + 1) * substeps
        for _ in range(collision_steps):
            self._req_pos = self.pos + self._vel / collision_steps
            self._collide(world)
            self.pos = WVec(self._req_pos)

    # ==== SAVE AND LOAD ====

    def load_from_disk(self, dir_path):
        try:
            with open(os.path.join(dir_path, f"{self.name}.json")) as file:
                data = json.load(file)
        except FileNotFoundError:
            return LoadResult.no_file

        self.set_transforms(data["pos"], data["vel"])
        self._is_on_ground = data["is_on_ground"]
        self._anim_surf.is_reversed = data["is_reversed"]
        return LoadResult.success

    def save_to_disk(self, dir_path):
        data = {
            "pos": tuple(self.pos),
            "vel": tuple(self._vel),
            "is_on_ground": self._is_on_ground,
            "is_reversed": self._anim_surf.is_reversed,
            }
        with open(os.path.join(dir_path, f"{self.name}.json"), "w") as file:
            json.dump(data, file, indent=4)
