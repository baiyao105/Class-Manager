"""
和历史记录相关的模型。
"""

from __future__ import annotations

import sys
import time
from queue import Queue
from typing import Any, Callable, TypeAlias
from concurrent.futures import ThreadPoolExecutor

from utils.algorithm import Thread
from utils.basetypes import Base
from utils.functions.numbers import steprange
from utils.qtconfig import (
    QListWidgetItem, QColor, Slot, 
    QModelIndex, Qt, QAbstractItemView
)

from .class_ui_model import MixinSuperType


CallableWithNoArgsNeeded: TypeAlias = Callable[..., Any]
ColorDataType: TypeAlias = tuple[int, int, int, int, int, int]
ActionInfoDataType: TypeAlias = tuple[str, CallableWithNoArgsNeeded, ColorDataType, int]

class ActionHistoryModel(MixinSuperType):
    """
    操作记录列表模型。
    """

    flash_executor = ThreadPoolExecutor(max_workers=128, thread_name_prefix="FlashAnimation")

    def __init__(self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化ActionHistoryModel", "ActionHistoryModel.__init__")

        self.listWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.insert_queue: Queue[ActionInfoDataType] = Queue()
        "在主窗口左侧listWidget插入项的队列"
        self.listView_data: list[CallableWithNoArgsNeeded] = []
        "listWidge数据，用于存储主窗口侧边存储历史操作记录的listWidget里面的命令（对应里面的每一项）"
        self.insert_action_history_thread: Thread = Thread(
            target=self.insert_action_history_info_while_alive,
            daemon=True,
            name="InsertActionHistoryThread"
        )
        self.insert_action_history_thread.start()
        self.listWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listWidget.doubleClicked.connect(self.click_opreation)

    def insert_action_history_info_while_alive(self):
        """
        插入操作记录的线程。
        """
        while self.is_running and not self.should_stop:
            try:
                text, command, insert_fade, fade_step = self.insert_queue.get()
                Base.log(
                    "I",
                    f"插入操作记录：名称{repr(text)}， 命令{repr(command)}",
                    "ActionHistoryModel.insert_action",
                )
                item = QListWidgetItem(text)
                self.listWidget.insertItem(0, item)
                self.listView_data.insert(0, command)
                self.listWidget.scrollToTop()

                def flash(item: QListWidgetItem, insert_fade: tuple[int, int, int, int, int, int], fade_step: int):
                    for r, g, b in list(
                        zip(
                            steprange(insert_fade[0], insert_fade[3], fade_step),
                            steprange(insert_fade[1], insert_fade[4], fade_step),
                            steprange(insert_fade[2], insert_fade[5], fade_step),
                        )
                    ):

                        item.setBackground(QColor(int(r), int(g), int(b)))
                        time.sleep(0.02)

                self.flash_executor.submit(flash, item, insert_fade, fade_step)

            except Exception as e:
                Base.log(
                    "E",
                    f"插入操作线程异常：[{sys.exc_info()[1].__class__.__name__}] {repr(e)}",
                    "ActionHistoryModel.insert_action_thread",
                )
        if self.should_stop:
            Base.log(
                "I",
                "self.should_stop = True，操作记录插入线程已停止",
                "ActionHistoryModel.insert_action_thread",
            )

    def insert_action_history_info(
        self,
        text: str,
        func: CallableWithNoArgsNeeded,
        color: tuple[int, int, int, int, int, int] = (127, 225, 195, 255, 255, 255),
        stepcount: int = 12,
    ):
        """
        插入操作历史项目

        :param text: 插入的文本
        :param click_callback: 项目被双击时的回调函数
        :param insert_fade: 插入的渐变颜色，前三项是起始颜色，后三项是结束颜色（rgb）
        :param stepcount: 渐变步长（是老版的参数名，懒得改了，费时间）
        """
        self.insert_queue.put((text, func, color, stepcount))

    @Slot(QModelIndex)
    def click_opreation(self, index: QModelIndex):
        """
        点击历史信息列表项的操作处理函数

        :index: 传过来的索引，不用管（是自动的）
        """
        Base.log(
            "I",
            f"点击列表项:{index.row()}, {repr(self.listView_data[index.row()])}",
            "ActionHistoryModel.click_opreation",
        )
        self.listView_data[index.row()]()