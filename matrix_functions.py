import math
import numpy as np


def translate(tx, ty, tz):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [tx, ty, tz, 1]
    ], dtype=np.float32)


def rotate_x(degree):
    a = math.radians(degree)
    m22 = math.cos(a)
    m23 = -math.sin(a)
    m32 = math.sin(a)
    m33 = math.cos(a)
    return np.array([
        [1, 0, 0, 0],
        [0, m22, m23, 0],
        [0, m32, m33, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def rotate_y(degree):
    a = math.radians(degree)
    m11 = math.cos(a)
    m13 = math.sin(a)
    m31 = -math.sin(a)
    m33 = math.cos(a)
    return np.array([
        [m11, 0, m13, 0],
        [0, 1, 0, 0],
        [m31, 0, m33, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def rotate_z(degree):
    a = math.radians(degree)
    m11 = math.cos(a)
    m12 = -math.sin(a)
    m21 = math.sin(a)
    m22 = math.cos(a)
    return np.array([
        [m11, m12, 0, 0],
        [m21, m22, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def rotate_axis(degree, x, y, z):
    maxx = max(x, y, z)
    x = x / maxx
    y = y / maxx
    z = z / maxx
    a = math.radians(degree)
    cosa = math.cos(a)
    sina = math.sin(a)
    m11 = x*x * (1 - cosa) + 1 * cosa
    m22 = y*y * (1 - cosa) + 1 * cosa
    m33 = z*z * (1 - cosa) + 1 * cosa
    m12 = x*y * (1 - cosa) - z * sina
    m13 = x*z * (1 - cosa) + y * sina
    m21 = x*y * (1 - cosa) + z * sina
    m23 = y*z * (1 - cosa) - x * sina
    m31 = x*z * (1 - cosa) - y * sina
    m32 = y*z * (1 - cosa) + x * sina
    m14 = m24 = m34 = 0
    m41 = m42 = m43 = 0
    m44 = 1
    return np.array([
        [m11, m12, m13, m14],
        [m21, m22, m23, m24],
        [m31, m32, m33, m34],
        [m41, m42, m43, m44]
    ], dtype=np.float32)


def scale(n):
    return np.array([
        [n, 0, 0, 0],
        [0, n, 0, 0],
        [0, 0, n, 0],
        [0, 0, 0, 1]
    ], dtype=np.float32)


def perspective(fov, aspect_ratio, near_plane, far_plane):
    m21 = 1.0 / np.tan(fov / 2.0)
    m11 = m21 / aspect_ratio
    m33 = far_plane / (near_plane - far_plane)
    m43 = (near_plane * far_plane) / (near_plane - far_plane)

    return np.array([
        [m11, 0.0, 0.0, 0.0],
        [0.0, m21, 0.0, 0.0],
        [0.0, 0.0, m33, -1.0],
        [0.0, 0.0, m43, 0.0]
    ], dtype=np.float32)


def orthographic(left, right, bottom, top, near_plane, far_plane):
    m11 = 2 / (right - left)
    m14 = - ((right + left) / (right - left))
    m22 = 2 / (top - bottom)
    m24 = -((top + bottom) / (top - bottom))
    m33 = -2 / (far_plane - near_plane)
    m34 = - ((far_plane + near_plane) / (far_plane - near_plane))
    return np.array([
        [m11, 0.0, 0.0, m14],
        [0.0, m22, 0.0, m24],
        [0.0, 0.0, m33, m34],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)


def concatenate(matrix):
    if matrix.ndim > 1:
        return np.concatenate(matrix)
    return matrix


def look_at(pos, direction, up):
    right = np.cross(up, direction)
    return np.array([
        [right[0], right[1], right[2], 0],
        [up[0], up[1], up[2], 0],
        [direction[0], direction[1], direction[2], 0],
        [0, 0, 0, 1]
    ], dtype=np.float32) @ np.array([
        [1, 0, 0, -pos[0]],
        [0, 1, 0, -pos[1]],
        [0, 0, 1, -pos[2]],
        [0, 0, 0, 1]
    ], dtype=np.float32)
