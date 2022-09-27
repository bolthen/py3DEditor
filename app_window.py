import wx
import sys

from wx import glcanvas
from OpenGL.GL import *
from camera import Camera
from model import Model
from shader import Shader
from shapes import Sphere, Object


class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent, grand_parent):
        self.window_size = (1920, 1080)
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        glcanvas.GLCanvas.__init__(self, parent, id=wx.EXPAND,
                                   size=self.window_size)
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

        self.light_model = None
        self.model = None
        self.active_shader = None
        self.light_shader = None
        self.last_mouse_pos = None
        self.all_shaders = None
        self.all_objects = []

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

    def on_resize(self, event):
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def on_paint(self, event):
        wx.PaintDC(self)

        if not self.init:
            self.init_gl()
            self.panel.on_gl_init()
            self.init = True
        self.on_draw()

    def init_gl(self):
        self.light_model = Model('models/Light/Lamp.obj', [10, 5, 7], 0.003)
        self.model = Sphere(5, 50, 50, [0, 0, 0], 'models/earth2048.bmp',
                            should_flip_texture=True)
        self.all_objects.append(self.model)
        self.all_objects.append(self.light_model)
        self.model.set_x_rotation(90)
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

    def on_draw(self):
        self._calculate_delta_time()
        self.camera.do_movement(self.active_keys, self.delta_time)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._update_view_matrix()

        self.model.draw(self.active_shader)
        self.light_model.draw(self.light_shader)

        self.SwapBuffers()
        self.Refresh(False)

    def on_mouse_move(self, event):
        if self.mouse_input:
            self.camera.do_mouse_movement(self.last_mouse_pos[0] + event.x,
                                          self.last_mouse_pos[1] - event.y)
            self.WarpPointer(-self.last_mouse_pos[0], self.last_mouse_pos[1])

    def on_mouse_right_down(self, event):
        self.last_mouse_pos = (-event.x, event.y)
        self.mouse_input = True
        self._hide_mouse_cursor()

    def on_mouse_right_up(self, event):
        self.mouse_input = False
        self._show_mouse_cursor()

    def on_mouse_wheel(self, event):
        self.camera.fov -= event.WheelRotation * \
                           self.camera.wheel_sensitivity // 120
        self._update_projection_matrix()

    def _calculate_delta_time(self):
        current_frame = self.time.Time()
        self.delta_time = (current_frame - self.last_frame) / 1000
        self.last_frame = current_frame

    def _update_projection_matrix(self):
        matrix = self.camera.get_projection(self.aspect_ratio)
        for shader in self.all_shaders:
            shader.set_uniforms(projection=matrix)

    def _update_view_matrix(self):
        matrix = self.camera.get_view_matrix()
        for shader in self.all_shaders:
            shader.set_uniforms(view=matrix, viewPos=self.camera.pos)

    def on_key_down(self, event):
        self.active_keys[event.GetKeyCode() % 1024] = True
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.panel.Close()

    def on_key_up(self, event):
        self.active_keys[event.KeyCode % 1024] = False

    def on_mouse_enter_window(self, event):
        pass

    def on_mouse_leave_window(self, event):
        self._show_mouse_cursor()
        self.mouse_input = False

    def _hide_mouse_cursor(self):
        self.panel.SetCursor(wx.StockCursor(wx.CURSOR_BLANK))

    def _show_mouse_cursor(self):
        self.panel.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

    def get_all_objects(self):
        return self.all_objects.copy()


class GlPanel(wx.Panel):
    def __init__(self, parent, grand_parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour("#3A4451")
        self.canvas = OpenGLCanvas(self, grand_parent)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.canvas, wx.ID_ANY, wx.EXPAND | wx.ALL)
        self.SetSizer(hbox)


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

        self.main_vbox.Add(self.title, wx.ID_ANY, flag=wx.EXPAND | wx.ALL,
                           border=self.FONT_SIZE * 1.25)
        self.main_vbox.Add(self.wireframe_checkbox, wx.ID_ANY,
                           wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.main_vbox)

    def _change_wireframe(self, event):
        self.obj.wireframe = event.IsChecked()


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="My wx frame")
        self.SetMaxSize((1920, 1080))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.SetBackgroundColour("#293039")
        self.ShowFullScreen(True)

        self.gl_panel = GlPanel(self, self)
        main_hbox = wx.BoxSizer(wx.HORIZONTAL)
        main_hbox.Add(self.gl_panel, proportion=1,
                      flag=wx.EXPAND)
        self.SetSizer(main_hbox)


    def on_gl_init(self):
        return
        '''
        main_hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.settings_panel = wx.Panel(self, style=wx.FULL_REPAINT_ON_RESIZE)
        self.settings_panel.SetBackgroundColour("#3A4451")

        self.hbox1 = wx.BoxSizer(wx.VERTICAL)
        objects = self.gl_panel.canvas.get_all_objects()

        first = ObjSettingsPanel(self.settings_panel, objects[0])
        second = ObjSettingsPanel(self.settings_panel, objects[1])

        self.hbox1.Add(first, 1, wx.EXPAND | wx.ALL, 5)
        self.hbox1.Add(second, 1, wx.EXPAND | wx.ALL, 5)

        self.settings_panel.SetSizer(self.hbox1)

        main_hbox.Add(self.gl_panel, proportion=24, flag=wx.ALL, border=20)
        main_hbox.Add(self.settings_panel, proportion=10, flag=wx.EXPAND | wx.ALL, border=20)

        self.SetSizer(main_hbox)'''

        main_hbox = wx.BoxSizer(wx.HORIZONTAL)

        settings_panel = wx.Panel(self.main_panel)
        objects = self.gl_panel.canvas.get_all_objects()

        first = ObjSettingsPanel(settings_panel, objects[0])
        second = ObjSettingsPanel(settings_panel, objects[1])
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox1.Add(first, wx.ID_ANY, flag=wx.EXPAND | wx.ALL, border=5)
        vbox1.Add(second, wx.ID_ANY, flag=wx.EXPAND | wx.ALL, border=5)
        settings_panel.SetSizer(vbox1)

        main_hbox.Add(self.gl_panel, proportion=24,
                      flag=wx.EXPAND | wx.ALL, border=20)
        # main_hbox.Add(settings_panel, proportion=10,
        #               flag=wx.EXPAND | wx.ALL, border=20)

        self.main_panel.SetSizer(main_hbox)
        self.main_panel.Refresh()

    def on_close(self, event):
        self.Destroy()
        sys.exit(0)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True


