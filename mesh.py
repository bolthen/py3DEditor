import numpy as np
from OpenGL.GL import *
from shader import *


class Vertex:
    STRUCT_SIZE = 32

    def __init__(self, pos=np.array([], dtype=np.float32),
                 normal=np.array([], dtype=np.float32),
                 tex_coord=np.array([], dtype=np.float32)):
        self.pos = pos
        self.normal = normal
        self.tex_coord = tex_coord


class Texture:
    def __init(self, id_: int, type_: str):
        self.id = id_
        self.type = type_


class Mesh:
    def __init__(self, vertices: np.ndarray, indices: np.ndarray):
        '''
        :param vertices: format 'T2F_N3F_V3F'
        '''
        self.vertices = vertices
        self.indices = indices
        self.VAO = self.VBO = self.EBO = None
        self._init_buffers()

    def _init_buffers(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                              3 * self.vertices.itemsize,
                              ctypes.c_void_p(0))

        glEnableVertexAttribArray(0)

        glBindVertexArray(0)

        '''
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        glBufferData(GL_ARRAY_BUFFER, self.vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE,
                              8 * self.vertices.itemsize,
                              ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE,
                              8 * self.vertices.itemsize,
                              ctypes.c_void_p(2 * self.vertices.itemsize))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE,
                              8 * self.vertices.itemsize,
                              ctypes.c_void_p(5 * self.vertices.itemsize))
        glBindVertexArray(0)'''

        '''
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, Vertex.STRUCT_SIZE,
                              ctypes.c_void_p(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, Vertex.STRUCT_SIZE,
                              ctypes.c_void_p(3 * self.vertices.itemsize))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, Vertex.STRUCT_SIZE,
                              ctypes.c_void_p(6 * self.vertices.itemsize))
        '''

    def draw(self, shader: Shader):
        glUseProgram(shader.program)

        glBindVertexArray(self.VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, 0)
        glBindVertexArray(0)

