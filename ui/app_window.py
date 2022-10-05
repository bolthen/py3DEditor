import pathlib

import wx
import sys
from ui.opengl_canvas import OpenGLCanvas
from ui.settings_panel import ObjSettingsPanel


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title='New Window')
        self.window_size = (800, 600)
        self.SetSize(self.window_size)
        self.SetMaxSize((1920, 1080))
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.SetBackgroundColour('#464544')

        splitter = wx.SplitterWindow(self, wx.ID_ANY,
                                     style=wx.SP_LIVE_UPDATE)

        self.gl_panel = OpenGLCanvas(splitter, self)
        self.settings_panel = ObjSettingsPanel(splitter)

        splitter.SplitVertically(self.gl_panel, self.settings_panel,
                                 sashPosition=self.window_size[1] * 3 // 4)

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
