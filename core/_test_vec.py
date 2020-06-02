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
# print(a)
# a += pos
# print(a)

# print(a + pos)
# print(pos + a)

# print(Vec(a.coords))

from core.funcs import *

b = WVec(102, 35)

print(b // a)
print(b / a)
# print(w_to_c_vec(a))
# print(w_to_c_to_w_vec(a))
