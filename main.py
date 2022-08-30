import pygame
import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram


vertex_shader_src = """
#version 330 core

layout (location = 0) in vec3 position;

void main()
{
    gl_Position = vec4(position.x, position.y, position.z, 1.0);
}
"""

fragment_shader_src = """
#version 330 core

out vec4 color;

void main()
{
    color = vec4(1.0f, 0.5f, 0.2f, 1.0f);
}
"""


class Game:
    def __init__(self):
        self.window_size = (800, 600)
        self.init_pygame()
        self.vao_buffer = glGenVertexArrays(1)
        self.vbo_buffer = glGenBuffers(1)
        self.init_vao_buffer()
        self.shader_program = self.create_shaders()

    def run(self):
        glClearColor(200 / 255, 200 / 255, 200 / 255, 1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        quit()

            glBindVertexArray(self.vao_buffer)

            glClear(GL_COLOR_BUFFER_BIT)
            glDrawArrays(GL_TRIANGLES, 0, 3)

            glBindVertexArray(0)

            pygame.display.flip()

    def init_vao_buffer(self):
        glBindVertexArray(self.vao_buffer)
        self.move_triangle_to_vbo()
        glBindVertexArray(0)

    def move_triangle_to_vbo(self):
        triangles = np.array([
            -0.5, -0.5, 0.0,
            0.5, -0.5, 0.0,
            0.0, 0.5, 0.0
        ], dtype=np.float32)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo_buffer)
        glBufferData(GL_ARRAY_BUFFER, triangles.nbytes, triangles,
                     GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, triangles.itemsize * 3,
                              ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

    @staticmethod
    def create_shaders():
        vertex_shader = compileShader(vertex_shader_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_shader_src,
                                        GL_FRAGMENT_SHADER)
        shader_program = compileProgram(vertex_shader, fragment_shader)

        glUseProgram(shader_program)

        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode(self.window_size,
                                         pygame.DOUBLEBUF | pygame.OPENGL)


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