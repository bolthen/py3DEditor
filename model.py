from pywavefront import *

from mesh import *
from shapes import Object
from matrix_functions import concatenate

import numpy as np
from pathlib import Path


class Model(Object):
    def __init__(self, path: Path, start_pos: list, shader: Shader, scale=1):
        super().__init__(start_pos, shader, scale)
        self.path = path
        self.scene = None
        self._load_model()

    def _load_model(self):
        self.scene = Wavefront(self.path, collect_faces=True,
                               create_materials=True)
        self._load_meshes()

    def _load_meshes(self):
        for mesh in self.scene.mesh_list:
            materials = []
            for i, material in enumerate(mesh.materials):
                texture_name = ''
                if material.texture is not None:
                    texture_name = self.path.parent / material.texture.file_name
                mat = Material(material.vertices, i, texture_name)
                materials.append(mat)

            self.meshes.append(
                Mesh(materials,
                     concatenate(np.array(mesh.faces, dtype=np.uint32))))

    def get_obj_name(self):
        return self.path
