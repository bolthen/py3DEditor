import wx
from wx.lib.agw import floatspin

from shapes import Object


class ObjectPanelsCreator:
    FONT_SIZE = 12
    FONT_COLOR = '#ecebed'

    def __init__(self, obj=None):
        self.obj = obj
        self.font = None
        self.wireframe_checkbox = None
        self.panel = None

    def get_obj_gui_panels(self, panel: wx, obj=None) -> list:
        if self.obj is None:
            self.obj = obj
        self.panel = panel

        panels = []

        title_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font.SetPointSize(self.FONT_SIZE * 1.25)

        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font.SetPointSize(self.FONT_SIZE)

        title = wx.StaticText(self.panel, label=self.obj.get_obj_name())
        title.SetForegroundColour(self.FONT_COLOR)
        title.SetFont(title_font)

        self.wireframe_checkbox = wx.CheckBox(self.panel, label="Wireframe")
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

        panels += [title, self.wireframe_checkbox, pitch, yaw,
                   roll, x_pos, y_pos, z_pos]
        return panels

    def _get_angle_hbox(self, text: str, handler) -> wx.BoxSizer:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        slider = wx.Slider(self.panel, wx.ID_ANY, 0, -180, 180)
        slider.Bind(wx.EVT_SCROLL, handler)
        yaw_text = wx.StaticText(self.panel, wx.ID_ANY, text)
        yaw_text.SetFont(self.font)
        yaw_text.SetForegroundColour(self.FONT_COLOR)
        slider.SetForegroundColour(self.FONT_COLOR)
        hbox.Add(slider, 1, wx.ALL | wx.EXPAND)
        hbox.Add(yaw_text, 1, wx.ALL | wx.EXPAND)
        return hbox

    def _get_pos_hbox(self, text: str, handler,
                      default_value: float) -> wx.BoxSizer:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        pos = floatspin.FloatSpin(self.panel, wx.ID_ANY, value=default_value,
                                  increment=0.5, digits=2)
        pos.Bind(floatspin.EVT_FLOATSPIN, handler)
        yaw_text = wx.StaticText(self.panel, wx.ID_ANY, text)
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
