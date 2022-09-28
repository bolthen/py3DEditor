import wx
import sys

from threading import Lock
from wx import glcanvas
from wx.lib import scrolledpanel
from OpenGL.GL import *
from camera import Camera
from model import Model
from shader import Shader
from shapes import Sphere, Object


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

        self.light_model = None
        self.model = None
        self.active_shader = None
        self.light_shader = None
        self.last_mouse_pos = None
        self.all_shaders = None
        self.all_objects = []

        self.light_model = Model('models/Light/Lamp.obj', [10, 5, 7], 0.003)
        self.earth_model = Sphere(5, 50, 50, [0, 0, 0], 'models/earth2048.bmp',
                                  should_flip_texture=True)
        self.eric_model = Model('models/Eric/rp_eric_rigged_001_zup_t.obj',
                                [15, -8, -30], 0.08)
        self.tiger_model = Model('models/Tiger Animal/smilodon.obj',
                                 [5, -5, -20], 0.03)
        self.tank_model = Model('models/Tiger 131/Tiger 131.obj',
                                [-15, -16, 10], 8)
        self.all_objects.append(self.earth_model)
        self.all_objects.append(self.light_model)
        self.all_objects.append(self.eric_model)
        self.all_objects.append(self.tiger_model)
        self.all_objects.append(self.tank_model)

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
        self.draw_mutex.acquire()
        wx.PaintDC(self)

        if not self.init:
            self.init_gl()
            self.init = True
        self.on_draw()
        self.draw_mutex.release()

    def on_draw(self) -> None:
        self._calculate_delta_time()
        self.camera.do_movement(self.active_keys, self.delta_time)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._update_view_matrix()

        self.earth_model.draw(self.active_shader)
        self.eric_model.draw(self.active_shader)
        self.tiger_model.draw(self.active_shader)
        self.tank_model.draw(self.active_shader)
        self.light_model.draw(self.light_shader)

        self.SwapBuffers()

    def init_gl(self) -> None:
        self.active_shader = Shader('programs/vertex_shader.glsl',
                                    'programs/fragment_shader.glsl')
        self.light_shader = Shader('programs/light_vertex.glsl',
                                   'programs/light_fragment.glsl')
        self.all_shaders = [self.active_shader, self.light_shader]

        self._update_projection_matrix()

        glClearColor(125 / 255, 125 / 255, 125 / 255, 1)
        glEnable(GL_DEPTH_TEST)

        self.active_shader.set_uniforms(lightColor=[1, 1, 1])
        self.active_shader.set_uniforms(lightPos=self.light_model.pos)

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
        return self.all_objects.copy()


class ObjSettingsPanel(wx.Panel):
    FONT_SIZE = 12

    def __init__(self, parent, obj: Object):
        wx.Panel.__init__(self, parent, style=wx.FULL_REPAINT_ON_RESIZE)
        self.obj = obj

        self.main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.title_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.title_font.SetPointSize(self.FONT_SIZE * 1.5)
        self.title_font.MakeBold()

        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font.SetPointSize(self.FONT_SIZE)

        self.title = wx.StaticText(self, label=obj.get_obj_name())
        self.title.SetFont(self.title_font)

        self.wireframe_checkbox = wx.CheckBox(self, label="Wireframe")
        self.wireframe_checkbox.SetFont(self.font)
        self.wireframe_checkbox.Bind(wx.EVT_CHECKBOX, self._change_wireframe)

        pitch = self._get_angle_hbox("Pitch", self._change_pitch)
        yaw = self._get_angle_hbox("Yaw", self._change_yaw)
        roll = self._get_angle_hbox("Roll", self._change_roll)

        self.main_vbox.Add(self.title, 0, wx.ALL | wx.CENTER, 5)
        self.main_vbox.Add(self.wireframe_checkbox, 0, wx.ALL, 5)
        self.main_vbox.Add(pitch, 0, wx.ALL | wx.EXPAND, 5)
        self.main_vbox.Add(yaw, 0, wx.ALL | wx.EXPAND, 5)
        self.main_vbox.Add(roll, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(self.main_vbox)

    def _get_angle_hbox(self, text: str, handler) -> wx.BoxSizer:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        slider = wx.Slider(self, wx.ID_ANY, 0, -180, 180)
        self.Bind(wx.EVT_SCROLL, handler, slider)
        yaw_text = wx.StaticText(self, wx.ID_ANY, text)
        yaw_text.SetFont(self.font)
        hbox.Add(slider, 1, wx.ALL | wx.EXPAND)
        hbox.Add(yaw_text, 1, wx.ALL | wx.EXPAND)
        return hbox

    def _change_wireframe(self, event) -> None:
        value = event.IsChecked()
        self.obj.wireframe = value
        self.wireframe_checkbox.SetValue(value)

    def _change_pitch(self, event) -> None:
        self.obj.set_x_rotation(event.Int)

    def _change_yaw(self, event) -> None:
        self.obj.set_y_rotation(event.Int)

    def _change_roll(self, event) -> None:
        self.obj.set_z_rotation(event.Int)


class MyFrame2(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='New Window')
        self.SetMaxSize((1920, 1080))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.panel = wx.Panel(self)
        self.gl_panel = OpenGLCanvas(self.panel, self)
        # self.gl_panel = GlPanel(self.panel, self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        scrollbar = wx.lib.scrolledpanel.ScrolledPanel(self.panel, wx.ID_ANY,
                                                       style=wx.SIMPLE_BORDER)
        scrollbar.SetupScrolling()
        objs = self.gl_panel.get_all_objects()
        vbox = wx.BoxSizer(wx.VERTICAL)

        for obj in objs:
            panel = ObjSettingsPanel(scrollbar, obj)
            vbox.Add(panel, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 10)

        scrollbar.SetSizer(vbox)

        hbox.Add(self.gl_panel, proportion=24, flag=wx.EXPAND)
        hbox.Add(scrollbar, proportion=7, flag=wx.EXPAND)

        self.panel.SetSizer(hbox)

    def on_close(self, event):
        self.Destroy()
        sys.exit(0)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame2()
        frame.Show()
        return True
