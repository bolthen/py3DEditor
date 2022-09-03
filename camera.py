import math

import numpy as np
import pygame
import matrix_functions as matrices

from pyrr import Matrix44


class Camera:
    FOV_MIN = 1
    FOV_MAX = 140

    def __init__(self,
                 start_view=np.array([0, 0, -1], dtype=np.float32),
                 start_pos=np.array([0, 0, 3], dtype=np.float32),
                 ):
        self.view_dir = start_view
        self.pos = start_pos
        self.up = np.array([0, 1, 0], dtype=np.float32)
        self.yaw = -90
        self.pitch = 0
        self.mouse_sensitivity = 0.03
        self.wheel_sensitivity = 3
        self._fov = 45

    @property
    def fov(self):
        return self._fov

    @fov.setter
    def fov(self, value):
        self._fov = int(self._clamp(value, self.FOV_MIN, self.FOV_MAX))

    def get_view_matrix(self):
        # return matrices.look_at(self.pos, self.pos + self.view_dir, self.up)
        return Matrix44.look_at(self.pos, self.pos + self.view_dir, self.up,
                                dtype='f4')

    def get_projection(self, aspect, min_distance=0.1, max_distance=100):
        # return matrices.perspective(fov, int(aspect),
        #                             min_distance, max_distance)
        return Matrix44.perspective_projection(self.fov, int(aspect),
                                               min_distance,
                                               max_distance, 'f4')

    def do_movement(self, active_keys, delta_time):
        camera_speed = 0.001

        if active_keys[pygame.K_w % 1024]:
            self.pos += camera_speed * self.view_dir * delta_time
        if active_keys[pygame.K_s % 1024]:
            self.pos -= camera_speed * self.view_dir * delta_time
        if active_keys[pygame.K_q % 1024]:
            self.pos += camera_speed * \
                        np.array([0, -1, 0], dtype=np.float32) * delta_time
        if active_keys[pygame.K_e % 1024]:
            self.pos += camera_speed * \
                        np.array([0, 1, 0], dtype=np.float32) * delta_time
        if active_keys[pygame.K_a % 1024]:
            self.pos -= matrices.normalize_vec(
                np.cross(self.view_dir, self.up)) * camera_speed * delta_time
        if active_keys[pygame.K_d % 1024]:
            self.pos += matrices.normalize_vec(
                np.cross(self.view_dir, self.up)) * camera_speed * delta_time

    def do_mouse_movement(self, x_offset, y_offset):
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        self._angle_normalized()
        self._update_view_vectors()

    def _update_view_vectors(self):
        yaw_radians = math.radians(self.yaw)
        pitch_radians = math.radians(self.pitch)
        self.view_dir = matrices.normalize_vec(np.array([
            math.cos(yaw_radians) * math.cos(pitch_radians),
            math.sin(pitch_radians),
            math.sin(yaw_radians) * math.cos(pitch_radians)
        ], dtype=np.float32))

    def _angle_normalized(self):
        self.yaw %= 360
        if self.yaw > 180:
            self.yaw -= 360
        if self.yaw < -180:
            self.yaw += 360

        self.pitch = self._clamp(self.pitch, -89.0, 89.0)

    @staticmethod
    def _clamp(value, min_v, max_v):
        if value < min_v:
            value = min_v
        if value > max_v:
            value = max_v
        return value
