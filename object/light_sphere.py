import wx
import numpy as np

from object.sphere import Sphere
from ui.obj_panels.light_sphere_panel import LightSpherePanelsCreator
from utilities.mesh import Material, MeshLightObject
from utilities.shader import Shader


class LightSphere(Sphere):
    def __init__(self, start_pos: list, shader: Shader, color: list):
        super().__init__(1.5, 20, 20, start_pos, shader)
        self._colour = color

    @property
    def colour(self):
        return [self._colour[0] / 255,
                self._colour[1] / 255,
                self._colour[2] / 255]

    @colour.setter
    def colour(self, value):
        self._colour = value
        self.shader.set_uniforms(lightColor=np.array(self._colour) / 255)

    def _add_mesh(self, material: Material):
        self.meshes.append(MeshLightObject([material], np.array([])))

    def _add_vertex_by_idx(self, vertices, idx1, idx2, idx3):
        if max(idx1, idx2, idx3) >= len(vertices):
            return
        self.vertices += vertices[idx1].to_opengl_coord_format()
        self.vertices += vertices[idx2].to_opengl_coord_format()
        self.vertices += vertices[idx3].to_opengl_coord_format()

    def get_settings_panels(self, panel: wx, sizer: wx.BoxSizer) -> list:
        panels = LightSpherePanelsCreator(self).get_obj_gui_panels(panel,
                                                                   sizer)
        return panels

    def get_obj_name(self) -> str:
        return "Light"
