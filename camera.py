import math

import numpy as np
import pygame
import matrix_functions as matrices

from pyrr import Matrix44


class _MovementSystem:
    def __init__(self, resistance_force=0.05, mass=80, speed=10):
        self._mass = mass
        self._resistance = resistance_force
        self._speed = speed
        self.velocity = np.array([0, 0, 0], dtype=np.float32)

    def get_velocity(self, view_dir: np.ndarray, active_keys) -> np.ndarray:
        force = self._get_force_direction(view_dir, active_keys) / self._mass
        self.velocity = (self.velocity + force) * (1 - self._resistance)
        return self.velocity

    def _get_force_direction(self, view_dir, active_keys) -> np.ndarray:
        direction = np.array([0, 0, 0], dtype=np.float32)
        speed = self._speed

        if active_keys[pygame.K_LSHIFT % 1024]:
            speed *= 5
        if active_keys[pygame.K_w % 1024]:
            direction += np.array([view_dir[0], 0, view_dir[2]],
                                  dtype=np.float32)
        if active_keys[pygame.K_s % 1024]:
            direction -= np.array([view_dir[0], 0, view_dir[2]],
                                  dtype=np.float32)
        if active_keys[pygame.K_q % 1024]:
            direction += np.array([0, -1, 0], dtype=np.float32)
        if active_keys[pygame.K_e % 1024]:
            direction += np.array([0, 1, 0], dtype=np.float32)
        if active_keys[pygame.K_a % 1024]:
            direction -= matrices.normalize_vec(
                np.cross(view_dir, np.array([0, 1, 0], dtype=np.float32)))
        if active_keys[pygame.K_d % 1024]:
            direction += matrices.normalize_vec(
                np.cross(view_dir, np.array([0, 1, 0], dtype=np.float32)))

        return matrices.normalize_vec(direction) * speed


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
        self.movement = _MovementSystem()
        self._fov = 45

    @property
    def fov(self) -> float:
        return self._fov

    @fov.setter
    def fov(self, value: float) -> None:
        self._fov = self._clamp(value, self.FOV_MIN, self.FOV_MAX)

    def get_view_matrix(self) -> np.ndarray:
        return Matrix44.look_at(self.pos, self.pos + self.view_dir, self.up,
                                dtype='f4')

    def get_projection(self, aspect: float,
                       min_distance=0.1, max_distance=100) -> np.ndarray:
        return Matrix44.perspective_projection(
            self.fov, int(aspect), min_distance, max_distance, 'f4')

    def do_movement(self, active_keys, delta_time: float):
        self.pos += self.movement.get_velocity(
            self.view_dir, active_keys) * delta_time

    def do_mouse_movement(self, x_offset, y_offset) -> None:
        x_offset *= self.mouse_sensitivity
        y_offset *= self.mouse_sensitivity

        self.yaw += x_offset
        self.pitch += y_offset

        self._angle_normalized()
        self._update_view_vectors()

    def _update_view_vectors(self) -> None:
        yaw_radians = math.radians(self.yaw)
        pitch_radians = math.radians(self.pitch)
        self.view_dir = matrices.normalize_vec(np.array([
            math.cos(yaw_radians) * math.cos(pitch_radians),
            math.sin(pitch_radians),
            math.sin(yaw_radians) * math.cos(pitch_radians)
        ], dtype=np.float32))

    def _angle_normalized(self) -> None:
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
