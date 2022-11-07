import wx
from wx.lib import scrolledpanel
from ui.obj_panels.panels_creator import ObjectPanelsCreator


class LightSpherePanelsCreator(ObjectPanelsCreator):
    def __init__(self, obj):
        super().__init__(obj)
        self.obj = obj

    def get_obj_gui_panels(self, panel: wx.lib.scrolledpanel,
                           sizer: wx.BoxSizer) -> list:
        panels = []
        self.panel = panel

        title_font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font.SetPointSize(self.FONT_SIZE * 1.25)

        self.font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font.SetPointSize(self.FONT_SIZE)

        title = wx.StaticText(self.panel, label=self.obj.get_obj_name())
        title.SetForegroundColour(self.FONT_COLOR)
        title.SetFont(title_font)

        x_pos = self._get_pos_hbox("x position", self._change_x_pos,
                                   self.obj.pos[0])
        y_pos = self._get_pos_hbox("y position", self._change_y_pos,
                                   self.obj.pos[1])
        z_pos = self._get_pos_hbox("z position", self._change_z_pos,
                                   self.obj.pos[2])

        custom_colour_picker = wx.ColourPickerCtrl(
            panel, wx.ID_ANY, style=wx.CLRP_USE_TEXTCTRL)
        custom_colour_picker.Bind(wx.EVT_COLOURPICKER_CHANGED,
                                  self._on_colour_changed)
        custom_colour_picker.SetColour([self.obj.colour[0] * 255,
                                        self.obj.colour[1] * 255,
                                        self.obj.colour[2] * 255])

        sizer.Add(title, 0, wx.ALL | wx.CENTER, 5)
        sizer.Add(x_pos, 0, wx.ALL, 5)
        sizer.Add(y_pos, 0, wx.ALL, 5)
        sizer.Add(z_pos, 0, wx.ALL, 5)
        sizer.Add(custom_colour_picker, 0, wx.ALL | wx.EXPAND, 10)

        panels += [title, x_pos, y_pos, z_pos]
        return panels

    def _on_colour_changed(self, event):
        self.obj.colour = event.Colour
