import wx
from wx.lib import scrolledpanel


class NewObjectPanelsCreator:
    def __init__(self):
        pass

    def get_obj_gui_panels(self, panel: wx.lib.scrolledpanel,
                           sizer: wx.BoxSizer) -> list:
        panels = []

        new_model = wx.Button(panel, wx.ID_ANY, "open new model")
        new_model.Bind(wx.EVT_PRESS_AND_TAP, self._new_model_open)

        new_sphere = wx.Button(panel, wx.ID_ANY, "new sphere")
        new_sphere.Bind(wx.EVT_PRESS_AND_TAP, self._new_sphere_create)

        sizer.Add(new_model, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(new_sphere, 0, wx.ALL | wx.EXPAND, 5)

        panels += [new_model, sizer]
        return panels

    def _new_model_open(self, event):
        pass

    def _new_sphere_create(self, event):
        pass
