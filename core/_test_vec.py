from copy import copy
from math import floor

from core.vec import Vec

pos = (-1, 2)
a = Vec(*pos)

# print(hash(a))
# print(hash(tuple(a)))
# print(hash(pos))
#
# test = {a: 0}
# print(tuple(a) in test)
# print(hash(a) == hash(tuple(a)))
# print(a == pos)
#
# a = copy(a)
#
print(a)
a += pos
print(a)

# print(a + pos)
# print(pos + a)

# print(Vec(a.coords))
