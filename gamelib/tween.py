'''A collection of functions to find an eased value between A and B, with a
progression unit varying from 0 to 1'''

# Much of the credit to the pytweening project, whose implementation was used as
# a guideline for this one
# https://github.com/asweigart/pytweening/tree/master/pytweening

import math

def linear(a, b, n):
    return apply(a, b, n)

def quadratic(a, b, n):
    return apply(a, b, n ** 2)

def quadraticeaseout(a, b, n):
    return apply(a, b, -n * (n - 2))

def quadraticeaseinout(a, b, n):
    if n < 0.5:
        return apply(a, b, 2 * (n ** 2))
    else:
        k = (n * 2) - 1
        return apply(a, b, -0.5 * ((k * (k - 2)) - 1))

def cubic(a, b, n):
    return apply(a, b, n ** 3)

def cubiceaseout(a, b, n):
    k = n - 1
    return apply(a, b, (k ** 3) + 1)

def cubiceaseinout(a, b, n):
    k = 2 * n
    if k < 1:
        return apply(a, b, 0.5 * (k ** 3))
    else:
        j = k - 2
        return apply(a, b, 0.5 * ((j ** 3) + 2))

def sin(a, b, n):
    return apply(a, b, math.sin(0.5 * n * math.pi))

def apply(a, b, progress):
    difference = b - a
    return a + difference * progress

def clamp(value, bottom, top):
    return min(max(value, bottom), top)
