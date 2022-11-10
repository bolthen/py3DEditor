import numpy as np

from object.uiline import UiLine
from utilities import matrix_functions as matrices
from utilities.shader import Shader


class Axes:
    def __init__(self, shader: Shader):
        self.shader = shader
        self.lines = []
        self.transform = np.eye(4, dtype=np.float32)
        self._init_lines()

    def _init_lines(self) -> None:
        x = UiLine([0, 0, 0], [1, 0, 0], self.shader, [255, 0, 0])
        y = UiLine([0, 0, 0], [0, 1, 0], self.shader, [0, 255, 0])
        z = UiLine([0, 0, 0], [0, 0, -1], self.shader, [0, 0, 255])
        self.lines += [x, y, z]

    def set_rotation(self, x, y, z):
        self.transform = \
            matrices.scale(0.15) @ \
            matrices.rotate_z(z) @ \
            matrices.rotate_y(y) @ \
            matrices.rotate_x(x)

    def draw(self) -> None:
        for line in self.lines:
            line.draw(self.transform)
