from mesh import Material, MeshCustomObject
from object.base_object import BaseObject
from shader import Shader


class CustomObject(BaseObject):
    def __init__(self, start_pos: list, shader: Shader):
        super().__init__(start_pos, shader)
        self.main_material = Material([], 0)
        self.main_mesh = MeshCustomObject(self.main_material)
        self.meshes.append(self.main_mesh)
        self._n_vertices = 0

    def add_new_vertex(self, pos: list) -> None:
        # vertices: format 'C3F_N3F_V3F'
        self._n_vertices += 1
        new_vertex = [0.6, 1.0, 0.1, 0, 0, 0, pos[0], pos[1], pos[2]]
        if self._n_vertices > 3:
            new_triangle = self.main_material.vertices[-18:] + new_vertex
            self.main_material.vertices += new_triangle
        else:
            self.main_material.vertices += new_vertex

        if self._n_vertices >= 3:
            self.main_mesh.update_buffers()

    def get_obj_name(self):
        return "custom object"
