import math
import threading

import pygame
import shapes
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import matrix_functions as matrices
from matrix_functions import concatenate
from pyrr import Matrix44
from camera import Camera

vertex_shader_src = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec2 textureCoord;

out vec3 ourColor;
out vec2 ourTextureCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * view * model * vec4(position, 1.0f);
    ourColor = color;
    ourTextureCoord = textureCoord;
}
"""

fragment_shader_src = """
#version 330 core

out vec4 color;

in vec3 ourColor;
in vec2 ourTextureCoord;

uniform sampler2D firstTexture;
uniform sampler2D secondTexture;
uniform vec2 resolution;
uniform float time;

void main()
{
    color = mix(texture(firstTexture, ourTextureCoord),
                texture(secondTexture, ourTextureCoord),
                0.2f);
}
"""


class Game:
    def __init__(self):
        self.window_size = (1920, 1080)
        self.aspect_ratio = int(self.window_size[0] / self.window_size[1])
        self._init_pygame()
        self.vao_buffer = glGenVertexArrays(1)
        self.vbo_buffer = glGenBuffers(1)
        self.ebo_buffer = glGenBuffers(1)
        # self._move_triangle_to_vao_buffer()
        # self._move_rect_to_vao()
        self._move_cube_to_vao()
        self.active_shaders = self.shader_program = self._create_shaders()
        self.uniform_to_location = self._get_uniforms_locations()
        self.active_keys = [False] * 1024
        self.camera = Camera()
        self.delta_time = 0
        self.last_frame = 0

    def run(self):
        self._set_transform_matrices(
            projection=self.camera.get_projection(self.aspect_ratio, 80))

        glClearColor(200 / 255, 200 / 255, 200 / 255, 1)
        glEnable(GL_DEPTH_TEST)
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

        face_texture = self._load_texture('textures/awesomeface.png')
        bricks_texture = self._load_texture('textures/container.jpg')

        while True:
            # self.mouse_last_pos = mouse_new_pos

            self._pull_events()
            self.calculate_delta_time()
            self.camera.do_movement(self.active_keys, self.delta_time)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glBindVertexArray(self.vao_buffer)

            self._set_textures([bricks_texture, face_texture])
            self._set_uniforms()
            self._set_transform_matrices(view=self.camera.get_view_matrix())

            for i, pos in enumerate(shapes.cubes_model_pose):
                k = pygame.time.get_ticks() / 100
                offsets = shapes.cubes_model_pose
                self._set_transform_matrices(
                    model=matrices.rotate_x(i * k) @
                          matrices.rotate_y(i * k) @
                          matrices.rotate_z(i * k) @
                          matrices.translate(offsets[i][0],
                                             offsets[i][1],
                                             offsets[i][2]))
                glDrawArrays(GL_TRIANGLES, 0, 36)

            # glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

            glBindVertexArray(0)

            pygame.display.flip()

    def calculate_delta_time(self):
        current_frame = pygame.time.get_ticks()
        self.delta_time = current_frame - self.last_frame
        self.last_frame = current_frame

    @staticmethod
    def _get_look_at_matrix():
        radius = 10
        cam_x = math.sin(pygame.time.get_ticks() / 1000) * radius
        cam_z = math.cos(pygame.time.get_ticks() / 1000) * radius
        return Matrix44.look_at([cam_x, 0, cam_z], [0, 0, 0], [0, 1, 0],
                                dtype='f4')
        # return matrices.look_at(np.array([cam_x, 0, cam_z]),
        #                          np.array([0, 0, 0]),
        #                          np.array([0, 1, 0]))

    def _set_textures(self, textures: list):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, textures[0])
        glUniform1i(glGetUniformLocation(self.active_shaders,
                                         "firstTexture"), 0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniform1i(glGetUniformLocation(self.active_shaders,
                                         "secondTexture"), 1)

    def _set_uniforms(self):
        glUniform1f(self.uniform_to_location['time'],
                    pygame.time.get_ticks() / 100)
        glUniform2f(self.uniform_to_location['resolution'],
                    self.window_size[0], self.window_size[1])

    def _set_transform_matrices(self, **kwargs):
        """
        'model' - world position\n
        'projection' - camera FOV: perspective or orthographic\n
        'view' - camera pos
        """
        if 'projection' in kwargs.keys():
            glUniformMatrix4fv(
                self.uniform_to_location['projection'], 1, GL_FALSE,
                concatenate(kwargs['projection']))

        if 'model' in kwargs.keys():
            glUniformMatrix4fv(
                self.uniform_to_location['model'], 1, GL_FALSE,
                concatenate(kwargs['model']))

        if 'view' in kwargs.keys():
            glUniformMatrix4fv(
                self.uniform_to_location['view'], 1, GL_FALSE,
                concatenate(kwargs['view']))

    def _get_uniforms_locations(self) -> dict:
        form2pos = {
            'time': glGetUniformLocation(self.active_shaders,
                                         'time'),
            'resolution': glGetUniformLocation(self.active_shaders,
                                               'resolution'),
            'view': glGetUniformLocation(self.active_shaders,
                                         'view'),
            'model': glGetUniformLocation(self.active_shaders,
                                          'model'),
            'projection': glGetUniformLocation(self.active_shaders,
                                               'projection')
        }

        return form2pos

    def _move_cube_to_vao(self):
        vertices = shapes.cube

        glBindVertexArray(self.vao_buffer)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize,
                              ctypes.c_void_p(0))
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 5 * vertices.itemsize,
                              ctypes.c_void_p(3 * vertices.itemsize))

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindVertexArray(0)

    def _move_rect_to_vao(self):
        vertices = shapes.rect
        indices = shapes.rect_indices
        glBindVertexArray(self.vao_buffer)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize,
                              ctypes.c_void_p(0))
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize,
                              ctypes.c_void_p(3 * vertices.itemsize))
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 8 * vertices.itemsize,
                              ctypes.c_void_p(6 * vertices.itemsize))

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glEnableVertexAttribArray(2)

        glBindVertexArray(0)

    def _move_triangle_to_vao_buffer(self):
        glBindVertexArray(self.vao_buffer)
        self._move_vertexes_to_vbo([
            -0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            0.0, 0.5, 0.0
        ])
        glBindVertexArray(0)

    def _move_vertexes_to_vbo(self, vertices: list):
        points = np.array(vertices, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_buffer)
        glBufferData(GL_ARRAY_BUFFER, points.nbytes, points, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, points.itemsize * 3,
                              ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

    @staticmethod
    def _create_shaders():
        vertex_shader = compileShader(vertex_shader_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader_src,
                                        GL_FRAGMENT_SHADER)
        shader_program = compileProgram(vertex_shader, fragment_shader)

        glUseProgram(shader_program)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program

    def _init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode(self.window_size,
                                         pygame.DOUBLEBUF | pygame.OPENGL)

    @staticmethod
    def enable_wireframe():
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    @staticmethod
    def disable_wireframe():
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def _load_texture(self, path: str):
        image, width, height = self._get_texture_data_by_name(path)
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
    def _get_texture_data_by_name(path: str, should_flip=True):
        texture_surface = pygame.image.load(path)
        texture_data = pygame.image.tostring(texture_surface, "RGB",
                                             should_flip)
        return (texture_data,
                texture_surface.get_width(),
                texture_surface.get_height()
                )

    def _pull_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEMOTION:
                mouse_new_pos = pygame.mouse.get_rel()
                self.camera.do_mouse_movement(mouse_new_pos[0],
                                              -mouse_new_pos[1])
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
                self.active_keys[event.key % 1024] = True
            if event.type == pygame.KEYUP:
                self.active_keys[event.key % 1024] = False

    def init_mouse(self):
        pass


if __name__ == '__main__':
    game = Game()
    game.run()

'''
import moderngl_window as mglw


class App(mglw.WindowConfig):
    resource_dir = 'programs'
    window_size = 1920, 1080

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quad = mglw.geometry.quad_fs()
        self.prog = self.load_program(vertex_shader=r"vertex_shader.glsl",
                                      fragment_shader="fragment_shader.glsl")
        self.set_uniform('resolution', self.window_size)

    def set_uniform(self, key, value):
        try:
            self.prog[key] = value
        except KeyError:
            print(f'variable \'{key}\' not found')

    def render(self, time: float, frame_time: float):
        self.ctx.clear()
        self.set_uniform('time', time)
        self.quad.render(self.prog)


if __name__ == '__main__':
    mglw.run_window_config(App)

'''

'''
from pyrr import Matrix44
import numpy

import moderngl
import moderngl_window
from base import CameraWindow


class LinesDemo(CameraWindow):
    gl_version = (3, 3)
    title = "Thick Lines"
    resource_dir = 'programs'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.mouse_exclusivity = True

        self.prog = self.load_program('lines.glsl')
        # self.prog['color'].value = (1.0, 1.0, 1.0)
        self.prog['m_model'].write(Matrix44.from_translation((0.0, 0.0, -3.5), dtype='f4'))

        N = 10
        # Create lines geometry
        def gen_lines():
            for i in range(N):
                # A
                yield -1.0
                yield 1.0 - i * 2.0 / N
                yield 0.0
                # b
                yield 1.0
                yield 1.0 - i * 2.0 / N
                yield 0.0

        buffer = self.ctx.buffer(numpy.fromiter(gen_lines(), dtype='f4', count=N * 6).tobytes())
        self.lines = self.ctx.vertex_array(
            self.prog,
            [
                (buffer, '3f', 'in_position'),
            ],
        )

    def set_uniform(self, key, value):
        try:
            self.prog[key] = value
        except KeyError:
            print(f'variable \'{key}\' not found')

    def render(self, time: float, frametime: float):
        # self.ctx.enable_only(moderngl.DEPTH_TEST)

        self.prog['m_proj'].write(self.camera.projection.matrix)
        self.prog['m_cam'].write(self.camera.matrix)
        self.lines.render(mode=moderngl.LINES)


if __name__ == '__main__':
    moderngl_window.run_window_config(LinesDemo)
'''
