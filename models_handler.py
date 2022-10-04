import pathlib

import wx

from camera import Camera
from model import Model
from shader import Shader


class ModelsHandler:
    def __init__(self):
        self.objects = []

    def open_new_model(self, path: pathlib.Path, camera: Camera,
                       shader: Shader) -> None:
        start_pos = camera.pos + camera.view_dir * 5
        self.objects.append(Model(path, start_pos, shader))

    def draw_all_objects(self) -> None:
        for obj in self.objects:
            obj.draw()

    def get_objs_names(self):
        return [i.get_obj_name() for i in self.objects]

