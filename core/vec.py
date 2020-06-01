from typing import overload
from math import floor

import numpy as np


class Vec:
    @overload
    def __init__(self, x: int or float, y: int or float):
        pass

    @overload
    def __init__(self, *, coords: np.ndarray):
        pass

    def __init__(self, *args, **kwargs):
        if "coords" in kwargs:
            self.coords = kwargs["coords"]
            return
        coords = args + tuple(kwargs.values())
        self.coords = np.array(coords)

    @property
    def x(self):
        return self.coords[0]

    @property
    def y(self):
        return self.coords[1]

    @x.setter
    def x(self, x):
        self.coords[0] = x

    @y.setter
    def y(self, y):
        self.coords[1] = y

    def __getitem__(self, key):
        return self.coords[key]

    def __setitem__(self, key, value):
        self.coords[key] = value

    def __repr__(self):
        return f"{type(self).__name__}(x={self.x}, y={self.y})"

    def __iter__(self):
        return iter((self.x, self.y))

    def __hash__(self):
        return hash(tuple(self))

    def __add__(self, other):
        return Vec(coords=self.coords + other.coords)

    def __sub__(self, other):
        return Vec(coords=self.coords - other.coords)

    def __mul__(self, other):
        if isinstance(other, Vec):
            return Vec(coords=self.coords * other.coords)
        return Vec(coords=self.coords * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Vec):
            return Vec(coords=self.coords / other.coords)
        return Vec(coords=self.coords / other)

    def __rtruediv__(self, other):
        return self.__truediv__(other)

    def __iadd__(self, other):
        self.coords += other.coords

    def __isub__(self, other):
        self.coords -= other.coords

    def __imul__(self, other):
        self.coords *= other.coords

    def __itruediv__(self, other):
        self.coords /= other.coords

    def __neg__(self):
        return Vec(coords=-self.coords)

    def __pos__(self):
        return self

    def __abs__(self):
        return Vec(coords=abs(self.coords))

    def __round__(self, ndigits=0):
        return Vec(*(round(coord, ndigits) for coord in self.coords))

    def __floor__(self):
        return Vec(*(floor(coord) for coord in self.coords))

    def __eq__(self, other):
        return all(self_coord == other_coord for self_coord, other_coord in zip(self, other))
