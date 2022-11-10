import pathlib
import time

import wx
import sys

from engine import RedactorEngine
from models_handler import ModelsHandler
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

        self.engine = RedactorEngine()
        self.gl_panel = OpenGLCanvas(splitter, self, self.engine)
        self.settings_panel = ObjSettingsPanel(splitter,
                                               self.engine.obj_handler)

        splitter.SplitVertically(self.gl_panel, self.settings_panel,
                                 sashPosition=self.window_size[1] * 3 // 4)

    def on_close(self, event):
        self.Destroy()
        sys.exit(0)


class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True
