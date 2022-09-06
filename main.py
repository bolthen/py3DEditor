from model import *
import matrix_functions as matrices
from camera import Camera


class Game:
    def __init__(self):
        self.window_size = (1920, 1080)
        self._init_pygame()
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        self.model = Model('models/Eric/rp_eric_rigged_001_zup_t.obj')
        # self.model = Model('models/Eric/rp_eric_rigged_001_zup_t.obj')
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
        # self.active_shader.enable_wireframe()

        while True:
            self._pull_events()
            self.calculate_delta_time()
            self.camera.do_movement(self.active_keys, self.delta_time)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            self.active_shader.set_uniforms(view=self.camera.get_view_matrix())
            self.active_shader.set_uniforms(model=matrices.scale(0.3) @ matrices.rotate_x(90))

            self.model.draw(self.active_shader)

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
        self.active_shader.set_uniforms(
            projection=self.camera.get_projection(self.aspect_ratio))

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
