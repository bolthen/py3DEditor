import math

import numpy as np
import wx

import matrix_functions as matrices

from mesh import Material, Mesh
from shader import Shader
from ui.obj_panels.panels_creator import ObjectPanelsCreator
from ui.obj_panels.sphere_settings import SpherePanelsCreator

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
    def _compute_transform(change_func):
        def new_func(self, *args, **kwargs):
            change_func(self, *args, **kwargs)
            self._calculate_transform_matrix()

        return new_func

    def __init__(self, pos: list, shader: Shader, scale=1):
        self.meshes = []
        self.wireframe = False
        self.scale = scale
        self.shader = shader
        self.transform = None
        self.pos = np.array(pos, dtype=np.float32)
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self._calculate_transform_matrix()

    def draw(self):
        if self.wireframe:
            self.shader.enable_wireframe()
        else:
            self.shader.disable_wireframe()
        self.shader.set_uniforms(model=self.transform)
        for mesh in self.meshes:
            mesh.draw(self.shader)

    def _calculate_transform_matrix(self):
        self.transform = \
            matrices.scale(self.scale) @ \
            matrices.rotate_y(self.pitch) @ \
            matrices.rotate_x(self.yaw) @ \
            matrices.rotate_z(self.roll) @ \
            matrices.translate(self.pos[0], self.pos[1], self.pos[2])

    def get_obj_name(self):
        return "Unknown"

    @_compute_transform
    def translate(self, tx, ty, tz):
        self.pos += np.array([tx, ty, tz], dtype=np.float32)

    @_compute_transform
    def set_pos(self, x, y, z):
        self.pos = np.array([x, y, z], dtype=np.float32)

    @_compute_transform
    def set_x_rotation(self, degree):
        self.yaw = degree

    @_compute_transform
    def set_y_rotation(self, degree):
        self.pitch = degree

    @_compute_transform
    def set_z_rotation(self, degree):
        self.roll = degree

    @_compute_transform
    def set_scale(self, value):
        self.scale = value

    def get_settings_panels(self, panel: wx, sizer: wx.BoxSizer) -> list:
        base_panels = ObjectPanelsCreator(self).get_obj_gui_panels(panel,
                                                                   sizer)
        return base_panels


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
                 start_pos: list, shader: Shader, texture_name='', scale=1,
                 should_flip_texture=False):
        super().__init__(start_pos, shader, scale)
        self.radius = radius
        self.n_sectors = sector_count
        self.n_stacks = stack_count
        self.vertices = []
        self.texture = texture_name
        self.texture_flipped = should_flip_texture
        self.generate()

    def get_obj_name(self):
        return "sphere"

    def generate(self):
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

        material = Material(self.vertices, 0, self.texture,
                            self.texture_flipped)
        self.meshes.append(Mesh([material], np.array([])))

    def _add_vertex_by_idx(self, vertices, idx1, idx2, idx3):
        if max(idx1, idx2, idx3) >= len(vertices):
            return
        self.vertices += vertices[idx1].to_opengl_format()
        self.vertices += vertices[idx2].to_opengl_format()
        self.vertices += vertices[idx3].to_opengl_format()

    def get_settings_panels(self, panel: wx, sizer: wx.BoxSizer) -> list:
        panels = SpherePanelsCreator(self).get_obj_gui_panels(panel, sizer)
        return panels
