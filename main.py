import moderngl_window as mglw


fragment = """
#version 430

out vec4 fragColor;

//uniform float time;
uniform vec2 resolution;

void main()
{
    vec2 uv = (gl_FragCoord.xy - 0.5f * resolution.xy) / resolution.y;
    vec3 color = vec3(0.0);

    color += 100;

    fragColor = vec4(color, 1.0);
}
"""

vertex = """
#version 430

in vec3 in_position;

void main()
{
    gl_Position = vec4(in_position, 1);
}
"""


class App(mglw.WindowConfig):
    resource_dir = 'programs'
    window_size = 800, 600

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quad = mglw.geometry.quad_fs()
        self.prog = self.load_program(vertex_shader=r"vertex_shader.glsl",
                                      fragment_shader="fragment_shader.glsl")
        self.frag = self.ctx.program(vertex_shader=vertex,
                                     fragment_shader=fragment)
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
