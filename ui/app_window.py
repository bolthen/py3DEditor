import pathlib

import wx
import sys

from wx.lib.agw import floatspin

from ui.opengl_canvas import OpenGLCanvas
from shapes import Object


class ObjSettingsPanel(wx.Panel):
    FONT_SIZE = 12
    FONT_COLOR = '#ecebed'

    def __init__(self, parent, obj: Object):
        wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
        self.obj = obj

        self.main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.title_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.title_font.SetPointSize(self.FONT_SIZE * 1.25)
        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font.SetPointSize(self.FONT_SIZE)

        self.title = wx.StaticText(self, label=obj.get_obj_name())
        self.title.SetForegroundColour(self.FONT_COLOR)
        self.title.SetFont(self.title_font)

        self.wireframe_checkbox = wx.CheckBox(self, label="Wireframe")
        self.wireframe_checkbox.SetFont(self.font)
        self.wireframe_checkbox.SetForegroundColour(self.FONT_COLOR)
        self.wireframe_checkbox.Bind(wx.EVT_CHECKBOX, self._change_wireframe)

        pitch = self._get_angle_hbox("Pitch", self._change_pitch)
        yaw = self._get_angle_hbox("Yaw", self._change_yaw)
        roll = self._get_angle_hbox("Roll", self._change_roll)

        x_pos = self._get_pos_hbox("x position", self._change_x_pos,
                                   self.obj.pos[0])
        y_pos = self._get_pos_hbox("y position", self._change_y_pos,
                                   self.obj.pos[1])
        z_pos = self._get_pos_hbox("z position", self._change_z_pos,
                                   self.obj.pos[2])

        self.main_vbox.Add(self.title, 0, wx.ALL | wx.CENTER, 5)
        self.main_vbox.Add(self.wireframe_checkbox, 0, wx.ALL, 5)
        self.main_vbox.Add(x_pos, 0, wx.ALL, 5)
        self.main_vbox.Add(y_pos, 0, wx.ALL, 5)
        self.main_vbox.Add(z_pos, 0, wx.ALL, 5)
        self.main_vbox.Add(pitch, 0, wx.ALL | wx.EXPAND, 5)
        self.main_vbox.Add(yaw, 0, wx.ALL | wx.EXPAND, 5)
        self.main_vbox.Add(roll, 0, wx.ALL | wx.EXPAND, 5)

        self.SetSizer(self.main_vbox)

    def _get_angle_hbox(self, text: str, handler) -> wx.BoxSizer:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        slider = wx.Slider(self, wx.ID_ANY, 0, -180, 180)
        slider.Bind(wx.EVT_SCROLL, handler)
        yaw_text = wx.StaticText(self, wx.ID_ANY, text)
        yaw_text.SetFont(self.font)
        yaw_text.SetForegroundColour(self.FONT_COLOR)
        slider.SetForegroundColour(self.FONT_COLOR)
        hbox.Add(slider, 1, wx.ALL | wx.EXPAND)
        hbox.Add(yaw_text, 1, wx.ALL | wx.EXPAND)
        return hbox

    def _get_pos_hbox(self, text: str, handler,
                      default_value: float) -> wx.BoxSizer:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        pos = floatspin.FloatSpin(self, wx.ID_ANY, value=default_value,
                                  increment=0.5, digits=2)
        pos.Bind(floatspin.EVT_FLOATSPIN, handler)
        yaw_text = wx.StaticText(self, wx.ID_ANY, text)
        yaw_text.SetFont(self.font)
        yaw_text.SetForegroundColour(self.FONT_COLOR)
        pos.SetForegroundColour(self.FONT_COLOR)
        hbox.Add(pos, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
        hbox.Add(yaw_text, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
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

    def _change_x_pos(self, event) -> None:
        tmp = event.GetEventObject()
        self.obj.set_pos(tmp.Value, self.obj.pos[1], self.obj.pos[2])

    def _change_y_pos(self, event) -> None:
        tmp = event.GetEventObject()
        self.obj.set_pos(self.obj.pos[0], tmp.Value, self.obj.pos[2])

    def _change_z_pos(self, event) -> None:
        tmp = event.GetEventObject()
        self.obj.set_pos(self.obj.pos[0], self.obj.pos[1], tmp.Value)


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='New Window')
        self.SetMaxSize((1920, 1080))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.panel = wx.Panel(self)
        self.gl_panel = OpenGLCanvas(self.panel, self)
        self.SetBackgroundColour('#464544')

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        objs = self.gl_panel.get_all_objects()
        # scrollbar = wx.lib.scrolledpanel.ScrolledPanel(self.panel, wx.ID_ANY,
        #                                                style=wx.SIMPLE_BORDER)
        # scrollbar.SetupScrolling()
        # vbox = wx.BoxSizer(wx.VERTICAL)
        #
        # for obj in objs:
        #     panel = ObjSettingsPanel(scrollbar, obj)
        #     vbox.Add(panel, 0, wx.EXPAND | wx.ALL, 10)
        #
        # scrollbar.SetSizer(vbox)
        objs_name = [i.get_obj_name() for i in objs]
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(15)
        scrollbar = wx.ListBox(self.panel, wx.ID_ANY, choices=objs_name,
                               style=wx.LB_NEEDED_SB)
        scrollbar.SetFont(font)

        hbox.Add(self.gl_panel, proportion=24, flag=wx.EXPAND | wx.ALL,
                 border=10)
        hbox.Add(scrollbar, proportion=7, flag=wx.EXPAND | wx.ALL, border=5)

        self.panel.SetSizer(hbox)

    def get_path_obj_file(self) -> pathlib.Path:
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(self, 'Open', wildcard='*.obj', style=style)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        else:
            path = None
        dialog.Destroy()
        return pathlib.Path(path)

    def on_close(self, event):
        self.Destroy()
        sys.exit(0)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True
