import wx

from camera import Camera
from threading import Lock
from models_handler import ModelsHandler


class RedactorEngine:
    def __init__(self):
        self.camera = Camera()
        self.obj_handler = ModelsHandler(self.camera)
        self.delta_time = 0
        self._time = wx.StopWatch()
        self._last_frame = 0
        self._draw_mutex = Lock()

    def init_gl(self):
        self.obj_handler.init_shaders()

    def start_cycle(self) -> None:
        self._draw_mutex.acquire()

    def on_tick(self, active_keys: list) -> None:
        self._calculate_delta_time()
        self.camera.do_movement(active_keys, self.delta_time)
        self.update_view_matrices()

    def draw_scene(self):
        self.obj_handler.draw_all_objects()

    def end_game_cycle(self) -> None:
        self._draw_mutex.release()

    def set_mouse_pos(self, offset: tuple):
        self.camera.do_mouse_movement(offset[0], offset[1])

    def change_fov(self, offset: int):
        self.camera.fov -= offset * self.camera.wheel_sensitivity // 120

    def _calculate_delta_time(self) -> None:
        current_frame = self._time.Time()
        self.delta_time = (current_frame - self._last_frame) / 1000
        self._last_frame = current_frame
        # if self.delta_time != 0:
        #     print(1 / self.delta_time)

    def update_view_matrices(self) -> None:
        matrix = self.camera.get_view_matrix()
        for shader in self.obj_handler.all_shaders:
            shader.set_uniforms(view=matrix, viewPos=self.camera.pos)

    def update_projection_matrix(self, aspect_ratio) -> None:
        matrix = self.camera.get_projection(aspect_ratio)
        for shader in self.obj_handler.all_shaders:
            shader.set_uniforms(projection=matrix)
