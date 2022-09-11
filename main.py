import math

from model import *
import matrix_functions as matrices
from camera import Camera


class Game:
    def __init__(self):
        self.window_size = (1920, 1080)
        self._init_pygame()
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        self.light_model = Model('models/Light/Lamp.obj', 0.003, [10, 5, 7])
        self.model = Model('models/Tiger 131/Tiger 131.obj', scale=3)
        # self.model = Model('models/Eric/rp_eric_rigged_001_zup_t.obj', scale=0.3)
        # self.model = Model('models/Tiger Animal/smilodon.obj', scale=0.03)
        self.active_shader = Shader('programs/vertex_shader.glsl',
                                    'programs/fragment_shader.glsl')
        self.light_shader = Shader('programs/light_vertex.glsl',
                                   'programs/light_fragment.glsl')
        self.all_shaders = [self.active_shader, self.light_shader]
        self.active_keys = [False] * 1024
        self.camera = Camera()
        self.delta_time = 0
        self.last_frame = 0

    def run(self):
        self._update_projection_matrix()

        glClearColor(125 / 255, 125 / 255, 125 / 255, 1)
        glEnable(GL_DEPTH_TEST)
        # self.active_shader.enable_wireframe()
        self.active_shader.set_uniforms(lightColor=[1, 1, 1])
        self.active_shader.set_uniforms(lightPos=self.light_model.pos)

        while True:
            self._pull_events()
            self.calculate_delta_time()
            self.camera.do_movement(self.active_keys, self.delta_time)

            radius = 10.0
            camX = math.sin(pygame.time.get_ticks() / 1000) * radius
            camZ = math.cos(pygame.time.get_ticks() / 1000) * radius
            # self.light_model.set_pos(camX, 5, camZ)

            # self.active_shader.set_uniforms(lightPos=[camX, 5, camZ])

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self._update_view_matrix()

            self.model.draw(self.active_shader)
            self.light_model.draw(self.light_shader)

            pygame.display.flip()

    def calculate_delta_time(self):
        current_frame = pygame.time.get_ticks()
        self.delta_time = (current_frame - self.last_frame) / 1000
        self.last_frame = current_frame
        fps = pygame.time.Clock()
        fps.tick(144)

    def _init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode(self.window_size,
                                         pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)

    def _update_projection_matrix(self):
        matrix = self.camera.get_projection(self.aspect_ratio)
        for shader in self.all_shaders:
            shader.set_uniforms(projection=matrix)

    def _update_view_matrix(self):
        matrix = self.camera.get_view_matrix()
        for shader in self.all_shaders:
            shader.set_uniforms(view=matrix, viewPos=self.camera.pos)

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
