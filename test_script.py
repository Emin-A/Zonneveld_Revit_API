from math import sqrt, pi
import os, sys

import json


def circle_area(radius):
    if radius < 0:
        print("Invalid radius")
    return pi * radius**2


def square_root(num):
    if num < 0:
        return None
    else:
        return sqrt(num)


print(circle_area(10))
print(square_root(25))
