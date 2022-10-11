import pathlib

import numpy as np
import wx

from pathlib import Path
from camera import Camera
from model import Model
from shader import Shader


class ModelsHandler:
    def __init__(self, camera: Camera):
        self.objects = []
        self.all_shaders = []
        self.model_shader = None
        self.light_shader = None
        self.camera = camera

    def init_shaders(self):
        shaders_location = Path(__file__).parent / 'opengl_shaders'
        self.model_shader = Shader(shaders_location / 'vertex_shader.glsl',
                                   shaders_location / 'fragment_shader.glsl')
        self.light_shader = Shader(shaders_location / 'light_vertex.glsl',
                                   shaders_location / 'light_fragment.glsl')

        self.all_shaders += [self.model_shader, self.light_shader]

        # TODO setting light pos and light color
        self.model_shader.set_uniforms(lightColor=[1, 1, 1], lightPos=[0, 0, 0])

    def open_new_model(self, path: pathlib.Path) -> Model:
        start_pos = self.camera.pos + self.camera.view_dir * 5
        model = Model(path, start_pos, self.model_shader)
        self.objects.append(model)
        return model

    def draw_all_objects(self) -> None:
        for obj in self.objects:
            obj.draw()

    def get_objs_names(self) -> list:
        return [i.get_obj_name() for i in self.objects]
