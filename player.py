from global_params import WATER_HEIGHT


class Player:
    def __init__(self):
        self.spawn_pos = 0, WATER_HEIGHT
        self.pos = self.spawn_pos
