import math
import numpy as np


def translate(pos):
    tx, ty, tz = pos
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [tx, ty, tz, 1]
    ])


def rotate_x(a):
    m22 = math.cos(a)
    m23 = math.sin(a)
    m32 = -math.sin(a)
    m33 = math.cos(a)
    return np.array([
        [1, 0, 0, 0],
        [0, m22, m23, 0],
        [0, m32, m33, 0],
        [0, 0, 0, 1]
    ])


def rotate_y(a):
    m11 = math.cos(a)
    m13 = -math.sin(a)
    m31 = math.sin(a)
    m33 = math.cos(a)
    return np.array([
        [m11, 0, m13, 0],
        [0, 1, 0, 0],
        [m31, 0, m33, 0],
        [0, 0, 0, 1]
    ])


def rotate_z(a):
    m11 = math.cos(a)
    m12 = math.sin(a)
    m21 = -math.sin(a)
    m22 = math.cos(a)
    return np.array([
        [m11, m12, 0, 0],
        [m21, m22, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])


def scale(n):
    return np.array([
        [n, 0, 0, 0],
        [0, n, 0, 0],
        [0, 0, n, 0],
        [0, 0, 0, 1]
    ])