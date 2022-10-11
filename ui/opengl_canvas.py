import sys
import wx

from wx import glcanvas
from engine import RedactorEngine
from OpenGL.GL import *


class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent, grand_parent, engine: RedactorEngine):
        self.window_size = (1920, 1080)
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        glcanvas.GLCanvas.__init__(self, parent, id=wx.EXPAND)
        self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        self.init = False
        self.active_keys = [False] * 1024
        self.panel = grand_parent
        self.mouse_input = False
        self.update_timer = wx.Timer(self)
        self.engine = engine
        self.last_mouse_pos = None

        self.Bind(wx.EVT_TIMER, lambda _: self.Refresh(), self.update_timer)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.Bind(wx.EVT_MOTION, self.on_mouse_move)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)
        self.Bind(wx.EVT_RIGHT_UP, self.on_mouse_right_up)
        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_leave_window)

        self.update_timer.Start(1000 / 144)

    def on_resize(self, event) -> None:
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def on_paint(self, event) -> None:
        if not self.init:
            self.init = True
            self.init_gl()

        self.engine.start_cycle()
        wx.PaintDC(self)
        self.on_draw()
        self.engine.end_game_cycle()

    def on_draw(self) -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.engine.on_tick(self.active_keys)
        self.engine.draw_scene()

        self.SwapBuffers()

    def init_gl(self) -> None:
        self.engine.update_projection_matrix(self.aspect_ratio)
        self.engine.init_gl()

        glClearColor(125 / 255, 125 / 255, 125 / 255, 1)
        glEnable(GL_DEPTH_TEST)

    def on_mouse_move(self, event) -> None:
        if self.mouse_input:
            self.engine.set_mouse_pos((self.last_mouse_pos[0] + event.x,
                                       self.last_mouse_pos[1] - event.y))

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
        self.engine.change_fov(event.WheelRotation)
        self.engine.update_projection_matrix(self.aspect_ratio)

    def on_key_down(self, event) -> None:
        self.active_keys[event.GetKeyCode() % 1024] = True
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.panel.Close()
            self.panel.Destroy()
            sys.exit(0)

    def on_key_up(self, event) -> None:
        self.active_keys[event.KeyCode % 1024] = False

    def on_mouse_leave_window(self, event) -> None:
        self._show_mouse_cursor()
        self.mouse_input = False

    def _hide_mouse_cursor(self) -> None:
        self.panel.SetCursor(wx.Cursor(wx.CURSOR_BLANK))

    def _show_mouse_cursor(self) -> None:
        self.panel.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
