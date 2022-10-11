import wx
from wx.lib.mixins import listctrl
from wx.lib import scrolledpanel

from models_handler import ModelsHandler
from ui.obj_panels.new_obj_settings import NewObjectPanelsCreator
from shapes import Object


class ObjsListCtrl(wx.ListCtrl, listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, panel):
        wx.ListCtrl.__init__(self, id=wx.ID_ANY, parent=parent,
                             style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        listctrl.ListCtrlAutoWidthMixin.__init__(self)
        self.SetBackgroundColour('#464544')
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
        self.panel.Refresh()
        self.Refresh()


class ObjSettingsPanel(wx.Panel):
    FONT_SIZE = 12
    FONT_COLOR = '#ecebed'

    def __init__(self, parent, obj_handler: ModelsHandler):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.SIMPLE_BORDER)
        self.actual_obj_idx = 0
        self._splitter_size = 100
        self.main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.splitter = wx.SplitterWindow(self, 0, style=wx.SP_LIVE_UPDATE)
        self.list_ctrl = ObjsListCtrl(self.splitter, self)

        scrollbar = scrolledpanel.ScrolledPanel(self.splitter, wx.ID_ANY,
                                                style=wx.SIMPLE_BORDER)
        scrollbar.SetupScrolling()
        scroll_vbox = wx.BoxSizer(wx.VERTICAL)
        scrollbar.SetSizer(scroll_vbox)
        panels = NewObjectPanelsCreator(obj_handler, self).get_obj_gui_panels(
            scrollbar, scroll_vbox)
        self.obj_to_scroll = {0: scrollbar}

        self.splitter.SplitHorizontally(self.list_ctrl,
                                        scrollbar,
                                        self._splitter_size)

        self.main_vbox.Add(self.splitter, wx.ID_ANY, flag=wx.EXPAND)
        self.SetSizer(self.main_vbox)

        self.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING,
                           self._on_splitter_resize)

    def add_obj(self, obj: Object) -> None:
        self.list_ctrl.add_object(obj.get_obj_name())

        new_scroll = scrolledpanel.ScrolledPanel(self.splitter, wx.ID_ANY,
                                                 style=wx.SIMPLE_BORDER)
        new_scroll.SetupScrolling()
        new_sizer = wx.BoxSizer(wx.VERTICAL)
        new_scroll.SetSizer(new_sizer)

        panels = obj.get_settings_panels(new_scroll, new_sizer)

        self.obj_to_scroll[len(self.obj_to_scroll)] = new_scroll
        self.update_obj_settings(len(self.obj_to_scroll) - 1)

    def update_obj_settings(self, idx: int) -> None:
        self._hide_scroll(self.actual_obj_idx)
        self.actual_obj_idx = idx
        self._show_actual_panels(idx)
        self.Refresh()

    def _hide_scroll(self, idx: int) -> None:
        self.splitter.Unsplit(self.obj_to_scroll[idx])

    def _show_actual_panels(self, idx: int) -> None:
        actual_scroll = self.obj_to_scroll[idx]
        self.splitter.SplitHorizontally(self.list_ctrl,
                                        actual_scroll,
                                        self._splitter_size)

    def _on_splitter_resize(self, event):
        self._splitter_size = event.SashPosition

