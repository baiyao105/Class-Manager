"""
用户信息显示相关模型。
"""

from __future__ import annotations

import os
import math
import json
import random
from typing import Any, Generator, Callable
import requests

from utils.algorithm import steprange
from utils.consts import runtime_flags
from utils.basetypes import Base
from utils.classobjects import ScoreModification, ScoreModificationTemplate
from utils.functions import question_chooose
from utils.qtconfig import (
    Signal, Slot, QWidget, QPoint, QTimer,
    Qt, QGuiApplication, QMoveEvent
)
from utils.profiler import profile

from widgets import WTFWidget, AboutWidget, SettingWidget

from .class_ui_model import MixinSuperType

def run_animation(generator_func: Callable[[], Generator[int, None, None]]) -> None:
    """
    运行动画。
    
    :param generator_func: 生成器函数，每帧yield一个延迟时间（毫秒）
    """
    def next_step() -> None:
        try:
            delay = next(generator)
            QTimer.singleShot(delay, next_step)
        except StopIteration:
            pass
    
    generator = generator_func()
    next_step()

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
        self.gravity = 0.25
        "重力模拟的重力加速度"
        self.window_bounce_factor = 0.8
        "窗口重力模拟碰到边缘的反弹系数"
        self.mouse_velocity_factor = 1.6
        "鼠标拖拽速度的系数"
        self.gravity_enabled = False
        "是否启用重力"
        self.gravity_timer = QTimer(self)
        "重力模拟的计时器"
        self.drag_release_timer = QTimer(self)
        "检测鼠标抓取和释放的计时器"
        self.velocity_x = 0.0
        "水平速度"
        self.velocity_y = 0.0
        "垂直速度"
        self.current_x = 0.0
        "当前x坐标"
        self.current_y = 0.0
        "当前y坐标"
        self.is_dragging = False
        "是否正在拖拽"
        self.programmatic_move = False
        "是否是代码操作的移动"
        self.mouse_velocity_x = 0.0
        "鼠标水平速度"
        self.mouse_velocity_y = 0.0
        "鼠标垂直速度"
        self.last_window_pos = None
        "上次窗口位置"
        self.about_window: AboutWidget | None = None
        "关于窗口"
        self.setting_window: SettingWidget | None = None
        "设置窗口"

        self.refresh_hint_widget()
        self.signal_dont_click.connect(self.slot_dont_click)
        self.signal_refresh_hint_widget.connect(self.slot_refresh_hint_widget)
        self.pushButton.clicked.connect(self.dont_click)
        self.pushButton_3.clicked.connect(self.about_this)
        self.pushButton_4.clicked.connect(self.open_setting_window)
        self.gravity_timer.timeout.connect(self._update_gravity)
        self.gravity_timer.setInterval(16)
        self.drag_release_timer.timeout.connect(self._check_mouse_release)
        self.drag_release_timer.setInterval(50)



    @profile("refresh_hint_widget")
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
    @profile("slot_dont_click")
    def slot_dont_click(self, style: int):
        "千万别点被点击时的接口"
        self.stop_gravity_mode()
        style = random.randint(1, 11) if style == 0 else style
        self.log("I", f"按钮被点击，本次执行类型：{style}", "MainWindow.dont_click")

        if style == 1:
            os.startfile("https://www.bilibili.com/video/BV1GJ411x7h7/")

        elif style == 2:
            def anim() -> Generator[int, None, None]:
                for _ in range(1145):
                    self.move(random.randint(0, 1920), random.randint(0, 1080))
                    yield 2
                self.move(200, 100)
            
            run_animation(anim)

        elif style == 3:
            def anim() -> Generator[int, None, None]:
                for i in range(114):
                    x, y = self.geometry().topLeft().x(), self.geometry().topLeft().y()
                    move = int(1.2 ** (i // 5))
                    self.move(x, y + move)
                    yield 10
                self.move(200, 100)
            
            run_animation(anim)

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
            
            def anim() -> Generator[int, None, None]:
                for i in range(1, 360 * 5, 3):
                    x = int(math.sin(math.radians(i)) * 30 * i / 360 * 4)
                    y = int(math.cos(math.radians(i)) * 30 * i / 360 * 4)
                    self.move(orig_x + int(x), orig_y + int(y))
                    yield 2
                self.move(200, 100)
            
            run_animation(anim)

        elif style == 7:
            orig_pos: dict[QWidget, QPoint] = {}
            for obj in self.findChildren(QWidget):
                obj: QWidget
                orig_pos[obj] = obj.geometry().topLeft()

            def anim() -> Generator[int, None, None]:
                for _ in range(200):
                    for obj in self.findChildren(QWidget):
                        obj.move(
                            random.randint(0, self.width() // 2),
                            random.randint(0, self.height() // 2),
                        )
                    yield 20

                for obj in self.findChildren(QWidget):
                    try:
                        obj.move(orig_pos[obj].x(), orig_pos[obj].y())
                    except KeyError:
                        pass
            
            run_animation(anim)

        elif style == 8:
            
            def anim() -> Generator[int, None, None]:
                colors = [
                    "#FFFFFF", "#FF8080", "#FFFF80", "#80FF80",
                    "#80FFFF", "#8080FF", "#FF80FF", "#FFFFFF"
                ]
                
                orig_style = self.styleSheet()
                steps = 10
                for i in range(len(colors) - 1):
                    start_color = colors[i]
                    end_color = colors[i + 1]
                    r_steps = steprange(int(start_color[1:3], base=16), int(end_color[1:3], base=16), steps)
                    g_steps = steprange(int(start_color[3:5], base=16), int(end_color[3:5], base=16), steps)
                    b_steps = steprange(int(start_color[5:7], base=16), int(end_color[5:7], base=16), steps)
                    for r, g, b in zip(r_steps, g_steps, b_steps):
                        color = f"#{int(r):02X}{int(g):02X}{int(b):02X}"
                        self.setStyleSheet(f"background-color: {color};")
                        yield 20
                
                self.setStyleSheet(orig_style)
            
            run_animation(anim)

        elif style == 9:
            orig_x, orig_y = self.geometry().x(), self.geometry().y()
            
            def anim() -> Generator[int, None, None]:
                for _ in range(100):
                    offset_x = random.randint(-10, 10)
                    offset_y = random.randint(-10, 10)
                    self.move(orig_x + offset_x, orig_y + offset_y)
                    yield 20
                self.move(orig_x, orig_y)
            
            run_animation(anim)

        elif style == 10:
            orig_geometry = self.geometry()
            
            def anim() -> Generator[int, None, None]:
                for i in range(30):
                    scale = 1.0 + 0.3 * math.sin(i * 0.5)
                    new_width = int(orig_geometry.width() * scale)
                    new_height = int(orig_geometry.height() * scale)
                    
                    center_x = orig_geometry.x() + orig_geometry.width() // 2
                    center_y = orig_geometry.y() + orig_geometry.height() // 2
                    
                    self.setGeometry(
                        center_x - new_width // 2,
                        center_y - new_height // 2,
                        new_width,
                        new_height
                    )
                    yield 20
                
                self.setGeometry(orig_geometry)
            
            run_animation(anim)

        elif style == 11:
            self.information("要来力", "你有没有好奇为什么窗口可以浮起来？这难道不是违反物理学的吗？")
            self.velocity_x = random.randint(-15, 15)
            self.velocity_y = random.randint(-15, 15)
            self.enable_gravity()
            
     
    
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

    @profile("_update_gravity")
    def _update_gravity(self) -> None:
        """
        更新重力模拟结果。
        """
        if not self.gravity_enabled or self.is_dragging:
            return
        
        
        orig_x = self.current_x + self.velocity_x
        orig_y = self.current_y + self.velocity_y
        
        screen_geometry = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        screen_x = screen_geometry.x()
        screen_y = screen_geometry.y()
        
        window_width = self.width()
        window_height = self.height()

        if orig_x <= screen_x:
            orig_x = screen_x
            self.velocity_x = -self.velocity_x * self.window_bounce_factor
        elif orig_x >= screen_x + screen_width - window_width:
            orig_x = screen_x + screen_width - window_width
            self.velocity_x = -self.velocity_x * self.window_bounce_factor
        
        if orig_y <= screen_y:
            orig_y = screen_y
            self.velocity_y = -self.velocity_y * self.window_bounce_factor
        elif orig_y >= screen_y + screen_height - window_height:
            orig_y = screen_y + screen_height - window_height
            self.velocity_y = -self.velocity_y * self.window_bounce_factor
        
        self.velocity_y += self.gravity

        self.programmatic_move = True

        self.move(int(orig_x), int(orig_y))
        self.current_x = orig_x
        self.current_y = orig_y

    def move(self, *args: Any, **kwargs: Any) -> None:
        self.programmatic_move = True
        super().move(*args, **kwargs)

    def setGeometry(self, *args: Any, **kwargs: Any) -> None:
        self.programmatic_move = True
        super().setGeometry(*args, **kwargs)

    def enable_gravity(self, initial_velocity_x: float = 0.0, initial_velocity_y: float = 0.0) -> None:
        """
        启用重力模拟模式。
        
        :param initial_velocity_x: 初始水平速度
        :param initial_velocity_y: 初始垂直速度
        """
        self.velocity_x = initial_velocity_x
        self.velocity_y = initial_velocity_y
        self.current_x = self.x()
        self.current_y = self.y()
        self.gravity_enabled = True
        self.gravity_timer.start()
        Base.log("I", f"重力模式已启用，初始速度：vx={self.velocity_x:.2f}, vy={self.velocity_y:.2f}", "UserDisplayModel.enable_gravity")

    def disable_gravity(self) -> None:
        """
        禁用重力模拟模式。
        """
        self.gravity_enabled = False
        self.gravity_timer.stop()
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        Base.log("I", "重力模式已禁用", "UserDisplayModel.disable_gravity")

    def stop_gravity_mode(self) -> None:
        """
        停止重力模拟模式。
        """
        self.disable_gravity()

    @profile("moveEvent")
    def moveEvent(self, event: QMoveEvent) -> None:
        """
        窗口移动事件。
        
        这里用于检测窗口拖动。
        """
        if self.programmatic_move:
            self.programmatic_move = False
            super().moveEvent(event)
            return

        if self.gravity_enabled:
            left_pressed = QGuiApplication.mouseButtons() & Qt.MouseButton.LeftButton

            if left_pressed:
                if not self.is_dragging:
                    self.is_dragging = True
                    self.last_window_pos = self.pos()
                    self.drag_release_timer.start()
                    Base.log("I", f"用户拖动开始，位置: {self.last_window_pos.x()}, {self.last_window_pos.y()}", "UserDisplayModel.moveEvent")
                else:
                    current_pos = self.pos()
                    if self.last_window_pos:
                        self.mouse_velocity_x = current_pos.x() - self.last_window_pos.x()
                        self.mouse_velocity_y = current_pos.y() - self.last_window_pos.y()
                        Base.log("I", f"拖动中，速度: vx={self.mouse_velocity_x:.2f}, vy={self.mouse_velocity_y:.2f}", "UserDisplayModel.moveEvent")
                    self.last_window_pos = current_pos
            else:
                if self.is_dragging:
                    self._end_dragging()

        super().moveEvent(event)

    def _check_mouse_release(self) -> None:
        """
        检查鼠标是否释放。
        """
        left_pressed = QGuiApplication.mouseButtons() & Qt.MouseButton.LeftButton
        if not left_pressed and self.is_dragging:
            self._end_dragging()

    def _end_dragging(self) -> None:
        """
        结束拖动。
        """
        if self.is_dragging:
            self.is_dragging = False
            self.drag_release_timer.stop()
            self.velocity_x = self.mouse_velocity_x * self.mouse_velocity_factor
            self.velocity_y = self.mouse_velocity_y * self.mouse_velocity_factor
            self.current_x = self.x()
            self.current_y = self.y()
            Base.log("I", f"用户拖动结束，继承速度：vx={self.velocity_x:.2f}, vy={self.velocity_y:.2f}", "UserDisplayModel._end_dragging")

    def stop(self):
        self.stop_gravity_mode()
        widgets: list[QWidget | None] = [
            self.setting_window,
            self.about_window
        ]
        for widget in widgets:
            if widget:
                if isinstance(widget, SettingWidget):
                    widget.force_close(True)
                else:
                    widget.close()
        super().stop()