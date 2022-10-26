import wx
from wx import CommandEvent
from wx.lib import scrolledpanel
from pathlib import Path
from models_handler import ModelsHandler


class NewObjectPanelsCreator:
    def __init__(self, obj_handler: ModelsHandler, parent):
        self.obj_handler = obj_handler
        self.parent = parent
        self.new_model_button = None
        self.new_sphere_button = None
        self.new_custom_button = None
        self.new_vertex_button = None
        self.finish_creation_button = None
        self.custom_colour_picker = None

        self.sizer = None

    def get_obj_gui_panels(self, panel: wx.lib.scrolledpanel,
                           sizer: wx.BoxSizer) -> list:
        panels = []
        self.sizer = sizer

        self.new_model_button = wx.Button(panel, wx.ID_ANY, "open new model")
        self.new_model_button.Bind(wx.EVT_BUTTON, self._new_model_open)

        self.new_sphere_button = wx.Button(panel, wx.ID_ANY, "new sphere")
        self.new_sphere_button.Bind(wx.EVT_BUTTON, self._new_sphere_create)

        self.new_custom_button = wx.Button(panel, wx.ID_ANY, "create object")
        self.new_custom_button.Bind(wx.EVT_BUTTON, self._new_custom_object)

        self.new_vertex_button = wx.Button(panel, wx.ID_ANY, "new vertex")
        self.new_vertex_button.Bind(wx.EVT_BUTTON, self._spawn_new_vertex)

        self.finish_creation_button = wx.Button(panel, wx.ID_ANY, "create")
        self.finish_creation_button.Bind(wx.EVT_BUTTON, self._finish_creation)

        self.custom_colour_picker = wx.ColourPickerCtrl(panel, wx.ID_ANY, style=wx.CLRP_USE_TEXTCTRL)
        # self.custom_colour_picker.Bind(wx.EVT_COLOURPICKER_CHANGED,
        #                                self._change_polygon_colour)

        sizer.Add(self.new_model_button, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.new_sphere_button, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.new_custom_button, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.new_vertex_button, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.finish_creation_button, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.custom_colour_picker, 0, wx.ALL | wx.EXPAND, 5)

        sizer.Hide(self.new_vertex_button)
        sizer.Hide(self.finish_creation_button)
        sizer.Hide(self.custom_colour_picker)

        panels += [self.new_model_button, self.new_sphere_button,
                   self.new_custom_button, self.new_vertex_button,
                   self.finish_creation_button, self.custom_colour_picker]
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
        self._show_custom_object_buttons()
        obj = self.obj_handler.create_new_custom()

    def _spawn_new_vertex(self, event):
        self.obj_handler.add_new_vertex_to_custom_obj(
            self.custom_colour_picker.Colour)

    def _finish_creation(self, event):
        obj = self.obj_handler.finish_object_creation()
        self._hide_custom_object_buttons()
        self.parent.add_obj(obj)

    def _show_custom_object_buttons(self) -> None:
        self.sizer.Hide(self.new_model_button)
        self.sizer.Hide(self.new_sphere_button)
        self.sizer.Hide(self.new_custom_button)

        self.sizer.Show(self.new_vertex_button)
        self.sizer.Show(self.finish_creation_button)
        self.sizer.Show(self.custom_colour_picker)

        self.sizer.Layout()

    def _hide_custom_object_buttons(self) -> None:
        self.sizer.Hide(self.new_vertex_button)
        self.sizer.Hide(self.finish_creation_button)
        self.sizer.Hide(self.custom_colour_picker)

        self.sizer.Show(self.new_model_button)
        self.sizer.Show(self.new_sphere_button)
        self.sizer.Show(self.new_custom_button)

        self.sizer.Layout()
