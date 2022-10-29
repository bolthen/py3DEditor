import wx

from pathlib import Path
from camera import Camera
from object.axes import Axes
from object.custom import CustomObject
from object.model import Model
from object.sphere import Sphere, ColorSphere
from utilities.shader import Shader
from collections import deque


class ModelsHandler:
    def __init__(self, camera: Camera):
        self.objects = []
        self.temple_objects = deque()
        self.camera = camera
        self.all_shaders = []
        self.model_shader = None
        self.light_shader = None
        self.custom_shader = None
        self.axis_shader = None
        self._active_custom_obj = None
        self.axes = None

    def init_shaders(self) -> None:
        shaders_location = Path(__file__).parent / 'opengl_shaders'
        self.model_shader = Shader(shaders_location / 'vertex_shader.glsl',
                                   shaders_location / 'fragment_shader.glsl')
        self.light_shader = Shader(shaders_location / 'light_vertex.glsl',
                                   shaders_location / 'light_fragment.glsl')
        self.custom_shader = Shader(shaders_location / 'custom_vertex.glsl',
                                    shaders_location / 'custom_fragment.glsl')
        self.axis_shader = Shader(shaders_location / 'axis_vertex.glsl',
                                  shaders_location / 'axis_fragment.glsl')

        self.all_shaders += [self.model_shader, self.light_shader,
                             self.custom_shader, self.axis_shader]

        self.axes = Axes(self.axis_shader)
        # TODO setting light pos and light color

    def open_new_model(self, path: Path) -> Model:
        start_pos = self.camera.pos + self.camera.view_dir * 5
        model = Model(path, start_pos, self.model_shader)
        self.objects.append(model)
        return model

    def create_new_sphere(self, texture: Path) -> Sphere:
        start_pos = self.camera.pos + self.camera.view_dir * 10
        sphere = Sphere(5, 50, 50, start_pos, self.model_shader, texture)
        self.objects.append(sphere)
        return sphere

    def create_new_mark(self, pos: list, colour: list) -> ColorSphere:
        return ColorSphere(0.5, 10, 10, pos, self.custom_shader, colour)

    def create_new_custom(self) -> CustomObject:
        start_pos = self.camera.pos + self.camera.view_dir * 5
        obj = CustomObject(start_pos, self.custom_shader)
        self._active_custom_obj = obj
        self.objects.append(obj)
        return obj

    def add_new_vertex_to_custom_obj(self, colour: wx.Colour) -> None:
        if self._active_custom_obj is None:
            raise Exception()
        start_pos = self.camera.pos + self.camera.view_dir * 5
        self._active_custom_obj.add_new_vertex(start_pos, colour)
        self.temple_objects.append(self.create_new_mark(start_pos,
                                                        [colour.red,
                                                         colour.green,
                                                         colour.blue]))
        if len(self.temple_objects) > 2:
            self.temple_objects.popleft()

    def finish_object_creation(self) -> CustomObject:
        if self._active_custom_obj is None:
            raise Exception()
        obj = self._active_custom_obj
        self._active_custom_obj = None
        self.temple_objects.clear()
        return obj

    def draw_all_objects(self) -> None:
        self.model_shader.set_uniforms(lightColor=[1, 1, 1],
                                       lightPos=self.camera.pos)
        for obj in self.objects:
            obj.draw()
        for obj in self.temple_objects:
            obj.draw()
        self.axes.draw()

    def get_objs_names(self) -> list:
        return [i.get_obj_name() for i in self.objects]
