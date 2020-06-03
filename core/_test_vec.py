from copy import copy
from math import floor

from core.classes import WVec
from core.vec import Vec

pos = (-1, 2)
a = WVec(*pos)

print(a + a)
print(a - a)
print(1 - a)
print(1 / a)
print(9 // a)
