import wx
from wx.lib.agw import floatspin
from wx.lib import scrolledpanel

from ui.obj_panels.panels_creator import ObjectPanelsCreator


class MultiObjectsPanel:
    class LocationObject:
        def __init__(self, obj):
            self.obj = obj
            self.start_pos = [obj.pos[0], obj.pos[1], obj.pos[2]]

    def __init__(self, objs: list):
        self.font = None
        self.objs = [MultiObjectsPanel.LocationObject(i) for i in objs]
        self.panel = None

    def get_obj_gui_panels(self, panel: wx.lib.scrolledpanel,
                           sizer: wx.BoxSizer) -> list:
        self.panel = panel

        title_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font.SetPointSize(ObjectPanelsCreator.FONT_SIZE * 1.25)

        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font.SetPointSize(ObjectPanelsCreator.FONT_SIZE)

        title = wx.StaticText(self.panel, label="group")
        title.SetForegroundColour(ObjectPanelsCreator.FONT_COLOR)
        title.SetFont(title_font)

        x_pos = self._get_pos_hbox("x position", self._change_x_pos)
        y_pos = self._get_pos_hbox("y position", self._change_y_pos)
        z_pos = self._get_pos_hbox("z position", self._change_z_pos)

        sizer.Add(title, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(x_pos, 0, wx.ALL, 5)
        sizer.Add(y_pos, 0, wx.ALL, 5)
        sizer.Add(z_pos, 0, wx.ALL, 5)

        panels = [title, x_pos, y_pos, z_pos]
        return panels

    def _get_pos_hbox(self, text: str, handler) -> wx.BoxSizer:
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        spin = floatspin.FloatSpin(self.panel, wx.ID_ANY, increment=0.5,
                                   digits=2)
        spin.Bind(floatspin.EVT_FLOATSPIN, handler)
        spin.SetForegroundColour(ObjectPanelsCreator.FONT_COLOR)

        text = wx.StaticText(self.panel, wx.ID_ANY, text)
        text.SetFont(self.font)
        text.SetForegroundColour(ObjectPanelsCreator.FONT_COLOR)

        hbox.Add(spin, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
        hbox.Add(text, 1, wx.RIGHT | wx.LEFT | wx.EXPAND, 5)
        return hbox

    def _change_x_pos(self, event) -> None:
        value = event.GetEventObject().Value
        for loc_obj in self.objs:
            obj = loc_obj.obj
            obj.set_pos(loc_obj.start_pos[0] + value, obj.pos[1], obj.pos[2])

    def _change_y_pos(self, event) -> None:
        value = event.GetEventObject().Value
        for loc_obj in self.objs:
            obj = loc_obj.obj
            obj.set_pos(obj.pos[0], loc_obj.start_pos[1] + value, obj.pos[2])

    def _change_z_pos(self, event) -> None:
        value = event.GetEventObject().Value
        for loc_obj in self.objs:
            obj = loc_obj.obj
            obj.set_pos(obj.pos[0], obj.pos[1], loc_obj.start_pos[2] + value)

