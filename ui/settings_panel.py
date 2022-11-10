import wx
from wx.lib.mixins import listctrl
from wx.lib import scrolledpanel
from collections import deque

from wx.lib.scrolledpanel import ScrolledPanel

from models_handler import ModelsHandler
from ui.obj_panels.custom_obj_panel import NewObjectPanelsCreator
from object.base_object import BaseObject
from ui.obj_panels.multi_objects_panel import MultiObjectsPanel


class ObjsListCtrl(wx.ListCtrl, listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, panel):
        wx.ListCtrl.__init__(self, id=wx.ID_ANY, parent=parent,
                             style=wx.LC_REPORT)
        listctrl.ListCtrlAutoWidthMixin.__init__(self)
        self.SetBackgroundColour('#464544')
        self.panel = panel
        self.active_objects = deque()
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(15)
        self.SetFont(font)
        self.setResizeColumn(0)
        self.InsertColumn(0, "Объект",
                          width=wx.LIST_AUTOSIZE)
        self.Append(["Новый объект"])
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_item_selected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_item_deselected)

    def add_object(self, name: str) -> None:
        self.Append([name])

    def on_item_deselected(self, event):
        if event.Index != 0:
            self.active_objects.remove(event.Index)
        self.panel.update_obj_settings()

    def on_item_selected(self, event):
        item_id = event.Index
        if event.Index != 0:
            self.active_objects.append(item_id)
        self.panel.update_obj_settings()
        self.panel.Refresh()
        self.Refresh()


class ObjSettingsPanel(wx.Panel):
    FONT_SIZE = 12
    FONT_COLOR = '#ecebed'

    def __init__(self, parent, obj_handler: ModelsHandler):
        wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.SIMPLE_BORDER)
        self._splitter_size = 200
        self.obj_handler = obj_handler
        self.num_to_obj = {}

        self.main_vbox = wx.BoxSizer(wx.VERTICAL)

        self.splitter = wx.SplitterWindow(self, 0, style=wx.SP_LIVE_UPDATE)
        self.splitter.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING,
                           self._on_splitter_resize)

        self.main_vbox.Add(self.splitter, wx.ID_ANY, flag=wx.EXPAND)
        self.SetSizer(self.main_vbox)

        self.list_ctrl = ObjsListCtrl(self.splitter, self)
        self.new_obj_panel = self._get_new_obj_panel()

        self._create_new_light()
        self.update_obj_settings()

    def add_obj(self, obj: BaseObject) -> None:
        self.list_ctrl.add_object(obj.get_obj_name())

        obj_idx = len(self.num_to_obj) + 1
        self.num_to_obj[obj_idx] = obj

        self.list_ctrl.Select(obj_idx)
        # self.list_ctrl.Focus(len(self.obj_to_scroll) - 1)

    def update_obj_settings(self) -> None:
        self._hide_scrolls()
        self._show_actual_panels()
        self.Refresh()

    def _get_active_objects(self) -> list:
        result = []
        for i in self.list_ctrl.active_objects:
            result.append(self.num_to_obj[i])
        return result

    def _hide_scrolls(self) -> None:
        self.splitter.Unsplit()

    def _show_actual_panels(self) -> None:
        if len(self.list_ctrl.active_objects) > 1:
            actual_scroll = self._accept_multi_objects_panel()
        else:
            actual_scroll = self._accept_single_object_panel()

        self.splitter.SplitHorizontally(self.list_ctrl,
                                        actual_scroll,
                                        self._splitter_size)

    def _accept_single_object_panel(self) -> ScrolledPanel:
        if len(self.list_ctrl.active_objects) == 0:
            return self.new_obj_panel

        obj = self.num_to_obj[self.list_ctrl.active_objects[0]]
        new_scroll = scrolledpanel.ScrolledPanel(self.splitter, wx.ID_ANY,
                                                 style=wx.SIMPLE_BORDER)
        new_scroll.SetupScrolling()
        new_sizer = wx.BoxSizer(wx.VERTICAL)
        new_scroll.SetSizer(new_sizer)

        _ = obj.get_settings_panels(new_scroll, new_sizer)
        return new_scroll

    def _accept_multi_objects_panel(self) -> ScrolledPanel:
        new_scroll = scrolledpanel.ScrolledPanel(self.splitter, wx.ID_ANY,
                                                 style=wx.SIMPLE_BORDER)
        new_scroll.SetupScrolling()
        new_sizer = wx.BoxSizer(wx.VERTICAL)
        new_scroll.SetSizer(new_sizer)

        multi_objs = MultiObjectsPanel(self._get_active_objects())
        _ = multi_objs.get_obj_gui_panels(new_scroll, new_sizer)

        return new_scroll

    def _get_new_obj_panel(self) -> scrolledpanel.ScrolledPanel:
        scrollbar = scrolledpanel.ScrolledPanel(self.splitter, wx.ID_ANY,
                                                style=wx.SIMPLE_BORDER)
        scrollbar.SetupScrolling()
        scroll_vbox = wx.BoxSizer(wx.VERTICAL)
        scrollbar.SetSizer(scroll_vbox)

        panels_creator = NewObjectPanelsCreator(self.obj_handler, self)
        _ = panels_creator.get_obj_gui_panels(scrollbar, scroll_vbox)
        return scrollbar

    def _on_splitter_resize(self, event):
        self._splitter_size = event.SashPosition

    def _create_new_light(self) -> None:
        light = self.obj_handler.create_light()
        self.add_obj(light)

