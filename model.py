from pywavefront import *

from mesh import *
from shader import *
from matrix_functions import concatenate

import numpy as np
import matrix_functions as matrices


class Model:
    def __init__(self, path: str, scale=1, start_pos=None):
        self.path = str.join('/', path.split('/')[0:-1])
        self.meshes = []
        self.scene = None
        self.default_scale = scale
        if start_pos is None:
            start_pos = [0, 0, 0]
        self.transform = matrices.scale(scale) @ \
                         matrices.translate(start_pos[0],
                                            start_pos[1],
                                            start_pos[2])
        self.pos = np.array(start_pos, dtype=np.float32)
        self._load_model(path)

    def _load_model(self, path: str):
        self.scene = Wavefront(path, collect_faces=True, create_materials=True)
        self._load_meshes()

    def _load_meshes(self):
        for mesh in self.scene.mesh_list:
            materials = []
            for i, material in enumerate(mesh.materials):
                texture_name = ''
                if material.texture is not None:
                    texture_name = self.path + '/' + material.texture.file_name
                mat = Material(material.vertices, i, texture_name)
                materials.append(mat)

            self.meshes.append(
                Mesh(materials,
                     concatenate(np.array(mesh.faces, dtype=np.uint32))))

    def draw(self, shader: Shader):
        shader.set_uniforms(model=self.transform)
        for mesh in self.meshes:
            mesh.draw(shader)

    def translate(self, tx, ty, tz):
        self.pos += np.array([tx, ty, tz], dtype=np.float32)
        self.transform = matrices.translate(tx, ty, tz) @ self.transform

    def set_pos(self, x, y, z):
        self.pos = np.array([x, y, z], dtype=np.float32)
        self.transform = matrices.scale(self.default_scale) @ \
                         matrices.translate(x, y, z)
