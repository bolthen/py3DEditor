from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
from matrix_functions import concatenate


class ShaderException(Exception):
    def __init__(self, message, shader=None, is_shader_program=False):
        info_log = ''
        if shader is not None:
            if is_shader_program:
                info_log = glGetProgramInfoLog(shader, 512, None)
            else:
                info_log = glGetShaderInfoLog(shader, 512, None)
        super().__init__(message + ': ' + info_log)
        glDeleteShader(shader)


class Shader:
    def __init__(self, vertex_path: str, fragment_path: str):
        self.program = self._load_program(vertex_path, fragment_path)
        self._uniform_to_location = self._get_uniforms_locations()

        self.use()

    def use(self):
        glUseProgram(self.program)

    def set_uniforms(self, **kwargs):
        """
        'time' - current_time
        'resolution' - resolution of window
        'model' - object's world position\n
        'projection' - camera FOV: perspective or orthographic\n
        'view' - view_matrix
        """
        if 'time' in kwargs.keys():
            glUniform1f(self._uniform_to_location['time'],
                        kwargs['time'])

        if 'resolution' in kwargs.keys():
            glUniform2f(self._uniform_to_location['resolution'],
                        kwargs['resolution'][0], kwargs['resolution'][1])

        if 'projection' in kwargs.keys():
            glUniformMatrix4fv(self._uniform_to_location['projection'], 1,
                               GL_FALSE, concatenate(kwargs['projection']))

        if 'model' in kwargs.keys():
            glUniformMatrix4fv(self._uniform_to_location['model'], 1,
                               GL_FALSE, concatenate(kwargs['model']))

        if 'view' in kwargs.keys():
            glUniformMatrix4fv(self._uniform_to_location['view'], 1,
                               GL_FALSE, concatenate(kwargs['view']))

    @staticmethod
    def _load_program(vertex_path: str, fragment_path: str):
        program = None
        try:
            with open(vertex_path, mode='r', encoding='UTF-8') as vertex_src, \
                    open(fragment_path, 'r') as fragment_src:

                vertex = compileShader(vertex_src.read(), GL_VERTEX_SHADER)
                if glGetShaderiv(vertex, GL_COMPILE_STATUS) is False:
                    raise ShaderException('Vertex Shader Error', vertex)

                fragment = compileShader(fragment_src.read(),
                                         GL_FRAGMENT_SHADER)
                if glGetShaderiv(fragment, GL_COMPILE_STATUS) is False:
                    raise ShaderException('Fragment Shader Error', fragment)

                program = compileProgram(vertex, fragment)
                if glGetProgramiv(program, GL_LINK_STATUS) is False:
                    raise ShaderException('Compile Shader Program Failed',
                                          program, True)

                glDeleteShader(vertex)
                glDeleteShader(fragment)

        except FileNotFoundError as exception:
            raise ShaderException(f'Shader program {exception.filename} '
                                  f'not found')

        return program

    def _get_uniforms_locations(self) -> dict:
        form2pos = {
            'time': glGetUniformLocation(self.program,
                                         'time'),
            'resolution': glGetUniformLocation(self.program,
                                               'resolution'),
            'view': glGetUniformLocation(self.program,
                                         'view'),
            'model': glGetUniformLocation(self.program,
                                          'model'),
            'projection': glGetUniformLocation(self.program,
                                               'projection')
        }

        return form2pos

    @staticmethod
    def enable_wireframe():
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    @staticmethod
    def disable_wireframe():
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
