"""
用户信息显示相关模型。
"""

from __future__ import annotations

import os
import time
import math
import json
import random
import requests

from utils.algorithm import Thread
from utils.consts import runtime_flags
from utils.basetypes import Base
from utils.classobjects import ScoreModification, ScoreModificationTemplate
from utils.functions import question_chooose
from utils.qtconfig import (
    Signal, Slot, QWidget, QPoint, QCoreApplication
)

from widgets import WTFWidget, AboutWidget, SettingWidget

from .class_ui_model import MixinSuperType

class UserDisplayModel(MixinSuperType):
    """
    用户信息显示有关的模型。
    """

    signal_refresh_hint_widget = Signal(int)
    "刷新提示(屏幕右上角的)文本信号"

    signal_dont_click = Signal(int)
    "千万别点被点击了"

    def __init__(
            self, 
            current_user: str, 
            class_name: str, 
            class_key: str, 
            save_path: str | None = None
        ):
        Base.log("D", "初始化UserDisplayModel", "UserDisplayModel.__init__")

        self.about_window: AboutWidget | None = None
        "关于窗口"
        self.setting_window: SettingWidget | None = None
        "设置窗口"
        self.CardWidget_2.clicked.connect(
            lambda: Thread(target=self.refresh_hint_widget).start()
        )
        self.signal_dont_click.connect(self.slot_dont_click)
        self.signal_refresh_hint_widget.connect(self.slot_refresh_hint_widget)
        self.pushButton.clicked.connect(self.dont_click)
        self.pushButton_3.clicked.connect(self.about_this)
        self.pushButton_4.clicked.connect(self.open_setting_window)



    def refresh_hint_widget(self, mode: int = 0):
        """
        刷新提示

        :param mode: 模式，按照范围划分
        """
        self.signal_refresh_hint_widget.emit(mode)

    @Slot(int)
    def slot_refresh_hint_widget(self, mode: int = 0):
        "刷新提示的接口"
        Base.log("I", f"刷新提示，当前模式：{mode}", "MainWindow.refresh_hints")
        mode = mode or random.randint(0, 100)
        tip_refresh = "hint_widget_tip_refresh" not in runtime_flags
        if tip_refresh:
            runtime_flags["hint_widget_tip_refresh"] = True
        if mode < 20:
            with open("utils/data/hints.txt", encoding="utf-8") as f:
                hints = [
                    l.replace("^#", "#")
                    for l in f.read().splitlines()
                    if ((not l.startswith("#")) and l.strip())
                ]
            self.label_22.setText(
                random.choice(hints) + ("\n（点击刷新）" if tip_refresh else "")
            )

        else:
            try:
                Base.log("I", "获取一言", "MainWindow._refresh_hint_widget")
                self.label_23.setText("一言")
                text = requests.get("https://v1.hitokoto.cn", timeout=0.5).text
                Base.log("I", f"返回：{text}", "MainWindow._refresh_hint_widget")
                req = json.loads(text)
                text = req["hitokoto"] + "\n\t- " + req["from"]
                self.label_22.setText(text)
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                Base.log(
                    "W",
                    f"获取一言失败，错误类型：{e.__class__.__name__}",
                    "MainWindow.refresh_hints",
                )
                with open("utils/data/hints.txt", encoding="utf-8") as f:
                    hints = [
                        l.replace("^#", "#")
                        for l in f.read().splitlines()
                        if ((not l.startswith("#")) and l.strip())
                    ]
                self.label_23.setText("Tip:")
                self.label_22.setText(
                    random.choice(hints)
                )
    

    @Slot(int)
    def dont_click(self, style: int | None = 0):
        "处理特殊按钮点击事件，触发随机彩蛋效果"
        if "tip_dont_click" not in runtime_flags:
            question_chooose(
                self,
                "警告",
                "该功能为危险功能，作者不会为它所造成的后果承担责任。\n"
                "无论如何都要继续吗？",
                ["确定", "确定", "确定"],
                msg_type="warning",
            )
            runtime_flags["tip_dont_click"] = True
        self.signal_dont_click.emit(style)

    @Slot(int)
    def slot_dont_click(self, style: int):
        "千万别点被点击时的接口"
        style = random.randint(1, 7) if style == 0 else style
        self.log("I", f"按钮被点击，本次执行类型：{style}", "MainWindow.dont_click")

        if style == 1:
            os.startfile("https://www.bilibili.com/video/BV1GJ411x7h7/")

        elif style == 2:
            for _ in range(1145):
                self.move(random.randint(0, 1920), random.randint(0, 1080))
            self.move(200, 100)

        elif style == 3:
            for i in range(114):
                x, y = self.geometry().topLeft().x(), self.geometry().topLeft().y()
                move = int(1.2 ** (i // 5))
                self.move(x, y + move)
                time.sleep(0.01)
            self.move(200, 100)

        elif style == 4:
            for _ in range(8):
                w = WTFWidget(self)
                w.show()

        elif style == 5:
            if not self.target_class:
                return
            self.send_modify_instance(
                [
                    ScoreModification(
                        ScoreModificationTemplate(
                            "fly_in_class",
                            -114.0,
                            "在课堂上飞起来",
                            "装___我让你________",
                        ),
                        s,
                    )
                    for s in self.target_class.students.values()
                ]
            )
            self.show_tip("提示", "可以通过撤销上一步恢复", duration=10000)

        elif style == 6:
            orig_x, orig_y = (
                self.geometry().topLeft().x(),
                self.geometry().topLeft().y(),
            )
            for i in range(1, 360 * 10, 3):
                x = int(math.sin(math.radians(i)) * 30 * i / 360 * 4)
                y = int(math.cos(math.radians(i)) * 30 * i / 360 * 4)
                self.move(orig_x + int(x), orig_y + int(y))
                time.sleep(0.01)
            self.move(200, 100)

        elif style == 7:
            orig_pos: dict[QWidget, QPoint] = {}
            for obj in self.findChildren(QWidget):
                obj: QWidget
                orig_pos[obj] = obj.geometry().topLeft()

            for i in range(200):
                for obj in self.findChildren(QWidget):
                    obj.move(
                        random.randint(0, self.width() // 2),
                        random.randint(0, self.height() // 2),
                    )
                QCoreApplication.processEvents()
                time.sleep(0.01)

            for obj in self.findChildren(QWidget):
                try:
                    obj.move(orig_pos[obj].x(), orig_pos[obj].y())
                except KeyError:
                    pass
    
    
    def about_this(self):
        """
        显示关于信息窗口。
        """
        Base.log("I", "显示关于", "OperationModel.about")
        self.about_window = AboutWidget(self)
        self.about_window.show()

    def open_setting_window(self):
        """
        打开设置窗口。
        """
        Base.log("I", "打开设置窗口", "OperationModel.setting_window")
        self.setting_window = SettingWidget(setting=self, master=self)
        self.setting_window.show()

    def stop(self):
        widgets: list[QWidget | None] = [
            self.setting_window,
            self.about_window
        ]
        for widget in widgets:
            if widget:
                widget.close()
        super().stop()