import timer
import wx
import sys
from wx import glcanvas
from wx.lib import ticker
from OpenGL.GL import *
import OpenGL.GL.shaders
from pyrr import Matrix44, matrix44, Vector3
import time, sys

from camera import Camera
from model import Model
from shader import Shader
from shapes import Sphere


class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent, grand_parent):
        self.window_size = (1120, 630)
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        glcanvas.GLCanvas.__init__(self, parent, -1, size=self.window_size)
        self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        self.init = False
        self.active_keys = [False] * 1024
        self.camera = Camera()
        self.time = wx.StopWatch()
        self.delta_time = 0
        self.last_frame = 0
        self.panel = grand_parent
        self.light_model = None
        self.model = None
        self.active_shader = None
        self.light_shader = None
        self.all_shaders = None
        self.last_mouse_pos = None
        self.mouse_input = False
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_MIDDLE_DOWN, self.on_mouse_middle_down)
        self.Bind(wx.EVT_MIDDLE_UP, self.on_mouse_middle_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

    def on_resize(self, event):
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def on_paint(self, event):
        wx.PaintDC(self)

        if not self.init:
            self.init_gl()
            self.init = True
        self.on_draw()

    def init_gl(self):
        self.light_model = Model('models/Light/Lamp.obj', 0.003, [10, 5, 7])
        self.model = Sphere(5, 50, 50, 'models/earth2048.bmp')
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

    def on_mouse_middle_down(self, event):
        self.last_mouse_pos = (-event.x, event.y)
        self.mouse_input = True

    def on_mouse_wheel(self, event):
        self.camera.fov += event.WheelRotation * \
                           self.camera.wheel_sensitivity // 120
        self._update_projection_matrix()

    def on_mouse_middle_up(self, event):
        self.mouse_input = False

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


class MyPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour("#626D58")
        self.canvas = OpenGLCanvas(self, parent)

        # the Start/Stop rotation button
        self.rot_btn = wx.Button(self, -1, label="Start/Stop \nrotation", pos=(1130, 10), size=(100, 50))
        self.rot_btn.BackgroundColour = [125, 125, 125]
        self.rot_btn.ForegroundColour = [255, 255, 255]

        # the radio buttons to switch between the 3D objects
        self.rad_btn1 = wx.RadioButton(self, -1, label="Show Triangle", pos=(1130, 80))
        self.rad_btn2 = wx.RadioButton(self, -1, label="Show Quad", pos=(1130, 100))
        self.rad_btn3 = wx.RadioButton(self, -1, label="Show Cube", pos=(1130, 120))

        # the translation sliders
        self.x_slider = wx.Slider(self, -1, pos=(1130, 180), size=(40, 150), style=wx.SL_VERTICAL|wx.SL_AUTOTICKS,
                                  value=0, minValue=-5, maxValue=5)
        self.y_slider = wx.Slider(self, -1, pos=(1170, 180), size=(40, 150), style=wx.SL_VERTICAL | wx.SL_AUTOTICKS,
                                  value=0, minValue=-5, maxValue=5)
        self.z_slider = wx.Slider(self, -1, pos=(1210, 180), size=(40, 150), style=wx.SL_VERTICAL | wx.SL_AUTOTICKS,
                                  value=0, minValue=-5, maxValue=5)

        # the slider labels using static texts
        font = wx.Font(14, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.x_slider_label = wx.StaticText(self, -1, label="X", pos=(1137, 160))
        self.x_slider_label.SetFont(font)
        self.y_slider_label = wx.StaticText(self, -1, label="Y", pos=(1177, 160))
        self.y_slider_label.SetFont(font)
        self.z_slider_label = wx.StaticText(self, -1, label="Z", pos=(1217, 160))
        self.z_slider_label.SetFont(font)

        # the checkboxes to set background color and the wireframe rendering
        self.bg_color = wx.CheckBox(self, -1, pos=(1130, 360), label="Black background")
        self.wireframe = wx.CheckBox(self, -1, pos=(1130, 390), label="Wireframe mode")

        # text control to display the translation matrix and the rotation matrix combined
        self.log_text = wx.TextCtrl(self, -1, size=(1120, 110), pos=(0, 630), style=wx.TE_MULTILINE)
        self.log_text.BackgroundColour = [70, 125, 70]
        self.log_text.SetFont(font)
        # self.log_text.AppendText(str(self.canvas.ticker.GetFPS()))

        # identity button, resets the matrices to identity
        self.identity_btn = wx.Button(self, -1, label="Set identity \nmatrix", pos=(1130, 630), size=(100, 50))
        self.identity_btn.BackgroundColour = [125, 125, 125]
        self.identity_btn.ForegroundColour = [255, 255, 255]

        # all the event bindings
        self.Bind(wx.EVT_BUTTON, self.rotate, self.rot_btn)
        self.Bind(wx.EVT_RADIOBUTTON, self.triangle, self.rad_btn1)
        self.Bind(wx.EVT_RADIOBUTTON, self.quad, self.rad_btn2)
        self.Bind(wx.EVT_RADIOBUTTON, self.cube, self.rad_btn3)
        self.Bind(wx.EVT_SLIDER, self.translate)
        self.Bind(wx.EVT_CHECKBOX, self.change_bg_color, self.bg_color)
        self.Bind(wx.EVT_CHECKBOX, self.set_wireframe, self.wireframe)
        self.Bind(wx.EVT_BUTTON, self.set_identity, self.identity_btn)

    def warp_pointer(self, x, y):
        self.WarpPointer(x, y)

    def set_identity(self, event):
        self.canvas.combined_matrix = Matrix44.identity()
        self.canvas.rotate = False
        self.canvas.trans_x, self.canvas.trans_y, self.canvas.trans_z = 0, 0, 0
        self.canvas.rot_y = Matrix44.identity()
        self.x_slider.SetValue(0)
        self.y_slider.SetValue(0)
        self.z_slider.SetValue(0)
        self.log_matrix()
        self.canvas.Refresh()

    # displays the combined matrix on the text control area
    def log_matrix(self):
        self.log_text.Clear()
        self.log_text.AppendText(str(self.canvas.ticker.GetFPS()))

    # sets the wireframe mode
    def set_wireframe(self, event):
        self.canvas.wireframe = self.wireframe.GetValue()
        self.canvas.Refresh()

    # changes the clear color to black
    def change_bg_color(self, event):
        self.canvas.bg_color = self.bg_color.GetValue()
        self.canvas.Refresh()

    # this method translates the 3D objects
    def translate(self, event):
        self.canvas.trans_x = self.x_slider.GetValue() * -0.2
        self.canvas.trans_y = self.y_slider.GetValue() * -0.2
        self.canvas.trans_z = self.z_slider.GetValue() * 0.5
        self.log_matrix()
        self.canvas.Refresh()

    # this method shows the triangle
    def triangle(self, event):
        self.canvas.show_triangle = True
        self.canvas.show_quad = False
        self.canvas.show_cube = False
        self.canvas.Refresh()

    # this method shows the quad
    def quad(self, event):
        self.canvas.show_triangle = False
        self.canvas.show_quad = True
        self.canvas.show_cube = False
        self.canvas.Refresh()

    def cube(self, event):
        self.canvas.show_triangle = False
        self.canvas.show_quad = False
        self.canvas.show_cube = True
        self.canvas.Refresh()

    def rotate(self, event):
        if not self.canvas.rotate:
            self.canvas.rotate = True
            self.canvas.Refresh()
        else:
            self.canvas.rotate = False


class MyFrame(wx.Frame):
    def __init__(self):
        self.size = (1280, 780)
        wx.Frame.__init__(self, None, title="My wx frame", size=self.size,
                          style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)
        self.SetMinSize((800, 600))
        self.SetMaxSize((1920, 1080))
        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.panel = MyPanel(self)

    def on_close(self, event):
        self.Destroy()
        sys.exit(0)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True


