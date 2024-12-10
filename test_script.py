import os, sys
import json

from math import sqrt, pi

# Path to pyrevitlib
PYREVIT_LIB_PATH = r"C:\Users\bim3d\AppData\Roaming\pyRevit-Master\pyrevitlib"
if PYREVIT_LIB_PATH not in sys.path:
    sys.path.append(PYREVIT_LIB_PATH)

# Extract environment variables
pyrevit_version = os.getenv("PYREVIT_VERSION")
cpy_version = os.getenv("PYREVIT_CPYVERSION")
ipy_version = os.getenv("PYREVIT_IPYVERSION")


# WORKS!
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
print(f"pyRevit Version: {pyrevit_version}")
print(f"CPython Version: {cpy_version}")
print(f"IronPython Version: {ipy_version}")
