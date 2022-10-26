import math
import numpy as np
import wx

from shader import Shader
from object.vertex import Vertex
from mesh import Material, Mesh, Texture, MeshCustomObject
from object.base_object import BaseObject
from ui.obj_panels.sphere_panel import SpherePanelsCreator


class Sphere(BaseObject):
    def __init__(self, radius: float, sector_count: int, stack_count: int,
                 start_pos: list, shader: Shader, texture_name='', scale=1,
                 should_flip_texture=False):
        super().__init__(start_pos, shader, scale)
        self.radius = radius
        self.n_sectors = sector_count
        self.n_stacks = stack_count
        self.vertices = []
        self.texture = Texture(0, texture_name, should_flip_texture)
        self.generate()

    def get_obj_name(self):
        return "sphere"

    def generate(self):
        sector_step = 2 * math.pi / self.n_sectors
        stack_step = math.pi / self.n_stacks
        vertices = []
        self.vertices = []
        self.meshes = []

        for st in range(self.n_stacks + 1):
            stack_angle = math.pi / 2 - st * stack_step
            xy = self.radius * math.cos(stack_angle)
            z = self.radius * math.sin(stack_angle)
            for sec in range(self.n_sectors + 1):
                sector_angle = sec * sector_step

                x = xy * math.cos(sector_angle)
                y = xy * math.sin(sector_angle)

                vertices.append(self._get_vertex(x, y, z, sec, st))

        self._vertices_to_triangles(vertices)

    def _get_vertex(self, x, y, z, sec, st) -> Vertex:
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

        return vert

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

        material = Material(self.vertices, 0, texture=self.texture)
        self._add_mesh(material)

    def _add_mesh(self, material: Material):
        self.meshes.append(Mesh([material], np.array([])))

    def _add_vertex_by_idx(self, vertices, idx1, idx2, idx3):
        if max(idx1, idx2, idx3) >= len(vertices):
            return
        self.vertices += vertices[idx1].to_opengl_texture_format()
        self.vertices += vertices[idx2].to_opengl_texture_format()
        self.vertices += vertices[idx3].to_opengl_texture_format()

    def get_settings_panels(self, panel: wx, sizer: wx.BoxSizer) -> list:
        panels = SpherePanelsCreator(self).get_obj_gui_panels(panel, sizer)
        return panels


class ColorSphere(Sphere):
    def __init__(self, radius: float, sector_count: int, stack_count: int,
                 start_pos: list, shader: Shader, color: list):
        # color: RGB 0-255
        self.color = color
        super().__init__(radius, sector_count, stack_count, start_pos, shader)
        self.wireframe = True

    def _get_vertex(self, x, y, z, sec, st) -> Vertex:
        vert = super(ColorSphere, self)._get_vertex(x, y, z, sec, st)
        vert.red = self.color[0]
        vert.green = self.color[1]
        vert.blue = self.color[2]
        return vert

    def _add_mesh(self, material: Material):
        mesh = MeshCustomObject(material)
        self.meshes.append(mesh)
        mesh.update_buffers()

    def _add_vertex_by_idx(self, vertices, idx1, idx2, idx3):
        if max(idx1, idx2, idx3) >= len(vertices):
            return
        self.vertices += vertices[idx1].to_opengl_color_format()
        self.vertices += vertices[idx2].to_opengl_color_format()
        self.vertices += vertices[idx3].to_opengl_color_format()
