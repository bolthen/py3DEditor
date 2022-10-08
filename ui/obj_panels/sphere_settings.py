import wx
from wx.lib import scrolledpanel

# from shapess import Sphere
from ui.obj_panels.panels_creator import ObjectPanelsCreator


class SpherePanelsCreator(ObjectPanelsCreator):
    def __init__(self, obj):
        super().__init__(obj)
        self.obj = obj

    def get_obj_gui_panels(self, panel: wx.lib.scrolledpanel,
                           sizer: wx.BoxSizer) -> list:
        panels = super(SpherePanelsCreator, self).get_obj_gui_panels(panel,
                                                                     sizer)
        panels = []

        radius = self._get_size_hbox(self.obj.radius, 1, 100,
                                     self._change_radius, "radius")
        sectors = self._get_size_hbox(self.obj.n_sectors, 3, 100,
                                      self._change_sectors, "sectors count")
        stacks = self._get_size_hbox(self.obj.n_stacks, 3, 100,
                                     self._change_sectors, "stacks count")

        sizer.Add(radius, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(sectors, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(stacks, 0, wx.ALL | wx.EXPAND, 5)

        panel += [radius, sectors, stacks]
        return panels

    def _get_size_hbox(self, default: int, min_: int, max_: int,
                       handler, text: str) -> wx.BoxSizer:
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        slider = wx.Slider(self.panel, wx.ID_ANY, default, min_, max_)
        slider.Bind(wx.EVT_SCROLL_CHANGED, handler)
        slider.SetBackgroundColour(self.FONT_COLOR)

        text = wx.StaticText(self.panel, wx.ID_ANY, text)
        text.SetFont(self.font)
        text.SetBackgroundColour(self.FONT_COLOR)

        hbox.Add(slider, 1, wx.ALL | wx.EXPAND)
        hbox.Add(text, 1, wx.ALL | wx.EXPAND)

        return hbox

    def _change_radius(self, event):
        self.obj.radius = event.Int
        self.obj.generate()

    def _change_sectors(self, event):
        self.obj.n_sectors = event.Int
        self.obj.generate()

    def _change_stacks(self, event):
        self.obj.n_stacks = event.Int
        self.obj.generate()
