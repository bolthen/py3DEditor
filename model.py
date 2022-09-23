from pywavefront import *

from mesh import *
from shapes import Object
from matrix_functions import concatenate

import numpy as np


class Model(Object):
    def __init__(self, path: str, start_pos: list, scale=1):
        super().__init__(start_pos, scale)
        self.path = str.join('/', path.split('/')[0:-1])
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
