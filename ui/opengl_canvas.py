import sys
import wx

from threading import Lock
from wx import glcanvas
from camera import Camera
from models_handler import ModelsHandler
from shader import Shader
from OpenGL.GL import *
from pathlib import Path


class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent, grand_parent):
        self.window_size = (1920, 1080)
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        glcanvas.GLCanvas.__init__(self, parent, id=wx.EXPAND)
        self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        self.init = False
        self.active_keys = [False] * 1024
        self.camera = Camera()
        self.time = wx.StopWatch()
        self.delta_time = 0
        self.last_frame = 0
        self.panel = grand_parent
        self.mouse_input = False
        self.draw_mutex = Lock()
        self.update_timer = wx.Timer(self)

        # self.light_model = None
        self.model = None
        self.active_shader = None
        self.light_shader = None
        self.last_mouse_pos = None
        self.all_shaders = None
        self.all_objects = []

        '''
        self.light_model = Model('../models/Light/Lamp.obj', [10, 5, 7], 0.003)
        self.earth_model = Sphere(5, 50, 50, [0, 0, 0], 'models/earth2048.bmp',
                                  should_flip_texture=True)
        self.eric_model = Model('../models/Eric/rp_eric_rigged_001_zup_t.obj',
                                [15, -8, -30], 0.08)
        self.tiger_model = Model('../models/Tiger Animal/smilodon.obj',
                                 [5, -5, -20], 0.03)
        self.tank_model = Model('../models/Tiger 131/Tiger 131.obj',
                                [-15, -16, 10], 8)
        self.all_objects.append(self.earth_model)
        self.all_objects.append(self.light_model)
        self.all_objects.append(self.eric_model)
        self.all_objects.append(self.tiger_model)
        self.all_objects.append(self.tank_model)
        '''

        self.obj_handler = ModelsHandler()

        self.Bind(wx.EVT_TIMER, lambda _: self.Refresh(), self.update_timer)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_mouse_right_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_enter_window)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave_window)

        self.update_timer.Start(1000 / 144)

    def on_resize(self, event) -> None:
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def on_paint(self, event) -> None:
        if not self.init:
            self.init = True
            self.init_gl()

        self.draw_mutex.acquire()
        wx.PaintDC(self)
        self.on_draw()
        self.draw_mutex.release()

    def on_draw(self) -> None:
        self._calculate_delta_time()
        self.camera.do_movement(self.active_keys, self.delta_time)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._update_view_matrix()

        '''
        self.earth_model.draw(self.active_shader)
        self.eric_model.draw(self.active_shader)
        self.tiger_model.draw(self.active_shader)
        self.tank_model.draw(self.active_shader)
        self.light_model.draw(self.light_shader)
        '''
        self.obj_handler.draw_all_objects()

        self.SwapBuffers()

    def init_gl(self) -> None:
        shaders_location = Path(__file__).parent.parent / 'opengl_shaders'
        self.active_shader = Shader(shaders_location / 'vertex_shader.glsl',
                                    shaders_location / 'fragment_shader.glsl')
        self.light_shader = Shader(shaders_location / 'light_vertex.glsl',
                                   shaders_location / 'light_fragment.glsl')

        self.all_shaders = [self.active_shader, self.light_shader]
        model = self.obj_handler.open_new_model(
            self.panel.get_path_obj_file(),
            self.camera,
            self.active_shader)
        self.panel.settings_panel.add_obj(model)

        self._update_projection_matrix()

        glClearColor(125 / 255, 125 / 255, 125 / 255, 1)
        glEnable(GL_DEPTH_TEST)

        self.active_shader.set_uniforms(lightColor=[1, 1, 1])
        self.active_shader.set_uniforms(lightPos=[10, 5, 7])

    def on_mouse_move(self, event) -> None:
        if self.mouse_input:
            self.camera.do_mouse_movement(self.last_mouse_pos[0] + event.x,
                                          self.last_mouse_pos[1] - event.y)
            self.WarpPointer(-self.last_mouse_pos[0], self.last_mouse_pos[1])

    def on_mouse_right_down(self, event) -> None:
        self.last_mouse_pos = (-event.x, event.y)
        self.mouse_input = True
        self.SetFocus()
        self._hide_mouse_cursor()

    def on_mouse_right_up(self, event) -> None:
        self.mouse_input = False
        self._show_mouse_cursor()

    def on_mouse_wheel(self, event) -> None:
        self.camera.fov -= event.WheelRotation * \
                           self.camera.wheel_sensitivity // 120
        self._update_projection_matrix()

    def _calculate_delta_time(self) -> None:
        current_frame = self.time.Time()
        self.delta_time = (current_frame - self.last_frame) / 1000
        self.last_frame = current_frame

    def _update_projection_matrix(self) -> None:
        matrix = self.camera.get_projection(self.aspect_ratio)
        for shader in self.all_shaders:
            shader.set_uniforms(projection=matrix)

    def _update_view_matrix(self) -> None:
        matrix = self.camera.get_view_matrix()
        for shader in self.all_shaders:
            shader.set_uniforms(view=matrix, viewPos=self.camera.pos)

    def on_key_down(self, event) -> None:
        self.active_keys[event.GetKeyCode() % 1024] = True
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.panel.Close()
            self.panel.Destroy()
            sys.exit(0)

    def on_key_up(self, event) -> None:
        self.active_keys[event.KeyCode % 1024] = False

    def on_mouse_enter_window(self, event) -> None:
        pass

    def on_mouse_leave_window(self, event) -> None:
        self._show_mouse_cursor()
        self.mouse_input = False

    def _hide_mouse_cursor(self) -> None:
        self.panel.SetCursor(wx.Cursor(wx.CURSOR_BLANK))

    def _show_mouse_cursor(self) -> None:
        self.panel.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def get_all_objects(self) -> list:
        return self.obj_handler.get_objs_names()
