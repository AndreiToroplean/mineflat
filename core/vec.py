from typing import overload
from math import floor
from collections.abc import Iterable

import numpy as np


class Vec:
    @overload
    def __init__(self, x: int or float = 0.0, y: int or float = 0.0):
        pass

    @overload
    def __init__(self, vec_like):
        pass

    def __init__(self, *args, **kwargs):
        # FIXME: There are still lots of usage patterns which shouldn't be legal but don't throw exceptions.
        
        x = None
        y = None
        vec_like = None
        if len(args) > 0:
            if isinstance(args[0], np.ndarray):
                vec_like = args[0]
            elif isinstance(args[0], Vec):
                vec_like = np.array(args[0].coords)
            elif isinstance(args[0], Iterable):
                vec_like = np.array(args[0])
            else:
                x = args[0]
        if len(args) > 1:
            y = args[1]
            
        if x is None:
            if "x" in kwargs:
                x = kwargs["x"]
            else:
                x = 0.0
            
        if y is None:
            if "y" in kwargs:
                y = kwargs["y"]
            else:
                y = 0.0
            
        if vec_like is None and "vec_like" in kwargs:
            if isinstance(kwargs["vec_like"], np.ndarray):
                vec_like = kwargs["vec_like"]
            elif isinstance(kwargs["vec_like"], Vec):
                vec_like = np.array(kwargs["vec_like"].coords)
            elif isinstance(kwargs["vec_like"], Iterable):
                vec_like = np.array(kwargs["vec_like"])
            
        if vec_like is None:
            self.coords = np.array((x, y))
        else:
            self.coords = vec_like
            

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
        if isinstance(other, Vec):
            return type(self)(self.coords + other.coords)
        return type(self)(self.coords + other)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        if isinstance(other, Vec):
            return type(self)(self.coords - other.coords)
        return type(self)(self.coords - other)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        if isinstance(other, Vec):
            return type(self)(self.coords * other.coords)
        return type(self)(self.coords * other)

    def __rmul__(self, other):
        return self * other

    def __floordiv__(self, other):
        if isinstance(other, Vec):
            return type(self)(self.coords // other.coords)
        return type(self)(self.coords // other)

    def __rfloordiv__(self, other):
        return type(self)(other // self.coords)

    def __truediv__(self, other):
        if isinstance(other, Vec):
            return type(self)(self.coords / other.coords)
        return type(self)(self.coords / other)

    def __rtruediv__(self, other):
        return type(self)(other / self.coords)

    def __iadd__(self, other):
        if isinstance(other, Vec):
            self.coords += other.coords
        else:
            self.coords += other
        return self

    def __isub__(self, other):
        if isinstance(other, Vec):
            self.coords -= other.coords
        else:
            self.coords -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Vec):
            self.coords *= other.coords
        else:
            self.coords *= other
        return self

    def __ifloordiv__(self, other):
        if isinstance(other, Vec):
            self.coords //= other.coords
        else:
            self.coords //= other
        return self

    def __itruediv__(self, other):
        if isinstance(other, Vec):
            self.coords /= other.coords
        else:
            self.coords /= other
        return self

    def __neg__(self):
        return type(self)(-self.coords)

    def __pos__(self):
        return self

    def __abs__(self):
        return type(self)(abs(self.coords))

    def __round__(self, ndigits=0):
        return type(self)(*(round(coord, ndigits) for coord in self.coords))

    def __floor__(self):
        return type(self)(*(floor(coord) for coord in self.coords))

    def __eq__(self, other):
        return all(self_coord == other_coord for self_coord, other_coord in zip(self, other))

    def __len__(self):
        return 2

    def norm(self):
        return np.linalg.norm(self.coords)

    def normalized(self):
        return self / self.norm()

    def dir_(self):
        return self / abs(self)
