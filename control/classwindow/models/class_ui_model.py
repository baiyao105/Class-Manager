"""
一个基本的UI界面，可以根据这里的控件进行操作。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from utils.basetypes import Base

from widgets.templates import MainClassWindow

from .basic_models import DataUIModel

class WindowInfo:
    "窗口信息"
    def __init__(self):
        self.video = VideoInfo()

class VideoInfo:
    "视频信息"

    def __init__(self):
        self.last_paint_event = PaintEventInfo()
        self.last_update_event = UpdateInfo()

class PaintEventInfo:
    "上一个绘制事件时间的信息"
    data_reading: float = 0.0
    "数据处理时间"
    painter_constructing: float = 0.0
    "绘制器构造时间"
    background_dealing: float = 0.0
    "背景处理时间"
    pixmap_drawing: float = 0.0
    "绘制Pixmap耗时"
    event_accepting: float = 0.0
    "事件处理耗时"
    total_time: float = 0.0
    "绘制事件总耗时"

class UpdateInfo:
    "更新信息"
    widget_updating: float = 0.0
    "更新控件的时间"
    super: float = 0.0
    "PySide6处理时间"
    total_time: float = 0.0
    "总时间"


class ClassUIModel(DataUIModel, MainClassWindow.Ui_MainWindow):

    def __init__(
        self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ) -> None:
        Base.log("D", "初始化ClassUIModel", "ClassUIModel.__init__")
        self.setup_ui_finished = False
        "是否已经完成UI设置"
        self.window_info = WindowInfo()
        "窗口绘制信息"
        super().__init__(
            current_user=current_user, 
            class_name=class_name, 
            class_key=class_key, 
            save_path=save_path
        )
        self.setupUi(self) # type: ignore
        self.setup_ui_finished = True

if TYPE_CHECKING:
    MixinSuperType = ClassUIModel
    MixinChildType = object
else:
    MixinSuperType = object
    MixinChildType = ClassUIModel


