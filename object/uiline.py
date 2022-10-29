import numpy as np

from utilities.mesh import Material, MeshLine
from utilities.shader import Shader


class UiLine:
    def __init__(self, start: list, end: list, shader: Shader, color: list):
        self.start = start[:3]
        self.end = end[:3]
        self.shader = shader
        self.color = color
        self.meshes = []
        self._init_meshes()

    def _init_meshes(self) -> None:
        vertices = [self.start[0], self.start[1], self.start[2],
                        self.color[0], self.color[1], self.color[2],
                    self.end[0], self.end[1], self.end[2],
                        self.color[0], self.color[1], self.color[2]]

        material = Material(vertices, 0)
        self.meshes += [MeshLine([material])]

    def draw(self, transform: np.ndarray) -> None:
        self.shader.set_uniforms(model=transform)
        for mesh in self.meshes:
            mesh.draw(self.shader)
