import wx
from wx.lib.agw import floatspin
from wx.lib.mixins import listctrl
from wx.lib import scrolledpanel

from panels_creator import ObjectPanelsCreator
from shapes import Object


class ObjsListCtrl(wx.ListCtrl, listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, panel):
        wx.ListCtrl.__init__(self, id=wx.ID_ANY, parent=parent,
                             style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        listctrl.ListCtrlAutoWidthMixin.__init__(self)
        self.SetBackgroundColour('#464544')
        self.active_item_idx = 0
        self.panel = panel
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(15)
        self.SetFont(font)
        self.setResizeColumn(0)
        self.InsertColumn(0, "Объект",
                          width=wx.LIST_AUTOSIZE)
        self.Append(["Новый объект"])

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_pressed)

    def add_object(self, name: str) -> None:
        self.Append([name])

    def on_item_pressed(self, event):
        item_id = event.Index
        self.panel.update_obj_settings(item_id)


class ObjSettingsPanel(wx.Panel):
    FONT_SIZE = 12
    FONT_COLOR = '#ecebed'

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.SIMPLE_BORDER)
        self.main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.splitter = wx.SplitterWindow(self, 0, style=wx.SP_LIVE_UPDATE)
        self.list_ctrl = ObjsListCtrl(self.splitter, self)

        self.scrollbar = scrolledpanel.ScrolledPanel(self.splitter, wx.ID_ANY,
                                                     style=wx.SIMPLE_BORDER)
        self.scrollbar.SetupScrolling()
        self.scroll_vbox = wx.BoxSizer(wx.VERTICAL)
        self.scrollbar.SetSizer(self.scroll_vbox)

        self.splitter.SplitHorizontally(self.list_ctrl, self.scrollbar, 100)

        self.main_vbox.Add(self.splitter, wx.ID_ANY, flag=wx.EXPAND)
        self.SetSizer(self.main_vbox)

        self.idx_to_obj = {0: list()}

    def add_obj(self, obj: Object) -> None:
        self.list_ctrl.add_object(obj.get_obj_name())
        panels = ObjectPanelsCreator(obj).get_obj_gui_panels(self.scrollbar)
        self.idx_to_obj[len(self.idx_to_obj)] = panels
        for panel in panels:
            self.scroll_vbox.Add(panel, 0, wx.EXPAND | wx.ALL, 10)
        self.update_obj_settings(len(self.idx_to_obj) - 1)

    def update_obj_settings(self, idx: int) -> None:
        actual_panels = self.idx_to_obj[idx]
        for k, v in self.idx_to_obj.items():
            if k == idx:
                continue
            for panel in v:
                self.scroll_vbox.Hide(panel)

        for panel in actual_panels:
            self.scroll_vbox.Show(panel, True)
        self.Refresh()
