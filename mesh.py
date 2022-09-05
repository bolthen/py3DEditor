import numpy as np
import pygame
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
    def __init__(self, id_: int, texture_name: str):
        self.id = id_
        self.name = texture_name
        self.texture = self._load_texture()

    def _load_texture(self):
        image, width, height = self._get_texture_data(self.name)
        texture = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texture)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                        GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB,
                     GL_UNSIGNED_BYTE, image)

        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

        return texture

    @staticmethod
    def _get_texture_data(path: str, should_flip=False):
        texture_surface = pygame.image.load(path)
        texture_data = pygame.image.tostring(texture_surface, "RGB",
                                             should_flip)
        return (texture_data,
                texture_surface.get_width(),
                texture_surface.get_height()
                )

    def activate(self, shader: Shader, texture_var_name: str):
        glActiveTexture(GL_TEXTURE0 + self.id)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniform1i(glGetUniformLocation(shader.program, texture_var_name),
                    self.id)


class Material:
    def __init__(self, vertices: np.ndarray,
                 model_idx: int, texture_name: str):
        '''
        :param vertices: format 'T2F_N3F_V3F'
        '''

        self.vertices = vertices
        # for i in range(len(self.vertices) // 8):
        #     self.vertices[i * 8 + 1] += 1
        self.model_idx = model_idx
        self.texture = Texture(model_idx, texture_name)

    def activate_texture(self, shader: Shader, texture_var_name='mainTexture'):
        self.texture.activate(shader, texture_var_name)


class Mesh:
    def __init__(self, materials: list, indices: np.ndarray):
        self.indices = indices
        self.VAO = self.VBO = self.EBO = None
        self.materials = materials
        self._init_buffers()

    def _init_buffers(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        vertices = self._get_all_vertices()

        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)

        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize,
                              ctypes.c_void_p(0))

        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize,
                              ctypes.c_void_p(2 * vertices.itemsize))

        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize,
                              ctypes.c_void_p(5 * vertices.itemsize))

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    def _get_all_vertices(self) -> np.ndarray:
        vertices = []
        for material in self.materials:
            vertices += material.vertices

        return np.array(vertices, dtype=np.float32)

    def draw(self, shader: Shader):
        glUseProgram(shader.program)

        glBindVertexArray(self.VAO)

        current_idx = 0

        for material in self.materials:
            material.activate_texture(shader)
            step = len(material.vertices) // 8
            glDrawArrays(GL_TRIANGLES,
                         current_idx,
                         current_idx + step)
            current_idx += step

        glBindTexture(GL_TEXTURE_2D, 0)
        glBindVertexArray(0)
