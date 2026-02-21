"""
和查看历史提示信息有关的模型。
"""

from __future__ import annotations

import time

from typing import Callable, Any

from utils.basetypes import Base
from utils.qtconfig import (
    QListWidgetItem, QWidget, QAbstractItemView,
    QIcon, InfoBarIcon, Slot
)


from widgets.templates import NoticeViewer
from widgets.basic import MyWidget, SideNotice

from .class_ui_model import MixinSuperType


class TipViewerModel(MixinSuperType):
    """
    查看历史提示信息的模型。
    """

    def __init__(
        self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化TipViewerModel", "TipViewerModel.__init__")
        self.ListWidget.itemDoubleClicked.connect(self.view_tip_history)
        self.ListWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    def impl_show_tip(self,
        title: str,
        content: str,
        master: QWidget | None,
        duration: int,
        icon: InfoBarIcon | QIcon | str | None,
        sound: str | None,
        closeable: bool,
        click_command: Callable[..., Any] | None,
        further_info: str
    ) -> SideNotice:
        obj = super().impl_show_tip(
            title, content, master, duration, 
            icon, sound, closeable, click_command, further_info
        )
        self.tip_history.insert(0, obj)
        self.ListWidget.insertItem(
            0,
            time.strftime("%H:%M ", time.localtime(obj.create_time)) + f"{obj.title} {obj.content}",
        )
        return obj

    @Slot(QListWidgetItem)
    def view_tip_history(self, item: QListWidgetItem):
        "查看提示历史，在屏幕右侧的历史列表被双击的时候自动调用"
        Base.log("I", f"查看历史信息，点击的索引：{self.ListWidget.row(item)}", 
                        "TipViewerModel.view_tip_hisory")
        index = self.ListWidget.row(item)
        obj = self.tip_history[index]
        self.tip_viewer_window = TipViewerWindow(obj, self)
        self.tip_viewer_window.show()
    

class TipViewerWindow(NoticeViewer.Ui_widget, MyWidget):
    "提示详细信息窗口"

    def __init__(
        self, obj: SideNotice, parent: QWidget | None = None
    ):
        super(NoticeViewer.Ui_widget, self).__init__(parent)
        self.setupUi(self) # type: ignore
        self.label_4.setText(time.strftime("%H:%M:%S", time.localtime(obj.create_time)))
        self.label_6.setText(f"{obj.duration}ms")
        self.label_8.setText("是" if obj.closeable else "否")
        self.label_3.setText(obj.title)
        self.textBrowser_2.setText(obj.content)
        self.textBrowser.setText(obj.further_info)

    def set_obj(self, obj: SideNotice):
        "设置当前的展示对象"
        self.label_4.setText(time.strftime("%H:%M:%S", time.localtime(obj.create_time)))
        self.label_6.setText(f"{obj.duration}ms")
        self.label_8.setText("是" if obj.closeable else "否")
        self.label_3.setText(obj.title)
        self.textBrowser_2.setText(obj.content)
        self.textBrowser.setText(obj.further_info)
