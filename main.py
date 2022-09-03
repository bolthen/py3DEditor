import math
import pygame
import numpy as np
import shapes
from shader import Shader
from OpenGL.GL import *
import matrix_functions as matrices
from camera import Camera


class Game:
    def __init__(self):
        self.window_size = (1920, 1080)
        self._init_pygame()
        self.aspect_ratio = int(self.window_size[0] / self.window_size[1])
        self.vao_buffer = glGenVertexArrays(1)
        self.vbo_buffer = glGenBuffers(1)
        self.ebo_buffer = glGenBuffers(1)
        # self._move_triangle_to_vao_buffer()
        # self._move_rect_to_vao()
        # self._move_cube_to_vao()
        # self._move_object_from_file_to_vao('Tiger.obj')
        self._move_object_from_file_to_vao('models/Tiger.obj')
        self.active_shader = self.shader_program = \
            Shader('programs/vertex_shader.glsl',
                   'programs/fragment_shader.glsl')
        self.active_keys = [False] * 1024
        self.camera = Camera()
        self.delta_time = 0
        self.last_frame = 0

    def run(self):
        self._update_projection_matrix()

        glClearColor(200 / 255, 200 / 255, 200 / 255, 1)
        glEnable(GL_DEPTH_TEST)
        self.active_shader.enable_wireframe()

        # face_texture = self._load_texture('textures/awesomeface.png')
        # bricks_texture = self._load_texture('textures/container.jpg')

        while True:
            self._pull_events()
            self.calculate_delta_time()
            self.camera.do_movement(self.active_keys, self.delta_time)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glBindVertexArray(self.vao_buffer)

            # self._set_textures([bricks_texture, face_texture])
            self.active_shader.set_uniforms(view=self.camera.get_view_matrix())

            '''for i, pos in enumerate(shapes.cubes_model_pose):
                k = pygame.time.get_ticks() / 100
                offsets = shapes.cubes_model_pose
                self.active_shader.set_uniforms(
                    model=matrices.rotate_x(i * k) @
                          matrices.rotate_y(i * k) @
                          matrices.rotate_z(i * k) @
                          matrices.translate(offsets[i][0],
                                             offsets[i][1],
                                             offsets[i][2]))
                glDrawArrays(GL_TRIANGLES, 0, 36)
            '''
            self.active_shader.set_uniforms(model=matrices.scale(3))
            glDrawElements(GL_TRIANGLES, 150000, GL_UNSIGNED_INT, None)

            glBindVertexArray(0)

            pygame.display.flip()

    def _update_projection_matrix(self):
        self.active_shader.set_uniforms(
            projection=self.camera.get_projection(self.aspect_ratio))

    def _move_object_from_file_to_vao(self, filename):
        vertex, faces = [], []
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertex.append([float(i) for i in line.split()[1:]])
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces.append(
                        [int(face_.split('/')[0]) - 1 for face_ in faces_])

        vertices = np.array([np.array(v) for v in vertex], dtype=np.float32)
        indices = np.array([np.array(face) for face in faces], dtype=np.uint32)
        vertices[(vertices > 2) | (vertices < -2)] = 0
        vertices = np.concatenate(vertices)
        indices = np.concatenate(indices)
        # vertices = shapes.rect
        # indices = shapes.rect_indices
        # vertices = shapes.rect2
        # indices = shapes.rect_indices

        glBindVertexArray(self.vao_buffer)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_buffer)
        glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo_buffer)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize,
                              ctypes.c_void_p(0))

        glEnableVertexAttribArray(0)

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

    def calculate_delta_time(self):
        current_frame = pygame.time.get_ticks()
        self.delta_time = (current_frame - self.last_frame) / 1000
        self.last_frame = current_frame

    def _set_textures(self, textures: list):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, textures[0])
        glUniform1i(glGetUniformLocation(self.active_shader.program,
                                         "firstTexture"), 0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glUniform1i(glGetUniformLocation(self.active_shader.program,
                                         "secondTexture"), 1)

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

    def _init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode(self.window_size,
                                         pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_WHEELDOWN:
                    self.camera.fov += self.camera.wheel_sensitivity
                elif event.button == pygame.BUTTON_WHEELUP:
                    self.camera.fov -= self.camera.wheel_sensitivity
                self._update_projection_matrix()
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
