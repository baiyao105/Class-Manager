"""
我的主窗口
"""

import time
import platform
import warnings
from typing import Union, Any

from utils.settings import SettingsInfo
from utils.basetypes import Base

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from widgets.basic.MyMainWindow import MyMainWindow


__all__ = ["MyWidget"]

class MyWidget(QWidget):
    "自定义子窗口基类，包含动画效果"

    def __init__(self, master: Union["MyMainWindow", "MyWidget"] = None):
        """
        初始化

        :param master: 父窗口，默认会浮在父窗口上面
        """
        super().__init__()
        self.is_running = True
        self.master = master
        if self.master is None:
            self.master = MyMainWindow.main_instance
        self.centralwidget = master
        self.setParent(master)
        Base.log("I", "子窗口创建", "MyWidget")
        self.setWindowFlags(
            (
                Qt.WindowType.WindowCloseButtonHint
                | Qt.WindowType.MSWindowsFixedSizeDialogHint
                | Qt.WindowType.WindowTitleHint
                | Qt.WindowType.WindowSystemMenuHint
                | Qt.WindowType.Window
            )
        )
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.startanimation: QPropertyAnimation = None
        self.closeanimation_1: QPropertyAnimation = None
        self.closeanimation_2: QPropertyAnimation = None



    if platform.system() != "Windows":
        warnings.warn("非Windows系统可能无法正常使用动画效果")

        def resize(self, *args, **kwargs):
            "调整大小"
            super().setFixedSize(*args, **kwargs)

    def create_animation(
        self,
        property_name: Union[QByteArray, bytes, bytearray, "memoryview[int]"],
        duration: int,
        start_value: Any,
        end_value: Any,
        easing_curve: Union[
            QEasingCurve, QEasingCurve.Type
        ] = QEasingCurve.Type.OutCubic,
    ):
        """
        创建通用动画

        Args:
            property_name: 目标属性名
            duration: 动画持续时间(毫秒)
            start_value: 起始值
            end_value: 结束值
            easing_curve: 缓动曲线类型

        Returns:
            配置好的QPropertyAnimation对象
        """
        animation = QPropertyAnimation(self, property_name)
        animation.setEasingCurve(easing_curve)
        animation.setDuration(
            duration / SettingsInfo.current.animation_speed
            if SettingsInfo.current.animation_speed > 0
            else duration
        )
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        return animation

    def showStartAnimation(self):
        "执行窗口显示动画"
        self.is_running = True
        if SettingsInfo.current.animation_speed <= 114514:
            # 计算动画终点位置
            if self.master:
                endpoint = (
                    self.master.geometry().topLeft()
                    + QPoint(
                        self.master.geometry().width() / 2,
                        self.master.geometry().height() / 2,
                    )
                    - QPoint(self.geometry().width() / 2, self.geometry().height() / 2)
                    + QPoint(SettingsInfo.current.subwindow_x_offset, SettingsInfo.current.subwindow_y_offset)
                )

                # 计算动画起点位置
                startpoint = QPoint(
                    endpoint.x(),
                    QGuiApplication.primaryScreen().availableGeometry().height()
                    + QGuiApplication.primaryScreen().availableGeometry().top(),
                )

            else:
                # 如果没有父窗口就默认以屏幕中心为最终位置
                endpoint = (
                    QPoint(
                        QGuiApplication.primaryScreen().availableGeometry().width() / 2,
                        QGuiApplication.primaryScreen().availableGeometry().height() / 2,
                    )
                    - QPoint(self.geometry().width() / 2, self.geometry().height() / 2)
                    + QPoint(SettingsInfo.current.subwindow_x_offset, SettingsInfo.current.subwindow_y_offset)
                    )
                
                startpoint = QPoint(
                    endpoint.x(),
                    QGuiApplication.primaryScreen().availableGeometry().height()
                    + QGuiApplication.primaryScreen().availableGeometry().top(),
                )
                

            # 使用通用动画创建方法
            self.startanimation = self.create_animation(
                b"pos", 400, startpoint, endpoint
            )
            self.startanimation.start()


    def showCloseAnimation(self):
        "执行窗口关闭动画"
        self.is_running = False

        if SettingsInfo.current.animation_speed <= 114514:

            # 第一阶段动画：向上移动
            Base.log("D", "关闭动画进入第一阶段", "MyWidget.showCloseAnimation")

            startpoint = QPoint(self.x(), self.y())
            endpoint = QPoint(startpoint.x(), self.y() - 75)

            # 使用通用动画创建方法
            self.closeanimation_1 = self.create_animation(
                b"pos", 150, startpoint, endpoint, QEasingCurve.Type.OutQuad
            )

            self.closeanimation_1.start()
            close_anim_loop_1 = QEventLoop(self)
            self.closeanimation_1.finished.connect(close_anim_loop_1.quit)
            close_anim_loop_1.exec()
            # 防止他们在窗口还在执行动画就又按了一次关闭按钮
            
            # 第二阶段动画：移出屏幕
            Base.log("D", "关闭动画进入第二阶段", "MyWidget.showCloseAnimation")
            startpoint = QPoint(self.x(), self.y())
            endpoint = QPoint(
                startpoint.x(),
                QGuiApplication.primaryScreen().availableGeometry().top()
                + QGuiApplication.primaryScreen().availableGeometry().height(),
            )
            # 使用通用动画创建方法
            self.closeanimation_2 = self.create_animation(
                b"pos", 230, startpoint, endpoint, QEasingCurve.Type.InQuad
            )
            self.closeanimation_2.start()
    
            close_anim_loop_2 = QEventLoop(self)
            self.closeanimation_2.finished.connect(close_anim_loop_2.quit)
            close_anim_loop_2.exec()

            Base.log("D", "关闭动画展示完成，关闭窗口", "MyWidget.showCloseAnimation")
            self.hide()
            self.move(startpoint)  # 把窗口移回起点，不然如果下次启动如果没有动画窗口就会卡在屏幕下边
        

    def closeEvent(self, event: QCloseEvent):
        """
        关闭事件处理器
        
        :param event: 传过来的关闭事件
        """
        self.is_running = False
        self.showCloseAnimation()
        self.hide()
        event.accept()

    def show(self):
        "展示窗口"
        self.is_running = True
        if self.master:
            pos = (
                self.master.geometry().topLeft()
                + QPoint(
                    self.master.geometry().width() / 2,
                    self.master.geometry().height() / 2,
                )
                - QPoint(self.geometry().width() / 2, self.geometry().height() / 2)
                + QPoint(SettingsInfo.current.subwindow_x_offset, SettingsInfo.current.subwindow_y_offset)
            )

        else:
            pos = (QPoint(
                QGuiApplication.primaryScreen().availableGeometry().width() / 2,
                QGuiApplication.primaryScreen().availableGeometry().height() / 2,
            )
                - QPoint(self.geometry().width() / 2, self.geometry().height() / 2)
                + QPoint(SettingsInfo.current.subwindow_x_offset, SettingsInfo.current.subwindow_y_offset)
            )
        
        self.move(pos)
        super().show()
        if SettingsInfo.current.animation_speed <= 114514:
            self.showStartAnimation()

    def orig_show(self):
        "原生的展示函数"
        super().show()




    def hide(self):
        self.is_running = False
        super().hide()

    def destroy(self):
        self.is_running = False
        super().destroy()

    def center(self):
        "将窗口居中显示在屏幕上"
        screen = QGuiApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2
        )

    def setTopmost(self, topmost: bool = True):
        """
        设置窗口置顶

        :param topmost: 是否置顶，默认是
        """
        if topmost:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
        self.show()
