import numpy as np
import wx

from utilities import matrix_functions as matrices
from utilities.shader import Shader
from ui.obj_panels.panels_creator import ObjectPanelsCreator


def _compute_transform(change_func):
    def new_func(self, *args, **kwargs):
        change_func(self, *args, **kwargs)
        self._calculate_transform_matrix()

    return new_func


class BaseObject:
    def __init__(self, pos: list, shader: Shader, scale=1):
        self.meshes = []
        self.wireframe = False
        self.scale = scale
        self.shader = shader
        self.pos = np.array(pos, dtype=np.float32)
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.transform = None
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
            matrices.rotate_z(self.roll) @ \
            matrices.rotate_y(self.pitch) @ \
            matrices.rotate_x(self.yaw) @ \
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
