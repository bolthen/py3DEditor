import wx
from wx import CommandEvent
from wx.lib import scrolledpanel
from pathlib import Path
from models_handler import ModelsHandler


class NewObjectPanelsCreator:
    def __init__(self, obj_handler: ModelsHandler, parent):
        self.obj_handler = obj_handler
        self.parent = parent

    def get_obj_gui_panels(self, panel: wx.lib.scrolledpanel,
                           sizer: wx.BoxSizer) -> list:
        panels = []

        new_model = wx.Button(panel, wx.ID_ANY, "open new model")
        new_model.Bind(wx.EVT_BUTTON, self._new_model_open)

        new_sphere = wx.Button(panel, wx.ID_ANY, "new sphere")
        new_sphere.Bind(wx.EVT_BUTTON, self._new_sphere_create)

        new_custom = wx.Button(panel, wx.ID_ANY, "create object")
        new_custom.Bind(wx.EVT_BUTTON, self._new_sphere_create)

        sizer.Add(new_model, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(new_sphere, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(new_custom, 0, wx.ALL | wx.EXPAND, 5)

        panels += [new_model, sizer]
        return panels

    def _new_model_open(self, event: CommandEvent) -> None:
        caller = event.GetEventObject()
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(caller, 'Open', wildcard='*.obj',
                               style=style)
        if dialog.ShowModal() == wx.ID_OK:
            path = Path(dialog.GetPath())
        else:
            path = None
        dialog.Destroy()

        if path is not None:
            model = self.obj_handler.open_new_model(path)
            self.parent.add_obj(model)

    def _new_sphere_create(self, event):
        caller = event.GetEventObject()
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        dialog = wx.FileDialog(caller, 'Open',
                               wildcard='*.bmp;*.png;*.jpg',
                               style=style)
        if dialog.ShowModal() == wx.ID_OK:
            path = Path(dialog.GetPath())
        else:
            path = None
        dialog.Destroy()

        model = self.obj_handler.create_new_sphere(path)
        self.parent.add_obj(model)

    def _new_custom_object(self, event):
        pass
