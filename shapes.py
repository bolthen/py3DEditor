import math

import numpy as np
import matrix_functions as matrices

from mesh import Material, Mesh
from shader import Shader

cube = np.array([
    -0.5, -0.5, -0.5, 0.0, 0.0,
    0.5, -0.5, -0.5, 1.0, 0.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    -0.5, 0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 0.0,

    -0.5, -0.5, 0.5, 0.0, 0.0,
    0.5, -0.5, 0.5, 1.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 1.0,
    0.5, 0.5, 0.5, 1.0, 1.0,
    -0.5, 0.5, 0.5, 0.0, 1.0,
    -0.5, -0.5, 0.5, 0.0, 0.0,

    -0.5, 0.5, 0.5, 1.0, 0.0,
    -0.5, 0.5, -0.5, 1.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,
    -0.5, -0.5, 0.5, 0.0, 0.0,
    -0.5, 0.5, 0.5, 1.0, 0.0,

    0.5, 0.5, 0.5, 1.0, 0.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    0.5, -0.5, -0.5, 0.0, 1.0,
    0.5, -0.5, -0.5, 0.0, 1.0,
    0.5, -0.5, 0.5, 0.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 0.0,

    -0.5, -0.5, -0.5, 0.0, 1.0,
    0.5, -0.5, -0.5, 1.0, 1.0,
    0.5, -0.5, 0.5, 1.0, 0.0,
    0.5, -0.5, 0.5, 1.0, 0.0,
    -0.5, -0.5, 0.5, 0.0, 0.0,
    -0.5, -0.5, -0.5, 0.0, 1.0,

    -0.5, 0.5, -0.5, 0.0, 1.0,
    0.5, 0.5, -0.5, 1.0, 1.0,
    0.5, 0.5, 0.5, 1.0, 0.0,
    0.5, 0.5, 0.5, 1.0, 0.0,
    -0.5, 0.5, 0.5, 0.0, 0.0,
    -0.5, 0.5, -0.5, 0.0, 1.0
], dtype=np.float32)

cubes_model_pose = [
    # np.array([0.0, 0.0, -3.0], dtype=np.float32),
    np.array([0.0, 0.0, 0.0], dtype=np.float32),
    np.array([2.0, 5.0, -15.0], dtype=np.float32),
    np.array([-1.5, -2.2, -2.5], dtype=np.float32),
    np.array([-3.8, -2.0, -12.3], dtype=np.float32),
    np.array([2.4, -0.4, -3.5], dtype=np.float32),
    np.array([-1.7, 3.0, -7.5], dtype=np.float32),
    np.array([1.3, -2.0, -2.5], dtype=np.float32),
    np.array([1.5, 2.0, -2.5], dtype=np.float32),
    np.array([1.5, 0.2, -1.5], dtype=np.float32),
    np.array([-1.3, 1.0, -1.5], dtype=np.float32)
]

rect = np.array([
    0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0,
    0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0,
    -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,
    -0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0
], dtype=np.float32)

rect2 = np.array([
    0.5, 0.5, 0.0,
    0.5, -0.5, 0.0,
    -0.5, -0.5, 0.0,
    -0.5, 0.5, 0.0
], dtype=np.float32)

rect_indices = np.array([
    0, 1, 3,
    1, 2, 3
], dtype=np.uint32)


class Object:
    def __init__(self):
        self.meshes = []

    def draw(self, shader: Shader):
        shader.set_uniforms(model=matrices.rotate_x(-90))
        for mesh in self.meshes:
            mesh.draw(shader)


class Vertex:
    def __init__(self, s=0, t=0, n1=0, n2=0, n3=0, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        self.s = s
        self.t = t
        self.n1 = n1
        self.n2 = n2
        self.n3 = n3

    def to_opengl_format(self):
        return [self.s, self.t,
                self.n1, self.n2, self.n3,
                self.x, self.y, self.z]


class Sphere(Object):
    def __init__(self, radius: int, sector_count: int, stack_count: int,
                 texture_name=''):
        super().__init__()
        self.radius = radius
        self.n_sectors = sector_count
        self.n_stacks = stack_count
        self.vertices = []
        self.texture = texture_name
        self._generate()

    def _generate(self):
        sector_step = 2 * math.pi / self.n_sectors
        stack_step = math.pi / self.n_stacks
        vertices = []

        for st in range(self.n_stacks + 1):
            stack_angle = math.pi / 2 - st * stack_step
            xy = self.radius * math.cos(stack_angle)
            z = self.radius * math.sin(stack_angle)
            for sec in range(self.n_sectors + 1):
                sector_angle = sec * sector_step

                x = xy * math.cos(sector_angle)
                y = xy * math.sin(sector_angle)
                # T2F_N3F_V3F
                vert = Vertex()
                vert.s = sec / self.n_sectors
                vert.t = st / self.n_stacks

                vert.x = x
                vert.y = y
                vert.z = z

                vert.n1 = x / self.radius
                vert.n2 = y / self.radius
                vert.n3 = z / self.radius

                vertices.append(vert)

        self._vertices_to_triangles(vertices)

    def _vertices_to_triangles(self, vertices: list):
        for i in range(self.n_stacks + 1):
            for j in range(self.n_sectors + 1):
                idx1 = i * self.n_sectors + j
                idx2 = idx1 + self.n_sectors
                idx3 = idx2 + 1
                if i == 0:
                    self._add_vertex_by_idx(vertices, idx1, idx2, idx3)
                if i == self.n_stacks:
                    self._add_vertex_by_idx(vertices, idx1 - 1, idx1, idx2)
                else:
                    self._add_vertex_by_idx(vertices, idx1, idx2, idx3)
                    self._add_vertex_by_idx(vertices, idx1, idx1 + 1, idx3)

        material = Material(self.vertices, 0, self.texture)
        self.meshes.append(Mesh([material], np.array([])))

    def _add_vertex_by_idx(self, vertices, idx1, idx2, idx3):
        if max(idx1, idx2, idx3) >= len(vertices):
            return
        self.vertices += vertices[idx1].to_opengl_format()
        self.vertices += vertices[idx2].to_opengl_format()
        self.vertices += vertices[idx3].to_opengl_format()

