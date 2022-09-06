from pywavefront import *

from mesh import *
from shader import *
from matrix_functions import concatenate

import numpy as np


class Model:
    def __init__(self, path: str):
        self.path = str.join('/', path.split('/')[0:-1])
        self.meshes = []
        self.scene = None
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
        for mesh in self.meshes:
            mesh.draw(shader)
