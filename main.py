# -*- coding: utf-8 -*-
# 奇怪的癖好：把import语句的顺序按长短排列（？
import os
import sys
import time
import copy
import math
import enum
import random
import psutil
import pickle
import signal
import requests
import platform
import warnings
import customtkinter  # pylint: disable=unused-import
import traceback
import threading
import functools
import dill as pickle  # pylint: disable=shadowed-import
import numpy as np
import pyqtgraph as pg
from queue import Queue
from typing import Optional, Union, List, Tuple, Dict, Any, Callable, Literal, Type
from shutil import copytree, rmtree, copy as shutil_copy
from concurrent.futures import ThreadPoolExecutor
from types import TracebackType
from PySide6.QtCore import *  # pylint: disable=wildcard-import, unused-wildcard-import
from PySide6.QtGui import *  # pylint: disable=wildcard-import, unused-wildcard-import
from PySide6.QtWidgets import *  # pylint: disable=wildcard-import, unused-wildcard-import
from qfluentwidgets.common import *  # pylint: disable=wildcard-import, unused-wildcard-import
from qfluentwidgets.components import *  # pylint: disable=wildcard-import, unused-wildcard-import
from qfluentwidgets.window import *  # pylint: disable=wildcard-import, unused-wildcard-import
from qfluentwidgets.multimedia import *  # pylint: disable=wildcard-import, unused-wildcard-import

from ui.py import (
    AttendanceInfoEdit,
    MainClassWindow,
    WTF,
    StudentWindow,
    MultiSelectWindow,
    NewTemplateWindow,
    EditTemplateWindow,
    ModifyHistoryWindow,
    SelectTemplateWindow,
    SettingWindow,
    AchievementWindow,
    GroupWindow,
    NoticeViewer,
    CleaingScoreSumUp,
    NoiseDetector,
    RandomSelector,
    AttendanceInfoView,
    HomeworkScoreSumUp,
    About,
    DebugWindow,
)

from utils.classobjects import (    # pylint: disable=unused-import
    sys as base_sys,
    Class,
    Student,  
    Achievement,
    AchievementTemplate,
    ScoreModification,
    ScoreModificationTemplate,
    StrippedStudent,
    AttendanceInfo,
    DayRecord,
    ClassStatusObserver,
    AchievementStatusObserver,
    Group,
    HomeworkRule,
    dummy_student,
    History,
    Stack,
    Base,
    ClassObj,
    DEFAULT_CLASSES,
    DEFAULT_ACHIEVEMENTS,
    DEFAULT_SCORE_TEMPLATES,
    default_user,
)

from utils.functions import steprange, play_sound, play_music, stop_music, Thread
from utils.classobjects import (
    CORE_VERSION,
    CORE_VERSION_CODE,
    VERSION_INFO,
    CLIENT_UPDATE_LOG,
    DEFAULT_CLASS_KEY,
)
from utils.classobjects import Chunk, UserDataBase
from utils.consts import (
    app_style,
    app_stylesheet,
    nl,
    enable_memory_tracing,
    runtime_flags,
)
from utils.widgets import ObjectButton, ProgressAnimatedListWidgetItem, SideNotice
from utils.functions import question_yes_no as question_yes_no_orig, question_chooose
from utils.functions import format_exc_like_java
from utils.settings import SettingsInfo
from utils.system import output_list
from utils.basetypes import logger
from utils.basetypes import DataObject
import utils.functions.prompts as PromptUtils

sys.stdout = Base.captured_stdout
"重定向的标准输出"
sys.stderr = Base.captured_stderr
"重定向的错误输出"

try:
    from utils.login import login
except ImportError:
    from utils.bak.login import login

    warnings.warn(
        "没有自定义登录模块，将使用默认，"
        "如果需要自定义登录模块请创建/修改utils/login.py"
    )


base_sys.stdout = Base.captured_stdout
"重定向的核心模块标准输出"
base_sys.stderr = Base.captured_stderr
"重定向的核心模块错误输出"

ExceptionInfoType = Tuple[Type[BaseException], BaseException, TracebackType]
"""异常信息类型"""

CLIENT_VERSION: str = VERSION_INFO["client_version"]
"应用程序界面版本"
CLIENT_VERSION_CODE: str = VERSION_INFO["client_version_code"]
"应用程序界面版本编码"

settings: SettingsInfo = SettingsInfo.current
"全局设置对象"

widget: "ClassWindow"
"主窗口实例"

ctrlc_times = 0
"中断信号计数器"

if not enable_memory_tracing:

    def profile(precision=4):  # NOSONAR; pylint: disable=unused-argument
        def decorator(func):
            return func

        return decorator

else:
    try:
        from memory_profiler import profile
    except ImportError:
        warnings.warn(
            "memory_profiler模块未安装, 相关性能分析功能将被禁用", RuntimeWarning
        )

        def profile(precision=4):  # NOSONAR; pylint: disable=unused-argument
            def decorator(func):
                return func

            return decorator

        Base.log("W", "memory_profiler模块未安装,相关性能分析功能将被禁用")


last_process_time = 0
"上次处理QCoreApplication.processEvents的时间"

max_process_rate = 120
"最大处理QCoreApplication.processEvents的频率"


def do_nothing():
    "啥也不干，让程序摸鱼一会"
    global last_process_time
    if time.time() - last_process_time > 1 / max_process_rate:
        last_process_time = time.time()
        QCoreApplication.processEvents()


def exception_handler(
    exc_type: Optional[Type[BaseException]] = None,
    exc_val: Optional[BaseException] = None,
    exc_tb: Optional[TracebackType] = None,
):
    """
    捕获未处理的异常并显示错误对话框

    用作sys.excepthook的处理函数
    """
    file_basename = os.path.basename(__file__)
    file_path = __file__.replace(os.getcwd(), "").lstrip("\\/")
    # 绑定上下文信息
    exc_info = (
        ["捕获到异常！\n"]
        + traceback.format_exception(exc_type, exc_val, exc_tb)
        + ["\n"]
    )
    logger.bind(
        file=file_basename,
        full_file=file_path,
        source="exception_handler",
        lineno=110,
        source_with_lineno="exception_handler:110",
    ).exception("Uncaught exception occurred", exc_info=exc_val)
    Base.log_exc("捕获到异常", "exception_handler", exc=exc_val)
    pagesize = 20
    pagemaxchars = 1000
    total = int(np.ceil(len(exc_info) / pagesize))
    index = 0
    try:
        parent = widget
        for i in range(total):
            currenttext = exc_info[i * pagesize : (i + 1) * pagesize]
            for j in range(math.ceil(len(currenttext) / pagemaxchars)):
                index += 1
                parent.critical(
                    "错误",
                    "".join(
                        currenttext[j * pagemaxchars : (j + 1) * (pagemaxchars + 1)]
                    )
                    + f"\n\t\t\t(页码{index}/{total})",
                )
    except (NameError, RuntimeError):
        parent = None
        for i in range(total):
            currenttext = exc_info[i * pagesize : (i + 1) * pagesize]
            for j in range(math.ceil(len(currenttext) / pagemaxchars)):
                index += 1
                box = QMessageBox()
                box.setWindowTitle("错误")
                box.setText(
                    "".join(
                        currenttext[j * pagemaxchars : (j + 1) * (pagemaxchars + 1)]
                    )
                )
                box.setInformativeText(f"(页码{index}/{total})")
                box.setIcon(QMessageBox.Icon.Critical)
                box.exec()


sys.excepthook = exception_handler
base_sys.excepthook = exception_handler
threading.excepthook = exception_handler


if sys.version_info < (3, 8):
    warnings.warn(
        f"建议使用Python3.8及以上的版本运行（当前为{sys.version_info.major}.{sys.version_info.minor}）"
    )

if sys.platform != "win32":
    warnings.warn("本程序目前主要支持Windows操作系统，其他操作系统可能无法正常运行")


HAS_PYAUDIO: bool = False
"PyAudio库可用性标志"
HAS_CV2: bool = False
"OpenCV库可用性标志"

try:
    import pyaudio

    HAS_PYAUDIO = True
except ImportError:
    pass

try:
    import cv2

    HAS_CV2 = True
except ImportError:
    pass


def question_yes_no(
    master: Optional[QWidget],
    title: str,
    text: str,
    default: bool = True,
    msg_type: Literal["question", "information", "warning", "critical"] = "question",
    pixmap: Optional[QPixmap] = None,
) -> bool:
    "显示是/否对话框并返回用户选择"
    Base.log(
        "I",
        f"询问框：{repr(title)} - {repr(text)}，"
        f"default={repr(default)}，type={repr(msg_type)}，pixmap={repr(pixmap)}",
    )
    return question_yes_no_orig(master, title, text, default, msg_type, pixmap)


def handle_fatal_qt_error(msg: str):
    """处理Qt致命错误并安全退出程序"""
    Base.log("F", "PySide6发生致命错误", "MainThread")
    widget.save_current_settings()
    widget.save_data()
    widget.critical("错误", f"PySide6发生致命错误\n错误信息：\n {msg}")
    widget.closeEvent(QCloseEvent(), do_tip=False)
    widget.destroy()
    Base.log("F", "程序退出", "MainThread")
    sys.exit(0)


def qt_messagehandler(
    mode: QtMsgType, context: QMessageLogContext, msg: str
):  # pylint: disable=unused-argument
    """自定义Qt消息处理函数，使用字典映射优化日志记录"""
    # 使用字典映射消息类型到日志级别
    msg_type_map = {
        QtMsgType.QtDebugMsg: "D",
        QtMsgType.QtInfoMsg: "I",
        QtMsgType.QtWarningMsg: "W",
        QtMsgType.QtCriticalMsg: "C",
        QtMsgType.QtFatalMsg: "F",
    }

    # 记录日志
    log_level = msg_type_map.get(mode, "I")  # 默认为Info级别
    Base.log(log_level, msg, "PySide6")

    # 处理致命错误
    if mode == QtMsgType.QtFatalMsg:
        handle_fatal_qt_error(msg)


qInstallMessageHandler(qt_messagehandler)
QLoggingCategory.setFilterRules("*.*=true\n*.debug=false\n*.info=false")
# 让Qt把除了debug和info以外的日志都输出到qtmessagehandler


class MyMainWindow(QMainWindow):
    """主应用程序窗口类"""

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.setTopmost(True)
        self.move(200, 110)
        self.setWindowFlags(
            (
                Qt.WindowType.WindowCloseButtonHint
                | Qt.WindowType.MSWindowsFixedSizeDialogHint
                | Qt.WindowType.WindowTitleHint
                | Qt.WindowType.WindowSystemMenuHint
                | Qt.WindowType.Window
            )
        )
        self.close_count = 0
        self.clear_time_timer = QTimer()
        self.clear_time_timer.timeout.connect(self.clear_close_count)
        self.clear_time_timer.start(30000)

    @Slot()
    def clear_close_count(self):
        self.close_count = 0

    def setTopmost(self, topmost: bool = True):
        "设置窗口置顶状态"
        if topmost:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
        self.show()

    def closeEvent(self, event: QCloseEvent, tip=True) -> bool:
        "处理窗口关闭事件"
        Base.log("I", "主窗口尝试退出", "MyMainWindow")
        self.close_count += 1
        if tip:
            if self.isEnabled():
                reply = question_yes_no(
                    self,
                    "提示",
                    "确定退出？" if self.close_count <= 5 else "确认退出程序？",
                )
                # 判断返回结果处理相应事项
                if reply:
                    Base.log("I", "确认退出", "MyMainWindow")
                    event.accept()
                    self.is_running = False
                    return True

                else:
                    Base.log("I", "取消退出", "MyMainWindow")
                    event.ignore()
                    return False
            else:
                Base.log("I", "子窗口未关闭，无法退出", "MyMainWindow")
                event.ignore()
                return False
        else:
            Base.log("I", "退出", "MyMainWindow")
            event.accept()
            self.is_running = False
            return True


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
            self.master = widget
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
        self.closeanimation: QPropertyAnimation = None

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
            duration / widget.animation_speed
            if widget.animation_speed > 0
            else duration
        )
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        return animation

    def showStartAnimation(self):
        "执行窗口显示动画"
        self.is_running = True
        if widget.animation_speed <= 114514:
            # 计算动画终点位置
            endpoint = (
                self.master.geometry().topLeft()
                + QPoint(
                    self.master.geometry().width() / 2,
                    self.master.geometry().height() / 2,
                )
                - QPoint(self.geometry().width() / 2, self.geometry().height() / 2)
                + QPoint(widget.subwindow_x_offset, widget.subwindow_y_offset)
            )

            # 计算动画起点位置
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
        super().show()
        if widget.animation_speed <= 114514:
            # 第一阶段动画：向上移动
            startpoint = QPoint(self.x(), self.y())
            endpoint = QPoint(startpoint.x(), self.y() - 75)

            # 使用通用动画创建方法
            self.closeanimation = self.create_animation(
                b"pos", 150, startpoint, endpoint, QEasingCurve.Type.OutQuad
            )
            self.closeanimation.start()

            # 等待第一阶段动画完成
            while self.closeanimation.state() != QAbstractAnimation.State.Stopped:
                do_nothing()

            # 第二阶段动画：移出屏幕
            startpoint = QPoint(self.x(), self.y())
            endpoint = QPoint(
                startpoint.x(),
                QGuiApplication.primaryScreen().availableGeometry().top()
                + QGuiApplication.primaryScreen().availableGeometry().height(),
            )
            # 使用通用动画创建方法
            self.closeanimation = self.create_animation(
                b"pos", 230, startpoint, endpoint, QEasingCurve.Type.InQuad
            )
            self.closeanimation.start()

            # 等待第二阶段动画完成
            while self.closeanimation.state() != QAbstractAnimation.State.Stopped:
                do_nothing()
            self.hide()
            self.move(
                startpoint
            )  # 把窗口移回起点，不然如果下次启动如果没有动画窗口就会卡在屏幕下边

    def show(self):
        self.is_running = True
        self.move(
            (
                self.master.geometry().topLeft()
                + QPoint(
                    self.master.geometry().width() / 2,
                    self.master.geometry().height() / 2,
                )
                - QPoint(self.geometry().width() / 2, self.geometry().height() / 2)
                + QPoint(widget.subwindow_x_offset, widget.subwindow_y_offset)
            )
        )
        super().show()
        if widget.animation_speed <= 114514:
            self.showStartAnimation()

    def close(self):
        self.is_running = False
        self.closeEvent(QCloseEvent())

    def closeEvent(self, event: QCloseEvent):
        self.is_running = False
        if widget.animation_speed <= 114514:
            self.showCloseAnimation()
        self.hide()
        event.accept()

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


WidgetType = Union[
    QMainWindow, QWidget, QFrame, QStackedWidget, QScrollArea, MyMainWindow, MyWidget
]


class Command:
    """快捷命令"""

    def __init__(
        self,
        key: str,
        name: str,
        _callable: str,
        for_which: Optional[Union[str, object]] = "MainWindow",
    ):
        self.name = name
        self.callable = _callable
        self.key = key
        self.usage = 0
        self.orig_func = lambda: None
        self.for_which = for_which

    def __repr__(self):
        return (
            f"Command(key={repr(self.key)}, "
            f"name={repr(self.name)}, callable={repr(self.callable)})"
        )


command_list: List[Command] = []
"快捷命令列表"
lately_used_commands: List[Command] = []
"最近使用命令列表"


def as_command(
    key: str, name: str, for_which: Optional[Union[str, object]] = "MainWindow"
):
    """
    快捷命令装饰器。

    :param key: 键值
    :param name: 命令名称
    """
    global lately_used_commands

    def decorator(func):
        global lately_used_commands
        cmd = Command(key, name, func, for_which)
        command_list.append(cmd)
        cmd.orig_func = func

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cmd.usage += 1
            if cmd not in lately_used_commands:
                lately_used_commands.append(cmd)
            else:
                lately_used_commands.remove(cmd)
                lately_used_commands.append(cmd)
            return func(*args, **kwargs)

        cmd.callable = wrapper
        return wrapper

    return decorator


class ClassWindow(ClassObj, MainClassWindow.Ui_MainWindow, MyMainWindow):
    """班级窗口实例化"""

    ##### 信号 #####

    log_update = Signal(str)
    """
    日志更新信号，用于更新日志窗口
    
    使用信号-槽机制解决跨线程UI更新问题，避免直接在线程中操作UI元素导致的错误：
    
    QObject: Cannot create children for a parent that is in a different thread.
    """

    tip_update = Signal(tuple)
    """提示更新信号，用于更新侧边提示栏"""

    anim_group_state_changed = Signal(int)
    """动画组状态改变信号"""

    button_update = Signal(ObjectButton, tuple)
    """按钮状态更新信号，用于控制按钮闪烁效果（这个应该是吃性能最多的信号了）"""

    show_info = Signal(tuple)
    """显示信息信号"""

    show_warning = Signal(tuple)
    """显示警告信号"""

    show_error = Signal(tuple)
    """显示错误信号"""

    show_question = Signal(tuple)
    """显示问题信号"""

    log_window_refresh = Signal()
    """日志窗口刷新信号，用于刷新日志窗口"""

    show_new_tip = Signal(SideNotice)
    """显示新提示信号"""

    stu_list_button_update = Signal()
    """学生列表按钮更新信号"""

    going_to_exit = Signal()
    "准备退出信号"

    dont_click_button_clicked = Signal(int)
    "千万别点被点击了"

    refresh_hint_widget_signal = Signal(int)
    "刷新提示(屏幕右上角的)文本信号"

    ###########################################################################
    #                                初始化                                    #
    ###########################################################################

    def __init__(
        self,
        *args,
        class_name="测试班级",
        current_user=default_user,
        class_key="CLASS_TEST",
    ):
        """
        窗口初始化

        :param class_name: 班级名称
        :param current_user: 当前用户
        :param class_key: 班级键
        """

        self.create_time = time.time()
        self.framerate_update_time = 0
        self.framecount = 0
        self.last_save_from_action = time.time()
        self.auto_save_last_time = time.time()
        self.sidenotice_waiting_order = Queue()
        self.sidenotice_avilable_slots = list(range(5))
        self.opacity = 0.88
        self.current_user = current_user
        Base.log("I", "程序创建", "MainWindow.__init__")
        self.app = QApplication(list(args))
        self.app.setStyle(QStyleFactory.create(app_style))
        self.app.setStyleSheet(app_stylesheet)
        self.save_path = f"chunks/{current_user}/"  # 可能在加载过之后变更
        "存档路径"
        self.backup_path = "backups/"
        "备份路径"
        super().__init__(user=current_user)
        self.init_display_data()
        self.load_settings()
        self.init_class_data(
            class_name=class_name,
            class_id=class_key,
            current_user=current_user,
            class_obs_tps=10,
            achievement_obs_tps=10,
        )
        # 给成就侦测器过载的时候增加一个提示
        orig_func = self.achievement_obs.on_observer_overloaded
        last_tip = 0.0

        def on_achievement_obs_overloaded(fr, op, mspt):
            "当成就侦测器过载时执行的操作"
            nonlocal last_tip
            if time.time() - last_tip >= 30:
                self.show_tip(
                    "警告",
                    "成就侦测器过载，已降低侦测速度",
                    self,
                    duration=8000,
                    icon=InfoBarIcon.WARNING,
                    further_info=f"详细信息：\n\n帧耗时：{fr}s\n操作耗时：{op}s\n帧耗时：{mspt}ms",
                )
                last_tip = time.time()
            orig_func(fr, op, mspt)

        self.achievement_obs.on_observer_overloaded = on_achievement_obs_overloaded

        self.stu_list_button_update.connect(self._grid_buttons)
        self.setup()
        self.achievement_obs.achievement_displayer = self.display_achievement
        self.is_running = True
        "窗口是否在运行"
        self.framerate_update_time = time.time()
        self.updator_thread = UpdateThread(mainwindow=self)
        self.command_list = command_list
        self.action.triggered.connect(self.student_rank)
        self.action_2.triggered.connect(self.manage_templates)
        self.action_3.triggered.connect(self.open_setting_window)
        self.action_5.triggered.connect(self.scoring_select)
        self.action_7.triggered.connect(self.retract_lastest)
        self.action_8.triggered.connect(lambda: self.tabWidget_2.setCurrentIndex(1))
        self.action_9.triggered.connect(lambda: self.tabWidget_2.setCurrentIndex(0))
        self.action_10.triggered.connect(self.save)
        self.action_12.triggered.connect(self.reset_scores)
        self.action_13.triggered.connect(self.show_all_history)
        self.action_14.triggered.connect(self.save_data_as)
        self.action_15.triggered.connect(self.music_selector)
        self.action_16.triggered.connect(self.show_recover_points)
        self.action_17.triggered.connect(self.create_recover_point)
        self.action_18.triggered.connect(self.cleaning_score_sum_up)
        self.action_19.triggered.connect(self.show_attendance)
        self.action_20.triggered.connect(self.show_noise_detector)
        self.action_21.triggered.connect(self.random_select)
        self.action_22.triggered.connect(self.homework_score_sum_up)
        self.action_23.triggered.connect(self.about_this)
        self.action_24.triggered.connect(self.show_update_log)
        self.action_25.triggered.connect(
            lambda: Thread(
                target=lambda: self.updator_thread.detect_new_version(False)
            ).start()
        )
        self.action_26.triggered.connect(self.refresh_window)
        self.action_28.triggered.connect(self.show_debug_window)
        self.actionNew_Template.triggered.connect(
            self.new_template
        )  # 笑死唯一一个不是默认名字的action控件
        self.show_new_tip.connect(lambda tip: tip.show())
        self.selected_quick_command: List[Optional[Command]] = [
            [c for c in self.command_list if c.key == "new_template"][0],
            [c for c in self.command_list if c.key == "manage_templates"][0],
            [c for c in self.command_list if c.key == "show_all_history"][0],
            [c for c in self.command_list if c.key == "scoring_select"][0],
            [c for c in self.command_list if c.key == "homework_score_sum_up"][0],
            [c for c in self.command_list if c.key == "cleaning_score_sum_up"][0],
            [c for c in self.command_list if c.key == "show_attendance"][0],
            [c for c in self.command_list if c.key == "detect_new_version"][0],
            [c for c in self.command_list if c.key == "show_update_log"][0],
        ]
        self.fast_command_edit_state = False
        self.refresh_quick_command_btns()
        self.HyperlinkLabel.clicked.connect(self.edit_fast_command_btns)
        self.CardWidget.clicked.connect(self.show_attendance)
        self.pushButton_3.clicked.connect(self.about_this)
        self.pushButton_4.clicked.connect(self.open_setting_window)
        try:
            self.load_quick_settings_from_list(
                pickle.load(
                    open(
                        os.getcwd()
                        + os.sep
                        + f"chunks/{self.current_user}/quick_commands.pkl",
                        "rb",
                    )
                )
            )
        except FileNotFoundError:
            Base.log("W", "未找到快速命令文件，重置为默认", "MainWindow.load_settings")
        self.listWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listWidget.doubleClicked.connect(self.click_opreation)
        self.tip_update.connect(lambda args: self._show_tip(*args))
        self.button_update.connect(self.add_new_btn_anim)
        self.log_window_refresh.connect(self._refresh_logwindow)
        self.pushButton.clicked.connect(self.dont_click)
        self.listView_data: List[Callable] = []
        "ListView数据，用于存储主窗口侧边ListView里面的命令（对应里面的每一项）"
        self.lastest_listview: Optional[ListView] = None
        "最近一次用self.list_view()开启的ListView"
        self.textBrowser.setReadOnly(True)
        self.textBrowser.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setFixedSize(self.width(), self.height())
        Base.log("I", f"设置透明度为{self.opacity}", "MainWindow.__init__")
        self.listWidget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )
        self.insert_queue = Queue()
        "在主窗口右侧ListWidget插入项的队列"
        self.logger_queue = Queue()
        "要插入到主窗口日志的队列"
        self.log_update.connect(self.logwindow_add_newline)
        self.log_update.emit("这里是日志")
        self.show_info.connect(lambda args: self._information(*args))
        self.show_warning.connect(lambda args: self._warning(*args))
        self.show_error.connect(lambda args: self._critical(*args))
        self.show_question.connect(lambda args: self._question_if_exec(*args))
        self.going_to_exit.connect(self.on_exit)
        self.dont_click_button_clicked.connect(self._dont_click)
        self.refresh_hint_widget_signal.connect(self._refresh_hint_widget)
        self.framecount = 0
        "自上一秒以来的更新帧数"
        self.framerate = 0
        "帧率"
        self.video_framecount = 0
        "动态背景帧数"
        self.video_framerate = 0
        "动态背景帧率"
        self.video_framerate_update_time = 0
        "动态背景帧数更新时间"
        self.displayed_on_the_log_window = 0
        "在小日志窗口上已经体现的日志条数，用来判断是否刷新"
        if self.auto_save_enabled:
            Thread(
                target=lambda: self.auto_save(timeout=int(self.auto_save_interval)),
                name="AutoSave",
                daemon=True,
            ).start()
        Thread(
            target=self.insert_action_history_info_while_alive,
            name="InsertOpreationHandler",
            daemon=True,
        ).start()
        Thread(
            target=self.read_video_while_alive, daemon=True, name="VideoReader"
        ).start()
        Thread(
            target=self.refresh_logwindow_while_alive,
            daemon=True,
            name="RefreshLogWindow",
        ).start()
        self.tip_handler = self.TipHandler(self)
        self.tip_handler.start()
        self.logwindow_content: List[str] = ["这里是日志"]
        self.auto_saving = False
        self.setWindowTitle(f"班寄管理 - {self.target_class.name}")
        self.terminal_locals = {}
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(8)
        self.recent_command_update_timer = QTimer()
        self.recent_command_update_timer.timeout.connect(
            self.update_recent_command_btns
        )
        self.recent_command_update_timer.start(300)
        self.tip_history: List[SideNotice] = []
        self.show_tip(
            "", "双击项目查看消息记录", duration=0, further_info="孩子真聪明（bushi"
        )
        self.ListWidget.itemDoubleClicked.connect(self.view_tip_hisory)
        self.ListWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        self.student_info_window: Optional[StudentWidget] = None
        self.CardWidget_2.clicked.connect(
            lambda: Thread(target=self.refresh_hint_widget).start()
        )
        PromptUtils.send_notice = lambda title, content, msg_type: (
            self.show_tip(
                title,
                content,
                (
                    InfoBarIcon.INFORMATION
                    if msg_type == "info"
                    else (
                        InfoBarIcon.WARNING
                        if msg_type == "warn"
                        else (
                            InfoBarIcon.ERROR
                            if msg_type == "error"
                            else InfoBarIcon.SUCCESS
                        )
                    )
                ),
            )
        )
        self.window_info: ClassWindow.WindowInfo = ClassWindow.WindowInfo()
        "窗口信息"
        self.refresh_hint_widget()
        self.btns_anim_group: Optional[QParallelAnimationGroup] = QParallelAnimationGroup()
        "按钮动画组"
        self.anim_group_state_changed.connect(self._anim_group_state_changed)
        self.exit_action_finished: bool = False
        "退出动作是否完成"
        self.exit_tip: Optional[QLabel] = None
        "退出时正在保存数据的提示"
        # self.use_animate_background: bool = False
        # "是否使用动态背景"
        self.capture: Optional[cv2.VideoCapture] = None
        "动态背景的捕获对象"
        self.current_video_frame: Optional[QImage] = None
        "当前的动态背景视频帧"
        self.tip_viewer_window: Optional[TipViewerWindow] = None
        "提示查看窗口"
        self.template_listbox: Optional[ListView] = None
        "模板列表框"
        self.manage_template_cursel_index: Optional[int] = None
        "管理模板时选中的索引"
        self.new_template_window: Optional[NewTemplateWidget] = None
        "新建模板窗口"
        self.history_detail_window: Optional[HistoryWidget] = None
        "历史详情窗口"
        self.multi_select_window: Optional[StudentSelectorWidget] = None
        "多选学生窗口"
        self.multi_select_template_window: Optional[SelectTemplateWidget] = None
        "多选学生打开的模板窗口（以前不会写信号和槽弄的）"
        self.setting_window: Optional[SettingWidget] = None
        "设置窗口"
        self.cleaning_sumup_window: Optional[CleaningScoreSumUpWidget] = None
        "卫生分总结窗口"
        self.group_info_window: Optional[GroupWidget] = None
        "小组信息窗口"
        self.icon: Optional[QIcon] = None
        "窗口图标"
        self.random_select_window: Optional[RandomSelectWidget] = None
        "随机选择窗口"
        self.homework_sumup_window: Optional[HomeworkScoreSumUpWidget] = None
        "作业分总结窗口"
        self.attendance_window: Optional[AttendanceInfoWidget] = None
        "考勤窗口"
        self.is_loading_all_history: bool = False
        "是否正在加载所有历史记录"
        self.listview_history_classes: Optional[ListView] = None
        "历史记录查看的所有班级列表"
        self.listview_history_class: Optional[ListView] = None
        "历史记录查看的班级列表"
        self.recovery_points: Optional[Dict[float, RecoveryPoint]] = None
        "所有的恢复点"
        self.about_window: Optional[AboutWidget] = None
        "关于窗口"
        self.debug_window: Optional[DebugWidget] = None
        "调试窗口"
        self.music_listview: Optional[ListView] = None
        "音乐列表"
        self.noise_detector: Optional[NoiseDetectorWidget] = None
        "噪音检测窗口"



    def __repr__(self):  # 其实是因为直接继承ClassObjects的repr会导致无限递归
        return super(MyMainWindow, self).__repr__()

    def init_display_data(self):
        """ "初始化显示数据和存储数据"""
        Base.log("I", "初始化本地显示数据", "MainWindow.init_siaplay_data")
        self.target_class: Class
        if not hasattr(self, "stu_buttons"):
            self.stu_buttons: Dict[int, ObjectButton] = {}
            self.grp_buttons: Dict[int, ObjectButton] = {}
        self.client_version = CLIENT_VERSION
        self.client_version_code = CLIENT_VERSION_CODE
        self.opacity = 0.88
        self.score_up_color_mixin_begin = (0xCA, 0xFF, 0xCA)
        self.score_up_color_mixin_end = (0x33, 0xCF, 0x6C)
        self.score_up_color_mixin_step = 15
        self.score_up_color_mixin_start = 2
        self.score_up_flash_framelength_base = 300
        self.score_up_flash_framelength_step = 100
        self.score_up_flash_framelength_max = 2000

        self.score_down_color_mixin_begin = (0xFC, 0xB5, 0xB5)
        self.score_down_color_mixin_end = (0xA9, 0x00, 0x00)
        self.score_down_color_mixin_step = 15
        self.score_down_color_mixin_start = 2
        self.score_down_flash_framelength_base = 300
        self.score_down_flash_framelength_step = 100
        self.score_down_flash_framelength_max = 2000

        self.log_keep_linecount = 100
        self.log_update_interval = 0.1

        self.auto_save_enabled = False
        self.auto_save_interval = 120
        self.auto_save_path: Literal["folder", "user"] = "folder"
        self.auto_backup_scheme: Literal["none", "only_data", "all"] = "only_data"

        self.animation_speed = 1.0
        self.subwindow_x_offset = 0
        self.subwindow_y_offset = 0
        self.use_animate_background = False
        self.max_framerate = 60

    ###########################################################################
    #                            用户提示类                                    #
    ###########################################################################

    def show_tip(
        self,
        title: str = "提示",
        content: str = "这是一个提示",
        master: Optional[WidgetType] = None,
        icon: Optional[Union[InfoBarIcon, QIcon, str]] = None,
        sound: Optional[str] = None,
        duration: int = 5000,
        closeable: bool = True,
        click_command: Optional[Callable] = None,
        further_info: str = "该提示没有详细信息。",
    ):
        """
        向用户发送一个提示

        :param text: 通知显示的文本内容
        :param master: 父窗口对象
        :param icon: 通知图标
        :param sound: 通知出现时播放的声音文件
        :param duration: 通知显示持续时间(毫秒)
        :param closeable: 是否允许用户关闭通知
        :param click_command: 点击通知时的回调函数
        """
        self.tip_update.emit(
            (
                title,
                content,
                master,
                duration,
                icon,
                sound,
                closeable,
                click_command,
                further_info,
            )
        )

    def _show_tip(
        self,
        title,
        content,
        master,
        duration,
        icon,
        sound,
        closeable,
        click_command,
        further_info,
    ):
        """显示提示，是一个接口（喜）（？"""
        if master is None:
            master = self
        if not hasattr(self, "sidenotice_waiting_order"):
            self.sidenotice_waiting_order = Queue()
            Base.log(
                "W",
                "未找到sidenotice_waiting_order，已经重置...",
                "MainWindow.show_tip",
            )
        obj = SideNotice(
            title=title,
            content=content,
            icon=icon,
            sound=sound,
            closeable=closeable,
            click_command=click_command,
            duration=duration,
            master=master,
            further_info=further_info,
        )
        self.tip_history.insert(0, obj)
        self.ListWidget.insertItem(
            0,
            time.strftime(
                f"%H:%M {obj.title} {obj.content}", time.localtime(obj.create_time)
            ),
        )
        self.sidenotice_waiting_order.put(obj)

    @Slot(QListWidgetItem)
    def view_tip_hisory(self, item: QListWidgetItem):
        "查看提示历史，在屏幕右侧的历史列表被双击的时候自动调用"
        index = self.ListWidget.row(item)
        obj = self.tip_history[index]
        self.tip_viewer_window = TipViewerWindow(obj, self)
        self.tip_viewer_window.show()

    class TipHandler(QThread):
        "侧边提示处理器"

        def __init__(self, parent: "ClassWindow"):
            super().__init__(parent)
            self._parent = parent

        @profile()
        def run(self):
            Base.log("I", "提示处理器线程被启动", "MainWindow.TipHandler")
            while not self._parent.is_running:
                time.sleep(0.1)
            Base.log("I", "提示处理器线程开始运行", "MainWindow.TipHandler")
            while self._parent.is_running:
                if not hasattr(self._parent, "sidenotice_waiting_order"):
                    self._parent.sidenotice_waiting_order = Queue()
                    Base.log(
                        "W",
                        "self._parent.sidenotice_waiting_order 被重新初始化",
                        "MainWindow.TipHandler",
                    )
                while True:
                    try:
                        current: SideNotice = self._parent.sidenotice_waiting_order.get(
                            timeout=1
                        )
                        break
                    except (
                        BaseException
                    ) as unused:  # pylint: disable=broad-exception-caught
                        pass

                while len(self._parent.sidenotice_avilable_slots) == 0:
                    time.sleep(0.1)

                index = self._parent.sidenotice_avilable_slots.pop(0)

                def return_slot(slot: int, current: SideNotice):
                    if not current.finished:
                        self._parent.sidenotice_avilable_slots.append(slot)
                        current.finished = True

                Thread(
                    target=lambda index=index, current=current, return_slot=return_slot: (
                        time.sleep(current.duration / 1000 + 0.2),
                        return_slot(index, current),
                    )
                ).start()

                current.closebutton_clicked = (
                    lambda index=index, current=current, return_slot=return_slot: (
                        return_slot(index, current),
                        current.click_command() if current.click_command else None,
                    )
                )

                Base.log(
                    "D",
                    f"正在将提示 {repr(current)} 放入第 {index} 个位置",
                    "MainWindow.TipHandler",
                )
                self._parent.show_new_tip.emit(current)
            Base.log("I", "提示处理器线程结束", "MainWindow.TipHandler")

    def information(self, title: str, text: str, pixmap: Optional[QPixmap] = None):
        """
        显示信息对话框

        :param title: 对话框标题
        :param text: 对话框内容
        :param pixmap: 自定义图标"""
        self.show_info.emit((title, text, pixmap))

    def _information(self, title, text, pixmap):
        "显示信息框的接口"
        Base.log(
            "I",
            f"信息框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.information",
        )
        msgbox = QMessageBox(
            QMessageBox.Icon.Information,
            title,
            text,
            QMessageBox.StandardButton.Ok,
            parent=self,
        )
        msgbox.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-main.png"))
        msgbox.exec()

    def warning(self, title: str, text: str, pixmap: Optional[QPixmap] = None):
        """
        显示警告对话框

        :param title: 对话框标题
        :param text: 对话框内容
        :param pixmap: 自定义图标"""
        self.show_warning.emit((title, text, pixmap))

    def _warning(self, title, text, pixmap):
        "显示警告框的接口"
        Base.log(
            "W",
            f"警告框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.warning",
        )
        msgbox = QMessageBox(
            QMessageBox.Icon.Warning,
            title,
            text,
            QMessageBox.StandardButton.Ok,
            parent=self,
        )
        msgbox.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-warn.png"))
        msgbox.exec()

    def critical(self, title: str, text: str, pixmap: Optional[QPixmap] = None):
        """
        显示错误对话框

        :param title: 对话框标题
        :param text: 对话框内容
        :param pixmap: 自定义图标
        """
        self.show_error.emit((title, text, pixmap))

    def _critical(self, title, text, pixmap):
        "显示错误框的接口"
        Base.log(
            "C",
            f"错误框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.critical",
        )
        msgbox = QMessageBox(
            QMessageBox.Icon.Critical,
            title,
            text,
            QMessageBox.StandardButton.Ok,
            parent=self,
        )
        msgbox.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-error.png"))
        msgbox.exec()

    def question_if_exec(
        self, title: str, text: str, command: Callable, pixmap: Optional[QPixmap] = None
    ):
        """显示确认对话框并在用户确认时执行指定函数

        :param title: 对话框标题
        :param text: 对话框内容
        :param command: 用户确认时执行的回调函数
        :param pixmap: 自定义图标"""
        self.show_question.emit((title, text, command, pixmap))

    def _question_if_exec(self, title, text, command, pixmap):
        "询问框的接口"
        Base.log(
            "I",
            f"询问框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.question_if_exec",
        )
        if question_yes_no(
            self,
            title,
            text,
            False,
            "question",
            pixmap or QPixmap("./img/logo/favicon-help.png"),
        ):
            command()
            return True
        return False

    ###########################################################################
    #                        功能实现：快捷命令                                #
    ###########################################################################

    @property
    def command_key_list(self) -> List[Optional[str]]:
        "快捷键列表（返回功能的key）"
        return [c.key if c else None for c in self.selected_quick_command]

    def refresh_quick_command_btns(self, reset_callable: bool = True):
        """
        刷新快捷命令按钮
        :param reset_callable: 是否重置按钮的回调函数
        """
        for i in range(1, 9 + 1):
            btn: PushButton = getattr(self, f"PushButton_{i}")
            if self.selected_quick_command[i - 1] is not None:
                btn.setText(self.selected_quick_command[i - 1].name)
                if reset_callable:
                    try:
                        btn.clicked.disconnect()
                    except RuntimeError as e:
                        Base.log("W", f"尝试断开未连接的信号：(PushButton_{i}) {e}")
                    cmd = self.selected_quick_command[i - 1]
                    func = cmd.callable

                    if cmd.for_which == "MainWindow":
                        # 因为不是直接调用的类方法，需要手动传一个self
                        btn.clicked.connect(lambda *, f=func: f(self))
                    elif cmd.for_which:
                        btn.clicked.connect(lambda *, f=func, c=cmd: f(c.for_which))
                    else:
                        btn.clicked.connect(lambda *, f=func: f())
                btn.setEnabled(True)
            else:
                btn.setText("未指定")
                btn.setEnabled(False)
            btn.update()

    def edit_fast_command_btns(self):
        """
        编辑快捷命令按钮，如果已经处于编辑状态则退出编辑状态
        """
        if not hasattr(self, "fast_command_edit_state"):
            self.fast_command_edit_state = False
        self.fast_command_edit_state = not self.fast_command_edit_state

        if self.fast_command_edit_state:
            Base.log("I", "进入快捷命令编辑模式", "MainWindow.edit_fast_command_btns")
            self.CaptionLabel.setText("快速管理 (编辑中)")
            self.HyperlinkLabel.setText("完成")
            for i in range(1, 9 + 1):
                btn: PushButton = getattr(self, f"PushButton_{i}")

                def _select_command(btn: PushButton, i: int = i) -> int:
                    def _set_quick_command(cmd: object, i: int = i) -> None:
                        self.selected_quick_command[i - 1] = cmd
                        Base.log(
                            "I",
                            f"第{i}个快捷命令已被更改：{btn.text()} -> {cmd.name if cmd is not None else '未指定'}",
                        )
                        btn.setText(cmd.name if cmd is not None else "未指定")
                        self.refresh_quick_command_btns(False)
                        for i in range(1, 9 + 1):
                            _btn: PushButton = getattr(self, f"PushButton_{i}")
                            _btn.setEnabled(True)

                    self.list_view(
                        [("选择要设置的快捷命令", lambda: None)]
                        + [("", lambda: None)] * 2
                        + [
                            (
                                c.name,
                                lambda *, c=c: _set_quick_command(c),
                                self.refresh_quick_command_btns(False),
                            )
                            for c in self.command_list
                        ]
                        + [("<不指定>", lambda: _set_quick_command(None))],
                        "选择要设置的快捷命令",
                        self,
                        select_once_then_exit=True,
                    )

                try:
                    btn.clicked.disconnect()
                except RuntimeError as e:
                    Base.log(
                        "W",
                        f"尝试断开未连接的信号：(PushButton_{i}) {e}",
                        "MainWindow.edit_fast_command_btns",
                    )
                btn.clicked.connect(
                    lambda *, _select_command=_select_command, btn=btn: (
                        _select_command(btn),
                        self.refresh_quick_command_btns(False),
                    )
                )
                btn.setEnabled(True)

        else:
            Base.log("I", "退出快捷命令编辑模式", "MainWindow.edit_fast_command_btns")
            self.CaptionLabel.setText("快速管理")
            self.show_tip(
                "提示", "快捷命令保存成功", duration=3275, icon=InfoBarIcon.SUCCESS
            )
            self.HyperlinkLabel.setText("编辑")
            self.refresh_quick_command_btns(True)
            self.save_quick_command_config()

    def save_quick_command_config(self):
        Base.log("I", "保存快捷命令配置", "MainWindow.save_fast_command_config")
        pickle.dump(
            self.command_key_list,
            open(
                os.getcwd() + os.sep + f"chunks/{self.current_user}/quick_commands.pkl",
                "wb",
            ),
            pickle.HIGHEST_PROTOCOL,
        )
        self.refresh_quick_command_btns()

    def load_quick_settings_from_list(self, cmdlist: List[str]):
        "从名称或者key值列表中加载快捷命令"
        self.selected_quick_command = [None] * 9
        avaliable = [c.name for c in self.command_list]
        avaliable2 = [c.key for c in self.command_list]

        for i in range(9):
            if cmdlist[i] in avaliable:
                self.selected_quick_command[i] = [
                    c for c in self.command_list if c.name == cmdlist[i]
                ][0]
            elif cmdlist[i] in avaliable2:
                self.selected_quick_command[i] = [
                    c for c in self.command_list if c.key == cmdlist[i]
                ][0]
            else:
                Base.log(
                    "W", f"快捷命令{repr(cmdlist[i])}不存在，将会重置为默认(未指定)"
                )
                self.selected_quick_command[i] = None

        self.refresh_quick_command_btns()

    def update_recent_command_btns(self):
        """更新最近使用命令按钮"""
        try:
            self.PushButton_10.clicked.disconnect(None)
        except RuntimeError:
            pass
        try:
            self.PushButton_11.clicked.disconnect(None)
        except RuntimeError:
            pass
        try:
            self.PushButton_12.clicked.disconnect(None)
        except RuntimeError:
            pass
        self.PushButton_10.setText(
            lately_used_commands[-1].name if lately_used_commands else "暂无"
        )
        self.PushButton_11.setText(
            lately_used_commands[-2].name if len(lately_used_commands) >= 2 else "暂无"
        )
        self.PushButton_12.setText(
            lately_used_commands[-3].name if len(lately_used_commands) >= 3 else "暂无"
        )
        self.PushButton_10.clicked.connect(
            (
                lambda: (
                    lately_used_commands[-1].callable(self)
                    if lately_used_commands[-1].for_which == "MainWindow"
                    else (
                        lambda: (
                            lately_used_commands[-1].callable(
                                lately_used_commands[-1].for_which
                            )
                            if lately_used_commands[-1].for_which
                            else lately_used_commands[-1].callable()
                        )
                    )
                )
            )
            if lately_used_commands
            else lambda: None
        )
        self.PushButton_11.clicked.connect(
            (
                lambda: (
                    lately_used_commands[-2].callable(self)
                    if lately_used_commands[-2].for_which == "MainWindow"
                    else (
                        lambda: (
                            lately_used_commands[-2].callable(
                                lately_used_commands[-2].for_which
                            )
                            if lately_used_commands[-2].for_which
                            else lately_used_commands[-2].callable()
                        )
                    )
                )
            )
            if len(lately_used_commands) >= 2
            else lambda: None
        )
        self.PushButton_12.clicked.connect(
            (
                lambda: (
                    lately_used_commands[-3].callable(self)
                    if lately_used_commands[-3].for_which == "MainWindow"
                    else (
                        lambda: (
                            lately_used_commands[-3].callable(
                                lately_used_commands[-3].for_which
                            )
                            if lately_used_commands[-3].for_which
                            else lately_used_commands[-3].callable()
                        )
                    )
                )
            )
            if len(lately_used_commands) >= 3
            else lambda: None
        )
        super().update()

    ###########################################################################
    #                        功能实现：工具设置                                #
    ###########################################################################

    def save_settings(self):
        """保存当前的全局设置对象到设置存档文件"""
        Base.log("I", "保存设置到文件", "MainWindow.save_settings")
        os.makedirs(os.getcwd() + os.sep + f"chunks/{self.current_user}", exist_ok=True)
        settings.save_to(
            os.getcwd() + os.sep + f"chunks/{self.current_user}/settings.dat"
        )

    @Slot()
    def reset_settings(self):
        """重置全局设置并将主窗口的设置重置为全局设置当前的默认值"""
        settings.reset()
        version = self.client_version
        version_code = self.client_version_code
        self.set_settings(**settings.get_dict())
        self.set_settings(client_version_code=version_code, client_version=version)
        self.save_settings()

    def load_settings(self) -> SettingsInfo:
        """加载设置存档文件到全局设置对象后应用在主窗口"""
        Base.log("I", "从文件中加载设置", "MainWindow.load_settings")
        settings.load_from(
            os.getcwd() + os.sep + f"chunks/{self.current_user}/settings.dat"
        )
        self.set_settings(**settings.get_dict())

    def set_settings(self, **kwargs):
        """依照kwargs设置全局设置对象和主窗口的设置信息并保存当前设置到文件（调用save_settings）"""
        Base.log("I", "设置设置信息", "MainWindow.set_settings")
        for key, value in kwargs.items():
            if settings.get(key) != kwargs[key]:
                Base.log(
                    "I",
                    f"{key} 变更： "
                    f"{settings.get(key)} "
                    f"-> {repr(getattr(self, key, None))} (self) "
                    f"/ {repr(kwargs[key])} (kwargs)",
                    "MainWindow.set_settings",
                )
            setattr(self, key, value)
            setattr(settings, key, value)
        self.save_settings()

    def save_current_settings(self):
        """保存此窗口当前的设置到全局设置对象并保存设置"""
        Base.log("I", "保存当前设置", "MainWindow.save_settings")
        self.set_settings(
            client_version=self.client_version,
            client_version_code=self.client_version_code,
            opacity=self.opacity,
            score_up_color_mixin_begin=self.score_up_color_mixin_begin,
            score_up_color_mixin_end=self.score_up_color_mixin_end,
            score_up_color_mixin_step=self.score_up_color_mixin_step,
            score_up_color_mixin_start=self.score_up_color_mixin_start,
            score_up_flash_framelength_base=self.score_up_flash_framelength_base,
            score_up_flash_framelength_step=self.score_up_flash_framelength_step,
            score_up_flash_framelength_max=self.score_up_flash_framelength_max,
            score_down_color_mixin_begin=self.score_down_color_mixin_begin,
            score_down_color_mixin_end=self.score_down_color_mixin_end,
            score_down_color_mixin_step=self.score_down_color_mixin_step,
            score_down_color_mixin_start=self.score_down_color_mixin_start,
            score_down_flash_framelength_base=self.score_down_flash_framelength_base,
            score_down_flash_framelength_step=self.score_down_flash_framelength_step,
            score_down_flash_framelength_max=self.score_down_flash_framelength_max,
            log_keep_linecount=self.log_keep_linecount,
            log_update_interval=self.log_update_interval,
            auto_save_enabled=self.auto_save_enabled,
            auto_save_interval=self.auto_save_interval,
            auto_save_path=self.auto_save_path,
            auto_backup_scheme=self.auto_backup_scheme,
            animation_speed=self.animation_speed,
            subwindow_x_offset=self.subwindow_x_offset,
            subwindow_y_offset=self.subwindow_y_offset,
            use_animate_background=self.use_animate_background,
            max_framerate=self.max_framerate,
        )

    ###########################################################################
    #                            界面绘制相关                                  #
    ###########################################################################

    ##### PySide6相关 #####

    def setOpacity(self, opacity: float):
        "设置窗口透明度"
        op = QGraphicsOpacityEffect()
        op.setOpacity(opacity)
        self.setGraphicsEffect(op)

    def show(self):
        "显示主窗口"
        Base.log("I", "显示主窗口", "MainWindow.show")
        self.setWindowOpacity(self.opacity)
        super().show()
        self.is_running = True

    def closeEvent(self, event: QCloseEvent, do_tip: bool = True):
        """
        关闭事件，这里是覆写的MyMainWindow.closeEvent

        :param event: 传来的QCloseEvent
        """
        Base.log("I", "准备关闭程序", "MainWindow.closeEvent")
        if super().closeEvent(event, do_tip):
            self.setEnabled(False)
            self.exit_tip = QLabel(self)
            self.exit_tip.setText("正在保存数据...")
            self.exit_tip.setStyleSheet(
                "background-color: rgb(197, 197, 197); border-radius: 8px"
            )
            self.exit_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.exit_tip.setGeometry(
                self.width() // 2 - 70, self.height() // 2 - 20, 140, 40
            )
            self.exit_tip.show()
            self.exit_action_finished = False
            self.going_to_exit.emit()
            while not self.exit_action_finished:
                do_nothing()
            self.hide()
            Base.log("I", "执行app.quit()", "MainWindow.closeEvent")
            self.app.quit()

    ###### 窗口绘制 ######

    class WindowInfo(DataObject):
        "窗口信息"

        def __init__(self):
            self.video = ClassWindow.WindowInfo.Video()

        class Video(DataObject):
            "视频信息"

            def __init__(self):
                self.last_paint_event = ClassWindow.WindowInfo.Video.PaintEventInfo()
                self.last_update_event = ClassWindow.WindowInfo.Video.UpdateInfo()

            class PaintEventInfo(DataObject):
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

            class UpdateInfo(DataObject):
                widget_updating: float = 0.0
                "更新控件的时间"
                super: float = 0.0
                "PySide6处理时间"
                total_time: float = 0.0
                "总时间"

    def paintEvent(self, event: QPaintEvent):
        """处理窗口绘制事件，渲染背景图像或视频帧"""
        t = time.time()
        if time.time() - self.framerate_update_time >= 1:
            self.framerate = self.framecount
            self.framecount = 0
            self.framerate_update_time = time.time()
        self.framecount += 1

        padding = 15 * self.devicePixelRatio()
        t2 = time.time()

        if self.current_video_frame and self.use_animate_background:
            pixmap = QPixmap.fromImage(self.current_video_frame)
        else:
            if not os.path.exists("./img/main/background.jpg"):
                # 为了防止更新的时候给原有的background.jpg覆盖了
                shutil_copy(
                    "./img/main/default/background.jpg", "./img/main/background.jpg"
                )

            pixmap = QPixmap("./img/main/background.jpg")
        t3 = time.time()

        painter = QPainter(self)
        t4 = time.time()

        painter.drawPixmap(
            -padding,
            -padding,
            self.width() + padding * 2,
            self.height() + padding * 2,
            pixmap,
        )
        painter.end()
        t5 = time.time()

        event.accept()
        t6 = time.time()

        v = self.window_info.video.last_paint_event
        v.data_reading = t2 - t
        v.background_dealing = t3 - t2
        v.painter_constructing = t4 - t3
        v.pixmap_drawing = t5 - t4
        v.event_accepting = t6 - t5
        v.total_time = t6 - t

    class AnimationGroupStatement(enum.IntEnum):
        "动画组状态"
        CREATE_NEW = 0
        "创建新动画组"
        START = 1
        "启动动画组"
        STOP = 2
        "停止动画组"
        DELETE = 3
        "删除动画组"

    def _anim_group_state_changed(self, state: int):
        """处理动画组状态变化"""
        if state == self.AnimationGroupStatement.CREATE_NEW:
            self.btns_anim_group = QParallelAnimationGroup(self)
        elif state == self.AnimationGroupStatement.START:
            self.btns_anim_group.start()
        elif state == self.AnimationGroupStatement.STOP:
            self.btns_anim_group.stop()
        elif state == self.AnimationGroupStatement.DELETE:
            self.btns_anim_group.deleteLater()
            self.btns_anim_group = None

    @profile()
    def read_video_while_alive(self):
        """读取并处理背景视频文件，用于动态背景效果"""
        if not HAS_CV2:
            return
        if not os.path.isfile("background.mp4"):
            Base.log(
                "W", "没有找到视频文件，将使用默认动态背景", "MainWindow.read_video"
            )
            if os.path.isfile("audio/video/default/background.mp4"):
                if os.path.isdir("audio/video/default/background.mp4"):
                    os.rmdir("audio/video/default/background.mp4")
                shutil_copy("audio/video/default/background.mp4", "background.mp4")

                self.warning(
                    "提示",
                    "动态背景需要要视频文件（background.mp4），请检查文件是否存在\n"
                    "当前已经复制默认视频文件到根目录，如果需要使用其他动态背景直接替换background.mp4即可",
                )
            else:
                self.warning(
                    "提示",
                    "动态背景需要要视频文件（background.mp4），请检查文件是否存在\n"
                    "如果需要使用动态背景将background.mp4复制到工具的根目录即可",
                )
            self.use_animate_background = False
            while not os.path.isfile("background.mp4"):
                time.sleep(5)
        while self.is_running:
            self.capture = cv2.VideoCapture("background.mp4")
            last_frame_time = time.time()
            video_fps = self.capture.get(cv2.CAP_PROP_FPS)
            Base.log("I", f"视频解析完成，帧率：{video_fps}", "MainWindow.read_video")
            while self.is_running and self.use_animate_background:

                if time.time() - self.video_framerate_update_time >= 1:
                    self.video_framerate = self.video_framecount
                    self.video_framecount = 0
                    self.video_framerate_update_time = time.time()
                fd = 1 / max(1, min(self.max_framerate, video_fps))
                if time.time() - last_frame_time < fd:
                    time.sleep(max(fd - (time.time() - last_frame_time), 0))
                last_frame_time = time.time()

                ret, frame = self.capture.read()

                if not ret:
                    self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.capture.read()
                h, w, _ = frame.shape
                self.current_video_frame = QImage(
                    frame.data, w, h, 3 * w, QImage.Format.Format_BGR888
                )

                # self.update()
                self.video_framecount += 1

            self.video_framerate = 0
            while not self.use_animate_background:
                "等待到再次启用动态动画"
                time.sleep(0.1)

    def setup(self):
        """设置界面"""
        Base.log("I", "设置界面", "MainWindow.setup")
        self.setupUi(self)
        self.grid_buttons()

    def grid_buttons(self):
        """显示所有学生按钮（虽然不算真正意义上的grid）"""
        self.stu_list_button_update.emit()

    def _grid_buttons(self):
        """grid_buttons的接口，不要用Thread调用!"""
        Base.log("I", "准备显示按钮", "MainWindow.grid_buttons")
        for b in self.stu_buttons.values():
            b.deleteLater()
            do_nothing()
        row = 0
        col = 0
        max_col = (self.scrollArea.width() + 6) // (81 + 6)
        height = 0
        self.scrollAreaWidgetContents_2.setGeometry(
            0, 0, 901, max((51 + 4) * len(self.target_class.students), 410)
        )
        for num, stu in self.target_class.students.items():
            self.stu_buttons[num] = ObjectButton(
                f"{stu.num}号 {stu.name}\n{stu.score}分", self, object=stu
            )
            self.stu_buttons[num].setObjectName("StudentButton" + str(stu.num))
            self.stu_buttons[num].setGeometry(
                QRect(10 + col * (81 + 6), 8 + row * (51 + 4), 81, 51)
            )
            self.stu_buttons[num].setParent(self.scrollAreaWidgetContents_2)
            self.stu_buttons[num].clicked.connect(
                lambda *, stu=stu: self.student_info(stu)
            )
            self.stu_buttons[num].show()
            col += 1
            if col == 1:
                height += 51 + 4

            if col > max_col - 1:
                col = 0
                row += 1
        self.scrollAreaWidgetContents_2.setMinimumHeight(height)  # 不然不显示滚动条

        row = 0
        col = 0
        max_col = (self.scrollArea.width() + 6) // (162 + 6)
        height = 0
        for num, grp in self.target_class.groups.items():
            if grp.belongs_to == self.target_class.key:
                self.grp_buttons[num] = ObjectButton(
                    f"{grp.name}\n{stu.score}分", self, object=stu
                )
                self.grp_buttons[num].setObjectName("GroupButton" + str(stu.num))
                self.grp_buttons[num].setGeometry(
                    QRect(10 + col * (162 + 6), 8 + row * (102 + 4), 162, 102)
                )
                self.grp_buttons[num].setParent(self.tab_4)
                self.grp_buttons[num].clicked.connect(
                    lambda *, grp=grp: self.group_info(grp)
                )
                self.grp_buttons[num].show()
                col += 1
                if col == 1:
                    height += 102 + 4
                if col > max_col - 1:
                    col = 0
                    row += 1

        self.scrollAreaWidgetContents.setMinimumHeight(height)

    def update(self):
        "更新界面"
        t = time.time()
        self.label_2.setText(f"{self.target_class.name}")
        self.label_3.setText(f"{len(self.target_class.students)}")
        self.label_4.setText(f"{self.target_class.owner}")
        self.label_5.setText(f"{self.target_class.student_avg_score:.2f}")
        self.label_6.setText(
            str(
                max(
                    *[
                        float(self.target_class.students[num].score)
                        for num in self.target_class.students
                    ]
                )
            )
            + "/"
            + str(
                min(
                    *[
                        float(self.target_class.students[num].score)
                        for num in self.target_class.students
                    ]
                )
            )
        )
        self.label_7.setText(f"{self.framerate}fps; {self.video_framerate}fps")
        self.label_8.setText(f"{time.time() - self.create_time:.3f} s")
        self.label_9.setText(f"{threading.active_count()}")
        self.label_10.setText(
            str(round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 1))
            + " MB"
        )
        self.label_11.setText(
            f"{self.class_obs.tps:.2f}/"
            f"{self.class_obs.limited_tps}tps;"
            f" {str(round(self.achievement_obs.tps, 2)).rjust(5)}/"
            f"{self.achievement_obs.limited_tps}tps"
        )
        self.BodyLabel_2.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.BodyLabel.setText(
            "%s好，欢迎回来"
            % (
                "早上"
                if 5 <= time.localtime().tm_hour < 10
                else (
                    "上午"
                    if 10 <= time.localtime().tm_hour < 12
                    else (
                        "中午"
                        if 12 <= time.localtime().tm_hour < 14
                        else "下午" if 14 <= time.localtime().tm_hour < 18 else "晚上"
                    )
                )
            )
        )
        t2 = time.time()
        super().update()
        t3 = time.time()
        v = self.window_info.video.last_update_event
        v.widget_updating = t2 - t
        v.super = t3 - t2
        v.total_time = t3 - t

    def close(self):
        "关闭窗口，覆写MyMainWindow.close"
        self.is_running = False
        super().close()

    ###### 日志显示 ######

    @Slot(str)
    def logwindow_add_newline(self, string: str):
        """向日志窗口添加新日志条目

        :param string: 要添加的日志文本
        """
        if not hasattr(self, "logwindow_content"):
            self.logwindow_content = []
        self.logwindow_content.append(string.strip())
        if len(self.logwindow_content) > self.log_keep_linecount:
            self.logwindow_content.pop(0)

    def refresh_logwindow_while_alive(self):
        """更新日志窗口显示内容，同步最新日志信息"""
        while self.is_running:
            self.log_window_refresh.emit()
            time.sleep(self.log_update_interval)

    @Slot()
    def _refresh_logwindow(self):
        "刷新日志窗口的接口"
        if self.logged_count != self.displayed_on_the_log_window:
            self.textBrowser.setText(nl.join(self.short_log_info))
            self.textBrowser.verticalScrollBar().setValue(
                self.textBrowser.verticalScrollBar().maximum()
            )
            self.displayed_on_the_log_window = self.logged_count

    @Slot(QPushButton, tuple)
    def add_new_btn_anim(self, obj: ObjectButton, args: tuple):
        """闪烁按钮"""
        self.btns_anim_group.addAnimation(obj.get_flash_anim(*args))

    ##### 左上角信息栏控制 #####

    flash_executor = ThreadPoolExecutor(max_workers=128, thread_name_prefix="Animation")

    def insert_action_history_info_while_alive(self):
        """插入操作线程"""
        while self.is_running:
            try:
                text, command, insert_fade, fade_step = self.insert_queue.get()
                Base.log(
                    "I",
                    f"插入操作：名称{repr(text)}， 命令{repr(command)}",
                    "MainWindow.insert_action",
                )
                item = QListWidgetItem(text)
                self.listWidget.insertItem(0, item)
                self.listView_data.insert(0, command)
                self.listWidget.scrollToTop()

                def flash(item: QListWidgetItem, insert_fade: tuple, fade_step: int):
                    for r, g, b in list(
                        zip(
                            steprange(insert_fade[0], insert_fade[3], fade_step),
                            steprange(insert_fade[1], insert_fade[4], fade_step),
                            steprange(insert_fade[2], insert_fade[5], fade_step),
                        )
                    ):

                        item.setBackground(QColor(r, g, b))
                        time.sleep(0.02)
                        self.app.processEvents()

                self.flash_executor.submit(flash, item, insert_fade, fade_step)
            except Exception as e:
                Base.log(
                    "E",
                    f"插入操作线程异常：[{sys.exc_info()[1].__class__.__name__}] {repr(e)}",
                    "MainWindow.insert_action_thread",
                )

    def insert_action_history_info(
        self,
        text: str,
        click_callback: Callable,
        insert_fade=(127, 225, 195, 255, 255, 255),
        fade_step=12,
    ):
        """
        插入操作历史项目

        :param text: 插入的文本
        :param click_callback: 项目被双击时的回调函数
        :param insert_fade: 插入的渐变颜色，前三项是起始颜色，后三项是结束颜色（rgb）
        :param fade_step: 渐变步长（是老版的参数名，懒得改了，费时间）
        """
        self.insert_queue.put((text, click_callback, insert_fade, fade_step))

    @Slot(QModelIndex)
    def click_opreation(self, index: QModelIndex):
        """
        点击历史信息列表项的操作处理函数

        :index: 传过来的索引，不用管（是自动的）
        """
        Base.log(
            "I",
            f"点击列表项:{index.row()}, {repr(self.listView_data[index.row()])}",
            "MainWindow.click_opreation",
        )
        self.listView_data[index.row()]()

    def mainloop(self) -> int:
        """
        主循环，跟tk的差不多
        """
        Base.log("I", "mainloop启动中...", "MainWindow.mainloop")
        self.is_running = True
        self.insert_action_history_info(
            "双击这种列表项目可查看信息",
            lambda: QMessageBox.information(self, "。", "孩子真棒"),
        )
        self.icon = QIcon()
        self.icon.addPixmap(
            QPixmap("img/favicon.ico"), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.setWindowIcon(self.icon)
        self.on_start_up_finished()
        self.show()
        self.updator_thread.start()
        Base.log("I", "线程启动完成，exec()", "MainWindow.mainloop")
        status = self.app.exec()
        Base.log("I", "主窗口关闭", "MainWindow")
        self.app.quit()
        self.updator_thread.terminate()
        self.tip_handler.terminate()
        return status

    ###########################################################################
    #                            事件触发相关                                  #
    ###########################################################################

    def on_start_up_finished(self):
        "当启动完成时调用，此时界面还没有展示"
        lt = time.localtime()
        if (lt.tm_mon, lt.tm_mday) == (4, 1):
            e = ClassObj.ObserverError(
                f"数据加载失败，详情请查看日志[{random.randint(114514, 1919810)}]"
            )
            self.question_if_exec(
                "警告",
                "数据加载出现错误！\n"
                + "".join(traceback.format_exception_only(e.__class__, e))
                + "\n\n"
                "是否查看解决方案？",
                lambda: (
                    os.startfile("https://www.bilibili.com/video/BV1kW411m7VP/"),
                    self.information("114514", "愚人节快乐"),
                ),
            )

    def on_auto_save_failure(self, exc_info: ExceptionInfoType):
        """处理自动保存失败的情况"""
        self.show_tip(
            "警告",
            "自动保存失败，请查看日志",
            self,
            duration=8000,
            closeable=False,
            icon=InfoBarIcon.WARNING,
            further_info=f"详细信息：\n\n{''.join(traceback.format_exception(*exc_info))}",
        )
        return super().on_auto_save_failure(exc_info)

    def on_exit(self):
        "将要退出时执行的操作"
        Base.log("I", "进行将要退出操作", "MainWindow.on_exit")
        t = Thread(target=self._do_exit)
        t.start()
        while t.is_alive():
            do_nothing()
        self.exit_action_finished = True

    def _do_exit(self):
        "退出时执行的操作，有东西写这里"
        self.save_data(self.save_path)
        self.save_current_settings()
        self.script_backup(self.auto_backup_scheme)
        self.class_obs.stop()
        self.achievement_obs.stop()
        self.updator_thread.terminate()

    ###########################################################################
    #                         算法核心接口相关                                 #
    ###########################################################################

    def display_achievement(self, achievement: str, student: Student):
        """
        显示成就获取通知

        :param achievement: 成就标识符
        :param student: 获得成就的学生对象
        """
        self.show_tip(
            "成就达成",
            f"{student.name} 达成了成就 [{self.achievement_templates[achievement].name}]",
            sound=self.achievement_templates[achievement].sound,
            icon=self.achievement_templates[achievement].icon,
            duration=5000,
            further_info="就是单纯一个成就，没啥好看的",
        )

    @Slot()
    @as_command("retract_lastest", "撤回上步")
    def retract_lastest(self):
        """撤回上步，覆写的是ClassObjects.retract_last"""
        if self.class_obs.opreation_record.size() == 0:
            Base.log("I", "暂无可以撤回的操作", "MainWindow.retract_last")
            QMessageBox.information(self, "提示", "暂无可以撤回的操作")
            return
        Base.log("I", "询问是否撤销上一次操作", "MainWindow.retract_last")
        if question_yes_no(
            self,
            "提示",
            f'是否撤销上一次操作？（共计{len(self.class_obs.opreation_record.peek())}条，包含"{self.class_obs.opreation_record.peek()[0].title}"等点评）',
            True,
            "question",
        ):
            result, reason = super().retract_lastest()
            if result:
                self.show_tip(
                    "提示",
                    "撤销执行完成",
                    duration=3275,
                    icon=InfoBarIcon.SUCCESS,
                    further_info=f"信息：\n\n执行结果：{'成功' if result else '失败'}\n"
                    f"详细：{reason!r}",
                )
            else:
                self.show_tip(
                    "警告",
                    "撤销出现问题",
                    duration=7275,
                    icon=InfoBarIcon.WARNING,
                    further_info=f"信息：\n\n执行结果：{'成功' if result else '失败'}\n"
                    f"详细：{reason!r}",
                )

    @Slot()
    @as_command("reset_scores", "重置分数")
    def reset_scores(self):
        """重置，覆写的是ClassObjects.reset"""
        Base.log("I", "询问是否重置", "MainWindow.reset")
        if question_yes_no(self, "提示", "是否进行周结算？"):
            super().reset_scores()

    def day_end(self, weekday: int, utc: float, show_msgbox: bool = True):
        """每日结算

        :param weekday: 星期几
        :param utc: UTC时间
        """
        if len(self.weekday_record):
            if any([utc <= day.utc for day in self.weekday_record]):  # 时间倒流了？？
                self.information(
                    "提示",
                    "时间倒流了？给我干哪天来了？\n\n"
                    f"（结算时间：{utc:.1f}, 历史记录记录到了{max([day.utc for day in self.weekday_record]):.1f}）\n"
                    "（如果这是你第一次使用本程序，那么请忽略此提示）",
                )

        Base.log("I", "准备每日结算", "MainWindow.day_end")
        yesterday = DayRecord(
            self.target_class, weekday, utc, self.current_day_attendance
        )
        self.weekday_record.append(yesterday)
        self.current_day_attendance = AttendanceInfo(
            self.target_class.key, [], [], [], [], [], []
        )
        try:
            if hasattr(self, "attendance_window"):
                self.attendance_window.close()
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            Base.log_exc("关闭考勤窗口失败", "MainWindow.day_end")
        if show_msgbox:
            self.information(
                "提示",
                f"{time.strftime('%Y年%m月%d日（%A）', time.localtime(utc))} 结束了！\n"
                f"考勤系统已经重置，今天又是没好的一天！\n"
                f"\n"
                f"（今天的日期：{time.strftime('%Y年%m月%d日，%A')}",
            )

    def config_data(
        self,
        path: str = os.getcwd() + os.sep + f"chunks/{default_user}/",
        silent: bool = False,
        strict=False,
        reset_missing=False,
        mode: Literal["sqlite", "pickle", "auto"] = "sqlite",
        load_full_histories=False,
        reset_current=True,
    ) -> UserDataBase:
        "加载数据并设置"
        self.load_succeed = False
        Base.log("I", "加载数据并设置", "MainWindow.config_data")
        d = super().config_data(
            path,
            silent,
            strict,
            reset_missing,
            mode,
            load_full_histories,
            reset_current,
        )
        if self.load_succeed:
            self.show_tip(
                "提示", "数据加载成功", self, duration=5000, icon=InfoBarIcon.SUCCESS
            )
            Base.log("I", "数据加载成功", "MainWindow.config_data")
        else:
            self.show_tip(
                "警告", "数据加载失败", self, duration=5000, icon=InfoBarIcon.WARNING
            )
            Base.log("E", "数据加载失败", "MainWindow.config_data")
        return d

    ###########################################################################
    #                               功能相关                                   #
    ###########################################################################

    ##### 分数模板 #####

    @Slot()
    @as_command("new_template", "新建模板")
    def new_template(self):
        """新建模板窗口"""
        self.new_template_window = NewTemplateWidget(self, self)
        self.new_template_window.show()

    @Slot()
    @as_command("manage_templates", "管理模板")
    def manage_templates(self):
        """管理模板窗口"""
        self.template_listbox = ListView(self, title="管理模板")
        self.manage_template_cursel_index = 0

        def _generate_action():
            data: List[Tuple[str, Callable]] = []
            Base.log("I", "正在生成模板列表", "MainWindow.manage_template")
            index = 0
            for template in self.modify_templates.values():
                data.append(
                    (
                        template.title,
                        lambda template=template, index=index: (
                            self.edit_template(template, index),
                            self.wait_till_close(self.new_template_window),
                            self.template_listbox.setData(_generate_action()),
                        ),
                    )
                )
                index += 1
            return data

        def _swap_index(index1: int, index2: int):
            Base.log(
                "I", f"正在交换模板 {index1} 和 {index2}", "MainWindow.manage_template"
            )
            self.modify_templates.swaps(index1, index2)

        def _move_up(index: int):
            if index == -1 or index == 0:
                return
            Base.log("I", f"正在上移模板 {index}", "MainWindow.manage_template")
            if index > 0:
                _swap_index(index, index - 1)
                self.template_listbox.setData(_generate_action())
                self.manage_template_cursel_index = max(index - 1, 0)

        def _move_down(index: int):
            if index == -1 or index == len(self.modify_templates) - 1:
                return
            Base.log("I", f"正在下移模板 {index}", "MainWindow.manage_template")
            if index < len(self.modify_templates) - 1:
                _swap_index(index, index + 1)
                self.template_listbox.setData(_generate_action())
                self.manage_template_cursel_index = min(
                    index + 1, len(self.modify_templates) - 1
                )

        def move_up():
            return (
                _move_up(self.template_listbox.listWidget.currentRow()),
                self.template_listbox.setData(_generate_action()),
                self.template_listbox.listWidget.setCurrentRow(
                    self.manage_template_cursel_index
                ),
            )

        def move_down():
            return (
                _move_down(self.template_listbox.listWidget.currentRow()),
                self.template_listbox.setData(_generate_action()),
                self.template_listbox.listWidget.setCurrentRow(
                    self.manage_template_cursel_index
                ),
            )

        self.template_listbox.setData(_generate_action())
        self.template_listbox.setCommands(
            [
                ("项目上移", move_up),
                ("项目下移", move_down),
                (
                    "新建模板",
                    lambda: (
                        self.new_template(),
                        self.wait_till_close(self.new_template_window),
                        (
                            self.template_listbox.setData(_generate_action())
                            if self.template_listbox.listWidget.count()
                            < len(self.modify_templates)
                            else None
                        ),
                    ),
                ),
                (
                    "删除模板",
                    lambda: (
                        self.question_if_exec(
                            "警告",
                            f"确定删除模板 "
                            f"{repr(list(self.modify_templates.values())[self.template_listbox.listWidget.currentRow()].title)} 吗？"
                            "\n删除后，它将会被移除出模板列表，\n但不会影响已经添加到列表中的项目且无法恢复。",
                            lambda: (
                                self.del_template(
                                    list(self.modify_templates.keys())[
                                        self.template_listbox.listWidget.currentRow()
                                    ],
                                    "模板列表快捷删除",
                                ),
                                time.sleep(0.5),
                                self.template_listbox.setData(_generate_action()),
                            ),
                        )
                        if self.template_listbox.listWidget.currentRow() != -1
                        else None
                    ),
                ),  # 出现了，古希腊掌管lambda的神
                (
                    "补充默认",
                    lambda: (
                        self.question_if_exec(
                            "提示",
                            "是否将默认模板补充到模板列表中？\n"
                            "这个操作会同时将默认成就，小组和班级补全，但是不会覆盖现有的数据。\n"
                            "（补充完了记得翻到底下看看！）",
                            lambda: (
                                self.reset_missing(),
                                self.template_listbox.setData(_generate_action()),
                            ),
                        )
                    ),
                ),
                (
                    "复原默认",
                    lambda: (
                        self.question_if_exec(
                            "警告",
                            "是否复原所有默认模板？\n"
                            "这个操作会覆盖现有的默认模板，当前的修改将会丢失。",
                            lambda: (
                                self.reset_all_defaults(),
                                self.template_listbox.setData(_generate_action()),
                            ),
                        )
                    ),
                ),
                (
                    "复原全部",
                    lambda: (
                        self.question_if_exec(
                            "警告",
                            "是否复原所有模板？\n"
                            "这个操作会重置现有的所有模板，新建的将会删除，修改将会丢失。",
                            lambda: (
                                self.reset_all_data(False),
                                self.template_listbox.setData(_generate_action()),
                            ),
                        )
                    ),
                ),
            ]
        )

        self.template_listbox.show()

    def edit_template(self, template: ScoreModificationTemplate, index: int):
        """
        编辑模板窗口

        :param template: 模板对象
        """
        self.new_template_window = EditTemplateWidget(
            self, self, template, self.template_listbox, index
        )
        self.new_template_window.show()

    def history_window(
        self,
        modify: ScoreModification,
        listbox_index: int,
        listbox_widget: Optional["ListView"] = None,
        readonly: bool = False,
        master=None,
        remove_in_listbox_when_retracted=True,
    ):
        """
        加载一个历史记录的窗口


        :param modify: 记录
        :param listbox_index: 在listview中的索引，写的是listbox是因为之前用tk，懒得改了
        :param readonly: 是否只读
        :param master: 主窗口，没用到
        :param remove_in_listbox_when_retracted: 是否在撤销时从listview中移除，没实现
        """
        Base.log("I", f"选中历史记录： {modify}", "StudentWidget.history_detail")
        self.history_detail_window = HistoryWidget(
            self,
            self,
            modify,
            self.lastest_listview if listbox_widget is None else listbox_widget,
            listbox_index,
            readonly or (not modify.executed),
        )
        self.history_detail_window.show(readonly)

    @Slot()
    @as_command("scoring_select", "多选学生")
    def scoring_select(self, *, students: List[Student] = None):
        """多选并发送"""
        if students is None:
            # 如果没有传入学生则默认为当前班级的所有学生
            students = list(self.target_class.students.values())
        self.multi_select_window = StudentSelectorWidget(self, None, students)
        self.multi_select_window.return_result.connect(self.send_to_students)
        self.multi_select_window.show()

    def send_to_students(self, result: List[Student]):
        """选择点评发给指定学生"""
        self.multi_select_template_window = SelectTemplateWidget(self, self)
        self.multi_select_template_window.show()
        self.multi_select_template_window.return_result.connect(
            lambda selection, students=result: self.send_modify(
                selection[0], students, selection[1], selection[2], selection[3]
            )
        )
        self.multi_select_template_window.select()

    @Slot()
    @as_command("save", "保存数据")
    def save(self):
        "保存当前存档。"
        if self.last_save_from_action - time.time() < -3:
            Base.log("I", "保存当前存档", "MainWindow.save")
            self.last_save_from_action = time.time()
            Thread(
                target=lambda: (
                    self.save_current_settings(),
                    self.save_data(self.save_path),
                    self.save_quick_command_config(),
                    self.show_tip(
                        "提示",
                        "保存成功",
                        icon=InfoBarIcon.SUCCESS,
                        duration=2500,
                        further_info="保存成功，没什么好说的",
                    ),
                    Base.log("I", "存档保存完成", "MainWindow.save"),
                )
            ).start()

    def refresh_hint_widget(self, mode: int = 0):
        """
        刷新提示

        :param mode: 模式，按照范围划分
        """
        self.refresh_hint_widget_signal.emit(mode)

    def _refresh_hint_widget(self, mode: int = 0):
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
            self.label_23.setText("小提示")
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
                self.label_22.setText(text + ("\n（点击刷新）" if tip_refresh else ""))
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
                self.label_23.setText("小提示")
                self.label_22.setText(
                    random.choice(hints) + ("\n（点击刷新）" if tip_refresh else "")
                )

    @Slot()
    @as_command("open_setting_window", "设置窗口")
    def open_setting_window(self):
        """设置窗口"""
        Base.log("I", "打开设置窗口", "MainWindow.setting_window")
        self.setting_window = SettingWidget(mainwindow=self, master_widget=self)
        self.setting_window.show()

    @Slot()
    @as_command("cleaning_score_sum_up", "卫生分结算")
    def cleaning_score_sum_up(self):
        """打扫分数结算"""
        Base.log("I", "打开打扫分数结算窗口", "MainWindow.cleaning_sumup")
        self.cleaning_sumup_window = CleaningScoreSumUpWidget(
            mainwindow=self, master_widget=self
        )
        self.cleaning_sumup_window.show()

    def student_info(
        self, student: Student, master_widget=None, readonly: bool = False
    ):
        """
        展示学生信息

        :param student: 学生
        """
        Base.log(
            "I", f"打开学生信息窗口，学生名：{student.name}", "MainWindow.student_info"
        )
        self.student_info_window = StudentWidget(
            mainwindow=self,
            student=student,
            master_widget=master_widget or self,
            readonly=readonly,
        )
        self.student_info_window.set_student(student)
        self.student_info_window.pushButton_3.setDisabled(readonly)
        self.student_info_window.show(readonly)

    def group_info(
        self,
        group: Group,
        master_widget: Optional[WidgetType] = None,
        readonly: bool = False,
    ):
        """
        展示小组信息

        :param group: 小组
        """
        Base.log(
            "I", f"打开小组信息窗口，小组名：{group.name}", "MainWindow.group_info"
        )
        self.group_info_window = GroupWidget(
            self, (self if master_widget is None else master_widget), group, readonly
        )
        self.group_info_window.show(readonly)

    @Slot()
    @as_command("random_select", "随机选取")
    def random_select(self):
        """随机选择学生窗口"""
        Base.log("I", "打开随机选择学生窗口", "MainWindow.random_select")
        self.random_select_window = RandomSelectWidget(self, self)
        self.random_select_window.show()

    @Slot()
    @as_command("homework_score_sum_up", "作业分结算")
    def homework_score_sum_up(self):
        """作业总分结算窗口"""
        Base.log("I", "打开作业总分结算窗口", "MainWindow.homework_sumup")
        self.homework_sumup_window = HomeworkScoreSumUpWidget(
            mainwindow=self,
            master=self,
            target_class=self.target_class,
            target_students=self.target_class.students,
        )
        self.homework_sumup_window.show()

    @Slot()
    @as_command("show_attendance", "考勤记录")
    def show_attendance(self):
        """显示考勤"""
        self.attendance_window = AttendanceInfoWidget(
            self, self, self.current_day_attendance
        )
        self.attendance_window.show()

    @Slot()
    @as_command("show_all_history", "历史记录")
    def show_all_history(self):
        """显示所有历史"""
        if not hasattr(self, "is_loading_all_history"):
            self.is_loading_all_history = False
        if self.is_loading_all_history:
            Base.log("I", "还正在加载历史记录", "MainWindow.show_all_history")
        finished = False

        def _load_history():
            nonlocal finished
            self.show_tip("提示", "正在保存当前数据以保证完整性", duration=2000)
            self.save_data()
            self.show_tip("提示", "历史记录正在加载中，请稍等", duration=2000)
            self.config_data(
                os.getcwd() + os.sep + f"chunks/{self.current_user}",
                load_full_histories=True,
                reset_current=False,
                strict=True,
            )
            finished = True

        self.is_loading_all_history = True
        Thread(target=_load_history, name="HistoryLoader").start()
        self.is_loading_all_history = False
        while not finished:
            do_nothing()
        view = ListView(
            self,
            self,
            "所有历史记录",
            [
                (
                    f"位于{time.localtime(history.time).tm_year}/{time.localtime(history.time).tm_mon}/{time.localtime(history.time).tm_mday} {time.localtime(history.time).tm_hour}:{time.localtime(history.time).tm_min:02}:{time.localtime(history.time).tm_sec:02}的历史记录",
                    lambda h=history: self.show_classes_history(h.classes),
                )
                for history in self.history_data.values()
            ],
        )
        view.setCommands(
            [
                (
                    "删除最早记录",
                    lambda: (
                        self.question_if_exec(
                            "警告",
                            "最早的一次记录来自于"
                            f"{time.localtime(list(self.history_data)[0]).tm_year}/"
                            f"{time.localtime(list(self.history_data)[0]).tm_mon}/"
                            f"{time.localtime(list(self.history_data)[0]).tm_mday} "
                            f"{time.localtime(list(self.history_data)[0]).tm_hour}:"
                            f"{time.localtime(list(self.history_data)[0]).tm_min:02}:"
                            f"{time.localtime(list(self.history_data)[0]).tm_sec:02};\n"
                            "接下来的操作将会彻底删除这个时间段的记录，此操作不可逆！\n\n"
                            "你确定要删除吗？",
                            lambda: (
                                Chunk(self.save_path, None).del_history(
                                    list(self.history_data.values())[0].uuid
                                ),
                                self.history_data.pop(list(self.history_data)[0]),
                                self.insert_action_history_info(
                                    "删除"
                                    f"{time.localtime(list(self.history_data)[0]).tm_year}/"
                                    f"{time.localtime(list(self.history_data)[0]).tm_mon}/"
                                    f"{time.localtime(list(self.history_data)[0]).tm_mday} "
                                    f"{time.localtime(list(self.history_data)[0]).tm_hour}:"
                                    f"{time.localtime(list(self.history_data)[0]).tm_min:02}:"
                                    f"{time.localtime(list(self.history_data)[0]).tm_sec:02}的记录",
                                    self.show_all_history,
                                    (201, 94, 232, 235, 176, 252),
                                    40,
                                ),
                                self.information(
                                    "提示", "删除成功，请重新加载此窗口！"
                                ),
                                view.close(),
                            ),
                        )
                        if len(self.history_data)
                        else (self.information("提示", "没有历史记录可以删除..."))
                    ),
                ),
                (
                    "删除所有记录",
                    lambda: (
                        (
                            self.question_if_exec(
                                "警告",
                                "你确定要删除所有记录吗？\n"
                                "接下来的操作将会彻底删除所有记录，没错，是所有，请慎重！\n\n"
                                f"当前共有{len(self.history_data)}条历史记录, "
                                "你确定要删除吗？",
                                lambda: (
                                    self.insert_action_history_info(
                                        f"删除所有的历史记录（{len(self.history_data)}）",
                                        self.show_all_history,
                                        (142, 30, 114, 246, 139, 219),
                                        40,
                                    ),
                                    self.history_data.clear(),
                                    self.information(
                                        "提示", "删除成功，请重新加载此窗口！"
                                    ),
                                    view.close(),
                                ),
                            )
                        )
                        if len(self.history_data)
                        else (self.information("提示", "没有历史记录可以删除..."))
                    ),
                ),
            ]
        )
        view.show()

    def show_classes_history(self, classes: Dict[str, Class]):
        """显示所有班级历史"""
        self.listview_history_classes = ListView(
            self,
            self,
            "所有班级历史记录",
            [
                (
                    _class.name,
                    lambda _class=_class: self.show_class_history(
                        _class, _class.groups.values()
                    ),
                )
                for _class in classes.values()
            ],
        )
        self.listview_history_classes.show()

    def show_class_history(self, target_class: Class, groups: List[Group]):
        """显示单个班级历史"""
        self.listview_history_class = ListView(
            self,
            self,
            f"{target_class.name}的历史记录",
            [("所有学生", lambda: None)]
            + [("", lambda: None)]
            + [
                (
                    f"第{ranking}名 {stu.name} {stu.score}",
                    lambda stu=stu: self.student_info(
                        stu, master_widget=self, readonly=True
                    ),
                )
                for ranking, stu in target_class.rank_non_dumplicate
            ]
            + [("", lambda: None)] * 2
            + [("所有小组", lambda: None)]
            + [("", lambda: None)]
            + [
                (
                    f"第{ranking}名 {grp.name} {grp.total_score}",
                    lambda grp=grp: self.group_info(
                        grp, master_widget=self, readonly=True
                    ),
                )
                for ranking, grp in [
                    (ranking, grp)
                    for ranking, grp in enumerate(
                        sorted(groups, key=lambda grp: grp.total_score, reverse=True),
                        start=1,
                    )
                    if grp.belongs_to == target_class.key
                ]
            ],
        )
        self.listview_history_class.show()

    def list_view(
        self,
        data: List[Tuple[str, Callable]],
        title: str,
        master: Optional[WidgetType] = None,
        commands: List[Tuple[str, Callable]] = None,
        select_once_then_exit: bool = False,
    ):
        """显示一个列表框

        :param data: 数据, 每个元素是一个元组，
        第一个元素是显示的文本，第二个元素是一个函数，列表项点击后执行
        :param title: 标题
        :param master: 父窗口
        :param commands: 命令，每个元素是一个元组，
        第一个元素是显示的文本，第二个元素是一个函数，会以按钮形式显示在列表一边，点击后执行
        """
        self.lastest_listview = ListView(
            mainwindow=self,
            master_widget=master,
            data=data,
            title=title,
            commands=commands,
            select_once_then_exit=select_once_then_exit,
        )
        self.lastest_listview.show()

    @Slot()
    @as_command("stu_ranking", "学生排名")
    def student_rank(self):
        """显示学生排名"""
        self.list_view(
            [
                (
                    f"第{rank}名 {stu.name} {stu.score}分",
                    lambda: None,
                    (
                        (QColor(255, 255, 222), QColor(251, 220, 95))
                        if rank == 1 and stu.score > 0
                        else (
                            (QColor(244, 244, 244), QColor(232, 232, 232))
                            if rank == 2 and stu.score > 0
                            else (
                                (QColor(255, 255, 255), QColor(223, 162, 140))
                                if rank == 3 and stu.score > 0
                                else (
                                    (
                                        QColor(222, 255, 222),
                                        QColor(
                                            max(
                                                202,
                                                242 - ((stu.score) * (255 - 202) / 30),
                                            ),
                                            255,
                                            max(
                                                202,
                                                242 - ((stu.score) * (255 - 202) / 30),
                                            ),
                                        ),
                                    )
                                    if stu.score > 0
                                    else (
                                        (
                                            QColor(255, 222, 222),
                                            QColor(
                                                255,
                                                max(
                                                    202,
                                                    242
                                                    + ((stu.score) * (255 - 202) / 30),
                                                ),
                                                max(
                                                    202,
                                                    242
                                                    + ((stu.score) * (255 - 202) / 30),
                                                ),
                                            ),
                                        )
                                        if stu.score < 0
                                        else (
                                            QColor(233, 244, 255),
                                            QColor(255, 255, 255),
                                        )
                                    )
                                )
                            )
                        )
                    ),
                )
                for rank, stu in self.class_obs.rank_non_dumplicate
            ],
            "学生排名",
            self,
        )

    @Slot()
    @as_command("show_recover_points", "显示还原点")
    def show_recover_points(self):
        """显示还原点"""
        Base.log("I", "读取列表", "MainWindow.show_recovery_point")
        if not os.path.exists(self.backup_path + "backup_info.dat"):
            pickle.dump({}, open(self.backup_path + "backup_info.dat", "wb"))
        self.recovery_points: Dict[float, RecoveryPoint] = pickle.load(
            open(self.backup_path + "backup_info.dat", "rb")
        )
        Base.log("I", "检查各个还原点", "MainWindow.show_recovery_point")

        Base.log("I", "显示列表", "MainWindow.show_recovery_point")
        self.list_view(
            [
                (
                    f"在 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(point.time))} 创建的还原点",  # + f"  {'可用' if point.stat == 'active' else '损坏' if point.stat == 'damaged' else '不存在' if point.stat == 'missed' else '未知错误'}",
                    lambda point=point: self.load_recovery_point(point),
                )
                for point in self.recovery_points.values()
            ],
            "还原点",
            self,
        )

    def load_recovery_point(self, point: "RecoveryPoint"):
        """加载还原点"""
        Base.log("I", "询问是否加载还原点", "MainWindow.load_recovery_point")
        if question_yes_no(
            self,
            "提示",
            "是否加载还原点？\n恢复后，需要手动重启程序。\n还原点将会覆盖当前存档且无法恢复。",
            False,
            "warning",
        ):
            try:
                point.load_onlydata_and_set(self.current_user)
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                Base.log("E", "加载还原点失败", "MainWindow.load_recovery_point")
                QMessageBox.critical(
                    self,
                    "错误",
                    "加载还原点失败:\n\n"
                    + traceback.format_exc()
                    + "\n\n请尝试重新创建还原点",
                )
            else:
                Base.log("I", "加载还原点成功", "MainWindow.load_recovery_point")

    @Slot()
    @as_command("create_recovery_point", "创建还原点")
    def create_recover_point(self):
        """创建还原点"""
        Base.log("I", "询问是否创建还原点", "MainWindow.create_recovery_point")
        if question_yes_no(
            self, "提示", "是否在当前时间创建数据还原点？", True, "question"
        ):
            self.script_backup("only_data")
            self.show_tip(
                "提示", "还原点创建成功", self, duration=5000, icon=InfoBarIcon.SUCCESS
            )
            self.insert_action_history_info(
                "创建还原点",
                self.show_recover_points,
                (162, 216, 162, 232, 255, 255),
                30,
            )

    ###########################################################################
    #                        其他零散功能                                      #
    ###########################################################################

    @Slot()
    @as_command("show_update_log", "更新日志")
    def show_update_log(self):
        self.information(
            (
                "更新了！"
                if self.client_version_code < CLIENT_VERSION_CODE
                else "更新日志"
            ),
            (
                (
                    f"版本更新：{self.client_version} -> {CLIENT_VERSION}\n\n"
                    if self.client_version_code < CLIENT_VERSION_CODE
                    else "更新日志\n\n"
                )
                + (
                    CLIENT_UPDATE_LOG[CLIENT_VERSION_CODE].strip()
                    if CLIENT_VERSION_CODE in CLIENT_UPDATE_LOG
                    else "貌似没写更新日志\n这种一般都是例行维护\n"
                )
                + (
                    '\n\n在顶边栏的"其他"中可以再次查看更新日志。'
                    if self.client_version_code < CLIENT_VERSION_CODE
                    else ""
                )
            ).strip(),
        )

    def wait_till_close(self, window: QWidget):
        """等待窗口关闭"""
        while window.isVisible():
            self.app.processEvents()

    @as_command("detect_new_version", "检测新版本")
    def detect_new_version(self):
        "检测新版本"
        Base.log("I", "检测新版本", "MainWindow.detect_new_version")
        Thread(target=self.updator_thread.detect_new_version).start()

    @Slot()
    def dont_click(self, style: Optional[int] = 0):
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
        self.dont_click_button_clicked.emit(style)

    @Slot()
    def _dont_click(self, style: int):
        "千万别点被点击时的接口"
        style = random.randint(1, 7) if style == 0 else style
        self.log("I", f"按钮被点击，本次执行类型：{style}", "MainWindow.dont_click")

        if style == 1:
            os.startfile("https://www.bilibili.com/video/BV1kW411m7VP/")

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
                time.sleep(0.03)
                do_nothing()
            self.move(200, 100)

        elif style == 7:
            orig_pos: Dict[QPoint, QWidget] = {}
            for obj in self.findChildren(QWidget):
                orig_pos[obj] = obj.geometry().topLeft()

            for i in range(100):
                for obj in self.findChildren(QWidget):
                    obj.move(
                        random.randint(0, self.width() // 2),
                        random.randint(0, self.height() // 2),
                    )
                do_nothing()
                time.sleep(0.05)

            for obj in self.findChildren(QWidget):
                try:
                    obj.move(orig_pos[obj].x(), orig_pos[obj].y())
                except KeyError as unused:
                    pass

    def script_backup(self, mode: Literal["none", "all", "only_data"] = "only_data"):
        """执行应用程序备份

        :param mode: 备份模式
            "none": 不执行备份
            "all": 备份所有程序文件
            "only_data": 仅备份数据文件
        """
        if not os.path.exists(self.backup_path):
            os.mkdir(self.backup_path)
        try:
            infof: Dict[float, str] = pickle.load(
                open(self.backup_path + "backup_info.dat", "rb")
            )
        except FileNotFoundError:
            infof = {}
        except pickle.PickleError:
            Base.log_exc("备份信息文件损坏", "MainWindow.script_backup")
            QMessageBox.critical(self, "错误", "备份信息文件损坏，已经重置备份信息文件")
            infof = {}
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            Base.log_exc("备份信息文件损坏", "MainWindow.script_backup")
            QMessageBox.critical(
                self,
                "错误",
                "加载备份信息文件出错：\n"
                + traceback.format_exc()
                + "\n可以尝试过一会再试试？",
            )
            return

        today_and_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())

        if mode == "none":
            Base.log("I", "脚本备份已关闭，跳过此步", "MainWindow.script_backup")
            return

        if mode == "only_data":
            Base.log("I", "正在对数据文件进行备份...", "MainWindow.script_backup")
            try:
                p = self.backup_path + f"dataonly/b_{today_and_time}"
                for i in range(6):
                    try:
                        copytree("chunks", p + "/chunks")
                    except Exception as e:
                        if i > 4:
                            raise e
                    else:
                        break

                t = time.time()
                infof[t] = RecoveryPoint(p, mode, "active")
                Base.log("I", "备份成功！", "MainWindow.script_backup")

            except BaseException as unused:  # pylint: disable=broad-exception-caught
                Base.log_exc("保存失败！", "MainWindow.script_backup")

        if mode == "all":
            Base.log("I", "正在对完整程序进行备份...", "MainWindow.script_backup")
            try:
                copytree(os.getcwd(), "backup_tmp")
                for i in range(6):
                    try:
                        copytree(
                            "backup_tmp", self.backup_path + f"full/b_{today_and_time}"
                        )
                        rmtree("backup_tmp")
                    except OSError as e:
                        if i > 4:
                            raise e
                    else:
                        break

                t = time.time()
                infof[t] = RecoveryPoint(p, mode, "active")
                Base.log("I", "备份成功！", "MainWindow.script_backup")

            except BaseException as unused:  # pylint: disable=broad-exception-caught
                Base.log_exc("保存失败！", "MainWindow.script_backup")

        pickle.dump(infof, open(self.backup_path + "backup_info.dat", "wb"))

    def exec_command(self, command: str):
        Base.log("I", f"执行命令：{repr(command)}", "MainWindow.exec_command")
        self.terminal_locals.update({"self": self})
        self.terminal_locals.update(globals())
        ret = None
        try:
            ret = eval(command, globals(), self.terminal_locals)
        except SyntaxError:
            exec(f"{command}", globals(), self.terminal_locals)
        return ret

    @Slot()
    @as_command("refresh_window", "刷新窗口")
    def refresh_window(self):
        Base.log("I", "刷新窗口", "MainWindow.refresh_window")
        self.updator_thread.terminate()
        self.updator_thread = UpdateThread(self, self)
        self.updator_thread.start()

    @Slot()
    @as_command("about_this", "关于工具")
    def about_this(self):
        "显示关于信息"
        Base.log("I", "显示关于", "MainWindow.about")
        self.about_window = AboutWidget(self, self)
        self.about_window.show()

    @as_command("show_debug_window", "调试窗口")
    def show_debug_window(self):
        "显示调试窗口"
        Base.log("I", "显示调试窗口", "MainWindow.show_debug_window")
        self.debug_window = DebugWidget(self, self)
        self.debug_window.show()

    @Slot()
    @as_command("save_data_as", "另存为")
    def save_data_as(self):
        """另存为"""
        path = QFileDialog.getSaveFileName(
            self, "另存为", self.save_path, "数据文件 (分散文件)"
        )[0]
        if path:
            self.save_data(path)

    @Slot()
    @as_command("music_selector", "播放音乐")
    def music_selector(self):
        Base.log("I", "按钮被点击", "MainWindow.music_selector")
        music_list: List[Tuple[str, Callable]] = []
        self.music_listview: ListView
        for f in os.listdir("audio/music"):
            if f.endswith((".mp3", ".ogg", ".wav", ".flac", ".m4a", ".ape")):
                music_list.append(
                    (
                        f.rsplit(".", 1)[0],
                        lambda f=f: (
                            play_music("audio/music/" + f, volume=0.8, loop=2**31 - 1),
                            self.music_listview.close(),
                            self.show_tip("提示", f"播放音乐：{f.rsplit('.', 1)[0]}"),
                        ),
                    )
                )
        music_list.sort()
        music_list.append(
            (
                "<停止播放>",
                lambda: (
                    stop_music(),
                    self.music_listview.close(),
                    self.show_tip("提示", "停止播放音乐"),
                ),
            )
        )

        if len(music_list) == 0:
            Base.log("W", "没有找到音乐文件", "MainWindow.music_selector")
            return
        Base.log("I", f"找到{len(music_list)}个音乐文件", "MainWindow.music_selector")
        Base.log("I", "正在选择音乐", "MainWindow.music_selector")
        self.music_listview = ListView(self, self, "选择音乐", music_list)
        self.music_listview.show()

    @Slot()
    @as_command("show_noise_detector", "噪声检测器")
    def show_noise_detector(self):
        if HAS_PYAUDIO:
            Base.log("I", "启动噪声检测器", "MainWindow.show_noise_detector")
            self.noise_detector = NoiseDetectorWidget(self, self)
            self.noise_detector.show()
        else:
            self.warning("提示", "没有找到pyaudio库，无法启动噪声检测器...")


class UpdateThread(QThread):
    """更新线程，更新主界面的按钮什么之类的东西"""

    first_loop = True
    "是否是第一次循环"

    def __init__(
        self, parent: Optional[WidgetType] = None, mainwindow: ClassWindow = None
    ):
        "初始化"
        super().__init__(parent=parent)
        Base.log("I", "更新线程初始化完成", "UpdateThread.__init__")
        self.mainwindow = mainwindow
        self.running = True
        self.stopped = False
        self.last_day_time = 0
        self.button_shown = False
        self.button_state_last_change = time.time()
        self.last_student_list = [s for s in self.mainwindow.target_class.students]
        self.last_group_list = [g for g in self.mainwindow.target_class.groups]
        self.lastest_score: Dict[int, float] = {}
        self.lastest_grp_score: Dict[str, float] = {}

    def update_stu_btns(self):
        "更新主窗口的学生按钮"
        if self.last_student_list != [s for s in self.mainwindow.target_class.students]:
            Base.log("I", "学生列表变动, 准备更新", "UpdateThread.run")
            self.last_student_list = [s for s in self.mainwindow.target_class.students]
            self.lastest_score = {
                s: 0 for s in self.mainwindow.target_class.students.keys()
            }
            self.mainwindow.grid_buttons()
            Base.log("I", "学生列表更新完成", "UpdateThread.run")
        for num, stu in self.mainwindow.target_class.students.items():
            self.mainwindow.stu_buttons[num].setText(
                f"{stu.num}号 {stu.name}\n{stu.score}分"
            )
            if stu.score > self.lastest_score[stu.num]:
                begin = self.mainwindow.score_up_color_mixin_begin
                end = self.mainwindow.score_up_color_mixin_end
                step = self.mainwindow.score_up_color_mixin_step
                mixin_start = self.mainwindow.score_up_color_mixin_start
                value = abs(int(stu.score) - int(self.lastest_score[stu.num]))
                self.mainwindow.button_update.emit(
                    self.mainwindow.stu_buttons[num],
                    (
                        (
                            int(
                                min(
                                    begin[0],
                                    max(
                                        end[0],
                                        begin[0]
                                        - max(value - mixin_start, 0)
                                        * ((begin[0] - end[0]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[1],
                                    max(
                                        end[1],
                                        begin[1]
                                        - max(value - mixin_start, 0)
                                        * ((begin[1] - end[1]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[2],
                                    max(
                                        end[2],
                                        begin[2]
                                        - max(value - mixin_start, 0)
                                        * ((begin[2] - end[2]) / step),
                                    ),
                                )
                            ),
                        ),
                        (255, 255, 255),
                        min(
                            self.mainwindow.score_up_flash_framelength_max,
                            int(
                                value * self.mainwindow.score_up_flash_framelength_step
                                + self.mainwindow.score_up_flash_framelength_base
                            ),
                        ),
                    ),
                )
                self.lastest_score[stu.num] = stu.score
            elif stu.score < self.lastest_score[stu.num]:
                begin = self.mainwindow.score_down_color_mixin_begin
                end = self.mainwindow.score_down_color_mixin_end
                step = self.mainwindow.score_down_color_mixin_step
                mixin_start = self.mainwindow.score_down_color_mixin_start
                value = abs(stu.score - self.lastest_score[stu.num])
                self.mainwindow.button_update.emit(
                    self.mainwindow.stu_buttons[num],
                    (
                        (
                            int(
                                min(
                                    begin[0],
                                    max(
                                        end[0],
                                        begin[0]
                                        - max(value - mixin_start, 0)
                                        * ((begin[0] - end[0]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[1],
                                    max(
                                        end[1],
                                        begin[1]
                                        - max(value - mixin_start, 0)
                                        * ((begin[1] - end[1]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[2],
                                    max(
                                        end[2],
                                        begin[2]
                                        - max(value - mixin_start, 0)
                                        * ((begin[2] - end[2]) / step),
                                    ),
                                )
                            ),
                        ),
                        (255, 255, 255),
                        min(
                            self.mainwindow.score_up_flash_framelength_max,
                            int(
                                value
                                * self.mainwindow.score_down_flash_framelength_step
                                + self.mainwindow.score_down_flash_framelength_base
                            ),
                        ),
                    ),
                )
                if (
                    self.lastest_score[stu.num] - stu.score >= 1145
                    and not self.first_loop
                ):
                    play_sound("audio/sounds/boom.mp3", volume=0.2)
                    Base.log(
                        "I",
                        f"不是哥们，真有人能扣"
                        f"{self.lastest_score[stu.num] - stu.score:.1f}分？犯天条了？",
                        "UpdateThread.run",
                    )

                self.lastest_score[stu.num] = stu.score
            time.sleep(0.002)

    def update_grp_btns(self):
        "更新主界面的小组按钮"
        if self.last_group_list != [g for g in self.mainwindow.target_class.groups]:
            Base.log("I", "小组列表变动, 准备更新", "UpdateThread.run")
            self.last_group_list = [g for g in self.mainwindow.target_class.groups]
            self.lastest_grp_score = {
                g: 0 for g in self.mainwindow.target_class.groups.keys()
            }
            self.mainwindow.grid_buttons()
            Base.log("I", "小组列表更新完成", "UpdateThread.run")

        for key, grp in self.mainwindow.target_class.groups.items():
            grp: Group
            self.mainwindow.grp_buttons[key].setText(
                f"{grp.name}\n\n总分 {grp.total_score:.1f}分\n"
                f"平均 {grp.average_score:.2f}分\n"
                f"去最低平均 {grp.average_score_without_lowest:.2f}分"
            )
            if grp.total_score > self.lastest_grp_score[key]:
                begin = self.mainwindow.score_up_color_mixin_begin
                end = self.mainwindow.score_up_color_mixin_end
                step = self.mainwindow.score_up_color_mixin_step
                mixin_start = self.mainwindow.score_up_color_mixin_start
                value = abs(int(grp.total_score) - int(self.lastest_grp_score[key]))
                self.mainwindow.button_update.emit(
                    self.mainwindow.grp_buttons[key],
                    (
                        (
                            int(
                                min(
                                    begin[0],
                                    max(
                                        end[0],
                                        begin[0]
                                        - max(value - mixin_start, 0)
                                        * ((begin[0] - end[0]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[1],
                                    max(
                                        end[1],
                                        begin[1]
                                        - max(value - mixin_start, 0)
                                        * ((begin[1] - end[1]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[2],
                                    max(
                                        end[2],
                                        begin[2]
                                        - max(value - mixin_start, 0)
                                        * ((begin[2] - end[2]) / step),
                                    ),
                                )
                            ),
                        ),
                        (255, 255, 255),
                        min(
                            self.mainwindow.score_up_flash_framelength_max,
                            int(
                                value * self.mainwindow.score_up_flash_framelength_step
                                + self.mainwindow.score_up_flash_framelength_base
                            ),
                        ),
                    ),
                )
                self.lastest_grp_score[key] = grp.total_score
            elif grp.total_score < self.lastest_grp_score[key]:
                begin = self.mainwindow.score_down_color_mixin_begin
                end = self.mainwindow.score_down_color_mixin_end
                step = self.mainwindow.score_down_color_mixin_step
                mixin_start = self.mainwindow.score_down_color_mixin_start
                value = abs(grp.total_score - self.lastest_grp_score[key])
                self.mainwindow.button_update.emit(
                    self.mainwindow.grp_buttons[key],
                    (
                        (
                            int(
                                min(
                                    begin[0],
                                    max(
                                        end[0],
                                        begin[0]
                                        - max(value - mixin_start, 0)
                                        * ((begin[0] - end[0]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[1],
                                    max(
                                        end[1],
                                        begin[1]
                                        - max(value - mixin_start, 0)
                                        * ((begin[1] - end[1]) / step),
                                    ),
                                )
                            ),
                            int(
                                min(
                                    begin[2],
                                    max(
                                        end[2],
                                        begin[2]
                                        - max(value - mixin_start, 0)
                                        * ((begin[2] - end[2]) / step),
                                    ),
                                )
                            ),
                        ),
                        (255, 255, 255),
                        min(
                            self.mainwindow.score_up_flash_framelength_max,
                            int(
                                value
                                * self.mainwindow.score_down_flash_framelength_step
                                + self.mainwindow.score_down_flash_framelength_base
                            ),
                        ),
                    ),
                )
                self.lastest_grp_score[key] = grp.total_score

    def detect_update(self):
        "检测是否有更新过"
        if self.mainwindow.client_version_code < CLIENT_VERSION_CODE:
            play_sound("audio/sounds/orb.ogg")
            self.mainwindow.show_update_log()
            self.mainwindow.client_version_code = CLIENT_VERSION_CODE
            self.mainwindow.client_version = CLIENT_VERSION
            self.mainwindow.save_current_settings()

    def detect_new_version(self, from_system: bool = True):
        "检测是否有新版本"
        from utils.update_check import (
            update_check,
            update,
            unzip_to_dir,
            get_update_zip,
        )
        from utils.update_check import AUTHOR, MASTER, REPO_NAME
        from utils.update_check import UpdateInfo

        Base.log("I", "检测更新...", "UpdateThread.detect_new_version")
        res, info = update_check(CORE_VERSION_CODE, CLIENT_VERSION_CODE)
        Base.log("I", f"返回结果：{res}", "UpdateThread.detect_new_version")
        if res == UpdateInfo.ERROR:
            Base.log_exc(
                "检测更新出现错误", "UpdateThread.detect_new_version", exc=info
            )
            self.mainwindow.show_tip(
                "错误",
                "检测更新出现错误，请检查网络连接",
                duration=5000,
                icon=InfoBarIcon.ERROR,
                further_info="详细信息：\n\n"
                + "".join(
                    traceback.format_exception(type(info), info, info.__traceback__)
                ),
            )

        elif res == UpdateInfo.UPDATE_AVAILABLE:
            self.mainwindow.show_tip("提示", "发现新版本！", duration=5000)

            def update_self(self: UpdateThread):

                self.mainwindow.show_tip("提示", "正在下载更新...", duration=5000)

                def _update(self: UpdateThread):
                    try:
                        get_update_zip()
                        unzip_to_dir()
                        self.mainwindow.information(
                            "更新下载完成",
                            "10秒之后将会重启程序以完成更新。（按任意键关闭后开始计时）",
                        )
                        time.sleep(10)
                        self.mainwindow.save_data()
                        self.mainwindow.save_current_settings()
                        while self.mainwindow.auto_saving:
                            time.sleep(0.1)
                        update()

                    except Exception as e:
                        Base.log_exc("更新出现错误", "UpdateThread.update_self")
                        self.mainwindow.show_tip(
                            "错误",
                            "更新出现错误",
                            duration=5000,
                            icon=InfoBarIcon.ERROR,
                            further_info="详细信息：\n\n"
                            + "".join(
                                traceback.format_exception(type(e), e, e.__traceback__)
                            ),
                        )

                Thread(target=lambda: _update(self)).start()

            if not sys.argv[0].endswith(".py"):
                Base.log(
                    "I", "当前为发行版，无法自动更新", "UpdateThread.detect_new_version"
                )
                self.mainwindow.question_if_exec(
                    "发现新版本！",
                    "有新版本了！\n\n"
                    f"界面版本：{CLIENT_VERSION}({CLIENT_VERSION_CODE})"
                    f" -> {info['client_version']}({info['client_version_code']})\n"
                    f"核心版本：{CORE_VERSION}({CORE_VERSION_CODE})"
                    f" -> {info['core_version']}({info['core_version_code']})\n\n"
                    "是否要打开外部网站？\n"
                    f"（https://gitee.com/{AUTHOR}/{REPO_NAME}）\n",
                    lambda: os.startfile(f"https://gitee.com/{AUTHOR}/{REPO_NAME}"),
                )
            else:
                self.mainwindow.question_if_exec(
                    "发现新版本!",
                    "有新版本了！\n\n"
                    f"界面版本：{CLIENT_VERSION}({CLIENT_VERSION_CODE})"
                    f" -> {info['client_version']}({info['client_version_code']})\n"
                    f"核心版本：{CORE_VERSION}({CORE_VERSION_CODE})"
                    f" -> {info['core_version']}({info['core_version_code']})\n\n"
                    "是否更新？",
                    lambda: update_self(self),
                    QPixmap("./img/logo/favicon-update.png"),
                )

        elif res == UpdateInfo.NO_UPDATE:
            self.mainwindow.show_tip("提示", "当前已是最新版本。", duration=5000)

        elif res == UpdateInfo.VERSION_IS_AHEAD:  # 版本号比服务器高，不过一般应该不会吧
            self.mainwindow.show_tip(
                "?",
                "你对版本号文件做什么了。。。",
                duration=5000,
                icon=InfoBarIcon.ERROR,
            )

    def detect_newday(self):
        "检测是否是新的一天"
        if time.localtime(
            self.mainwindow.last_start_time
        ).tm_wday != time.localtime().tm_wday or (  # 不是一周的同一天
            time.time() - self.mainwindow.last_start_time
            >= 86400  # 是一周的同一天旦超过一天
            and time.localtime(self.mainwindow.last_start_time).tm_wday
            == time.localtime().tm_wday
        ):

            # 没好的一天又开始力
            self.mainwindow.show_tip(
                "日期刷新",
                time.strftime(
                    "%Y年%m月%d日过去了，",
                    time.localtime(self.mainwindow.last_start_time),
                )
                + "新的一天开始了！",
                self.mainwindow,
                duration=6000,
                sound="audio/sounds/orb.ogg",
                icon=InfoBarIcon.INFORMATION,
            )

            self.mainwindow.day_end(
                time.localtime(self.mainwindow.last_start_time).tm_wday,
                self.mainwindow.last_start_time,
                time.time() - self.mainwindow.last_start_time <= 86400,
            )
            self.mainwindow.last_start_time += min(
                time.time() - self.mainwindow.last_start_time, 86400
            )

        else:
            self.mainwindow.last_start_time += min(
                time.time() - self.mainwindow.last_start_time, 86400
            )

    def run(self):
        "线程运行"
        Base.log("I", "更新线程开始运行", "UpdateThread.run")
        self.lastest_score: Dict[int, float] = dict(
            [(stu.num, 0.0) for stu in self.mainwindow.target_class.students.values()]
        )

        self.lastest_grp_score: Dict[str, float] = dict(
            [(grp.key, 0.0) for grp in self.mainwindow.target_class.groups.values()]
        )

        while self.mainwindow.is_running:
            try:
                self.detect_newday()
                try:
                    self.update_stu_btns()
                    self.update_grp_btns()
                except IndexError as e:
                    Base.log_exc_short(
                        "疑似添加/减少学生，正在重新加载: ", "UpdateThread.run", "W", e
                    )
                    self.mainwindow.grid_buttons()
                if self.first_loop:
                    Thread(target=self.detect_new_version).start()
                    Thread(target=self.detect_update).start()
                    self.first_loop = False
                self.mainwindow.anim_group_state_changed.emit(ClassWindow.AnimationGroupStatement.START)
                time.sleep(0.5)
                self.mainwindow.anim_group_state_changed.emit(ClassWindow.AnimationGroupStatement.CREATE_NEW)


            except BaseException as unused:  # pylint: disable=broad-exception-caught
                Base.log_exc("更新窗口事件时发生错误", "UpdateThread.run")


class TipViewerWindow(NoticeViewer.Ui_widget, MyWidget):
    "提示详细信息窗口"

    def __init__(
        self, obj: Optional[SideNotice] = None, parent: Optional[QWidget] = None
    ):
        super(NoticeViewer.Ui_widget, self).__init__(parent)
        self.setupUi(self)
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


class RecoveryPoint:
    """还原点"""

    def __init__(
        self,
        path: str,
        mode: Literal["all", "only_data"],
        stat: Literal["active", "unknown", "damaged", "missed"],
    ):
        """
        初始化

        :param path: 路径
        :param mode: 模式
        :param stat: 状态
        """
        self.path = path
        self.mode = mode
        self.time = time.time()
        self.stat = stat

    def get_data_path(self, current_user: str):
        """
        获取数据路径

        :param current_user: 当前用户
        """
        return os.path.join(self.path, "chunks", current_user)

    def exists(self):
        """检查换还原点是否存在"""
        return os.path.exists(self.path)

    def load_onlydata_and_set(self, current_user="测试用户1"):
        """
        加载数据并设置

        :param current_user: 当前用户
        """
        Base.log("I", "正在从还原点恢复数据", "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点路径：" + self.path, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点模式：" + self.mode, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点时间：" + str(self.time), "RecoveryPoint.load_onlydata")
        Base.log("I", "当前用户：" + current_user, "RecoveryPoint.load_onlydata")
        while widget.auto_saving:
            do_nothing()
        self.load_onlydata(widget.current_user)
        widget.stop()
        rmtree(widget.save_path)

        def _copy():
            for root, dirs, files in os.walk(self.get_data_path(widget.current_user)):
                for file in files:
                    os.makedirs(
                        os.path.join(
                            widget.save_path,
                            os.path.relpath(
                                root, self.get_data_path(widget.current_user)
                            ),
                        ),
                        exist_ok=True,
                    )
                    shutil_copy(
                        os.path.join(root, file),
                        os.path.join(
                            widget.save_path,
                            os.path.relpath(
                                root, self.get_data_path(widget.current_user)
                            ),
                            file,
                        ),
                    )

        _copy()
        Base.log(
            "I",
            f"将文件从{self.get_data_path(widget.current_user)}"
            f"复制到{widget.save_path}...",
            "RecoveryPoint.load_onlydata_and_set",
        )
        QMessageBox.information(widget, "恢复成功", "恢复成功，请重新启动程序")

        while widget.auto_saving:
            do_nothing()
        _copy()  # 我就不信保存两次还能失败
        pid = os.getpid()  # 获取当前进程的PID
        os.kill(pid, signal.SIGTERM)  # 发送终止信号给当前进程（什么抽象关闭方法）

    def load_onlydata(self, current_user="测试用户1"):
        """只加载数据"""
        Base.log("I", "正在从还原点加载数据", "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点路径：" + self.path, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点模式：" + self.mode, "RecoveryPoint.load_onlydata")
        Base.log("I", "还原点时间：" + str(self.time), "RecoveryPoint.load_onlydata")
        Base.log("I", "当前用户：" + current_user, "RecoveryPoint.load_onlydata")
        return widget.load_data(self.get_data_path(current_user), strict=True)


class StudentWidget(StudentWindow.Ui_Form, MyWidget):
    """学生信息窗口实例化"""

    def __init__(
        self,
        mainwindow: ClassWindow = None,
        master_widget: Optional[WidgetType] = None,
        student: Student = None,
        readonly: bool = False,
    ):
        """
        初始化

        :param mainwindow: 程序的主窗口，方便传参
        :param master_widget: 这个学生窗口的父窗口
        :param student: 这个学生窗口对应的学生
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.student = student
        self.readonly = readonly
        self.show()
        self.mainLayout = QVBoxLayout()
        self.setWindowTitle("学生信息 - " + str(student.name))
        self.setLayout(self.mainLayout)
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(100)
        self.pushButton_3.clicked.connect(self.select_and_send)
        self.pushButton.clicked.connect(self.load_history)
        self.pushButton_2.clicked.connect(self.load_achievement)
        self.history_data: List[Tuple[str, Callable]] = []
        self.achievement_data: List[Tuple[str, Callable]] = []
        self.history_list_window: Optional[ListView] = None
        "历史记录详情窗口"
        self.achievement_list_window: Optional[ListView] = None
        "成就详情窗口"
        self.history_detail_window: Optional[HistoryWidget] = None
        "历史记录详情窗口"
        self.achievement_detail_window: Optional[AchievementWidget] = None
        "成就详情窗口"
        self.template_selector: Optional[SelectTemplateWidget] = None
        "模板选择窗口"
        if readonly:
            self.pushButton_3.setEnabled(False)

    def show(self, readonly=False):
        self.readonly = readonly
        Base.log(
            "I",
            f"学生信息窗口打开，目标学生：{repr(self.student)}，"
            f"只读模式：{self.readonly}",
            "StudentWidget",
        )
        self.setWindowTitle("学生信息 - " + str(self.student.name))
        super().show()
        self.pushButton_3.setDisabled(readonly)

    def update(self):
        self.label_11.setText(str(self.student.name))
        self.label_6.setText(str(self.student.num))
        self.label_12.setText(str(self.student.score))
        self.label_13.setText(
            str(self.mainwindow.classes[self.student.belongs_to].name)
        )
        self.label_8.setText(
            str(round(self.student.highest_score, 1))
            + "/"
            + str(round(self.student.lowest_score, 1))
        )
        self.label_7.setText(str(self.student.total_score))
        for i, s in self.mainwindow.class_obs.rank_non_dumplicate:
            if s.num == self.student.num and s.belongs_to == self.student.belongs_to:
                self.label_16.setText(str(i))
                break

    def send(self, result: Tuple[str, str, str, float]):
        "连接了SelectTemplateWidget.return_result的函数，用来发送点评"
        if not result[0]:
            Base.log("I", "未选择模板", "StudentWidget.send")
            return
        Base.log(
            "I",
            f"发送：{repr((result[0], self.student, result[1], result[2], result[3]))}",
            "StudentWidget.send",
        )
        self.mainwindow.send_modify(
            result[0], self.student, result[1], result[2], result[3]
        )

    @Slot()
    def load_history(self):
        "加载这个学生的历史记录"
        Base.log(
            "I",
            f"加载历史记录，只读模式：{self.readonly}",
            "StudentWidget.load_history",
        )
        index = 0
        for key in reversed(self.student.history):
            history = self.student.history[key]
            if history.executed:
                try:
                    text = f"{history.title} {history.execute_time.rsplit('.', 1)[0]} {history.mod:+.1f}"
                except (
                    AttributeError,
                    TypeError,
                ) as unused:  # pylint: disable=unused-variable
                    try:
                        text = f"{history.title} {history.create_time.rsplit('.', 1)[0]} {history.mod:+.1f}"
                    except (AttributeError, TypeError) as unused_2:  # NOSONAR
                        text = f"{history.title} <时间信息丢失>   {history.mod:+.1f}"

                def _callable(history=history, index=index, readonly=self.readonly):
                    return self.history_detail(history, index, readonly)

                flash_args = (
                    (
                        QColor(202, 255, 222)
                        if history.mod > 0
                        else (
                            QColor(255, 202, 202)
                            if history.mod < 0
                            else QColor(201, 232, 255)
                        )
                    ),
                    (
                        QColor(232, 255, 232)
                        if history.mod > 0
                        else (
                            QColor(255, 232, 232)
                            if history.mod < 0
                            else QColor(233, 244, 255)
                        )
                    ),
                )

                self.history_data.append((text, _callable, flash_args))

                index += 1
        self.history_list_window = ListView(
            self.mainwindow,
            self,
            f"历史记录 - {self.student.name}",
            self.history_data,
            {"readonly": self.readonly},
            [("查看分数折线图", self.show_score_graph)],
            allow_pre_action=True,
        )
        self.history_list_window.show()

    class ScoreGraphWindow(QMainWindow):

        def __init__(self, parent: MyWidget, student: Student):
            super().__init__(parent)
            self.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.graphWidget = pg.PlotWidget()
            self.setCentralWidget(self.graphWidget)
            self.master = parent
            self.history_data = student.history
            self.student = student
            self.setWindowTitle(f"分数折线图 - {self.student.name}")
            self.resize(600, 400)
            self.graphWidget.setBackground("w")
            self.graphWidget.setTitle(f"分数折线图 - {self.student.name}")
            self.graphWidget.setLabel("left", "分数")
            self.graphWidget.setLabel("bottom", "次数")
            self.graphWidget.showGrid(x=True, y=True)
            self.graphWidget.addLegend()
            self._x = [0]
            self._y = [0]
            score = Student.score_dtype(0)
            for index, history in enumerate(self.history_data.values(), start=1):
                if history.executed:
                    score += history.mod
                    self._x.append(index)
                    self._y.append(float(score))
            self.graphWidget.plot(self._x, self._y, pen=(255, 0, 0), name="分数")

        def show(self):
            self.move(self.master.geometry().center() - self.geometry().center())
            super().show()

    def show_score_graph(self):
        Base.log("I", "显示分数折线图", "StudentWidget.show_score_graph")
        if not len([m for m in self.student.history.values() if m.executed]):
            Base.log("I", "没有历史记录", "StudentWidget.show_score_graph")
            self.mainwindow.information("?", "可是都没有记录你点进来干嘛")
            return
        window = StudentWidget.ScoreGraphWindow(self.history_list_window, self.student)
        window.show()

    @Slot()
    def load_achievement(self):
        "加载这个学生的成就"
        index = 0
        Base.log("I", "加载成就", "StudentWidget.load_achievement")
        for key in reversed(self.student.achievements):
            achievement = self.student.achievements[key]
            self.achievement_data.append(
                (
                    achievement.temp.name,
                    lambda achievement=achievement, index=index: self.achievement_detail(
                        achievement, index
                    ),
                )
            )
            index += 1
        self.achievement_list_window = ListView(
            self.mainwindow, self, f"成就 - {self.student.name}", self.achievement_data
        )
        self.achievement_list_window.show()

    def history_detail(self, history: ScoreModification, index: int, readonly=False):
        """查看历史纪录的详细信息

        :param history: 记录
        :param index: 在listView中的索引"""
        Base.log(
            "I",
            f"选中历史记录： {history}，只读模式：{readonly}",
            "StudentWidget.history_detail",
        )
        self.history_detail_window = HistoryWidget(
            self.mainwindow,
            self.history_list_window,
            history,
            self.history_list_window,
            index,
            readonly,
        )
        self.history_detail_window.show(readonly)

    def achievement_detail(self, achievement: ScoreModification, index: int):
        """查看成就的详细信息

        :param achievement: 记录
        :param index: 在listView中的索引"""
        Base.log("I", f"选中成就： {achievement}", "StudentWidget.achievement_detail")
        self.achievement_detail_window = AchievementWidget(
            self.achievement_list_window, self.mainwindow, achievement
        )
        self.achievement_detail_window.show()

    @Slot()
    def select_and_send(self):
        "选择模板并发送点评"
        self.template_selector = SelectTemplateWidget(self.mainwindow, self)
        self.template_selector.show()
        self.template_selector.return_result.connect(self.send)
        self.template_selector.select()

    def set_student(self, student: Student):
        """设置学生信息

        :param student: 学生对象"""
        if self.isEnabled():
            self.student = student
        else:
            Base.log(
                "I", "学生信息窗口未启用，无法设置学生", "StudentWidget.set_student"
            )

    def close(self):
        """关闭"""
        self.is_running = False
        super().close()


class GroupWidget(GroupWindow.Ui_Form, MyWidget):
    "小组窗口"

    student_list_update = Signal()
    "学生列表更新信号"

    def __init__(
        self,
        mainwindow: ClassWindow = None,
        master_widget: Optional[WidgetType] = None,
        group: Group = None,
        readonly: bool = False,
    ):
        """
        初始化

        :param mainwindow: 程序的主窗口，方便传参
        :param master_widget: 这个窗口的父窗口
        :param group: 这个学生窗口对应的小组
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.group = group
        self.show()
        self.mainLayout = QVBoxLayout()
        self.setWindowTitle("小组信息 - " + str(group.name))
        self.setLayout(self.mainLayout)
        self.first_load = True
        self.update_timer = QTimer()
        self.last_score = {}
        self.update_timer.timeout.connect(self.update_label)
        self.update_timer.start(100)
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.listWidget_order = []
        for member in self.group.members:
            self.listWidget.addItem(
                QListWidgetItem(f"{member.num}号 {member.name} {member.score}分")
            )
            self.listWidget_order.append(member)
        self.listWidget.clicked.connect(self.student_clicked)
        self.textBrowser.setText(
            str(self.group.further_desc)
        )  # 不能在别的线程设置，我也不知道为什么
        self.update_stu_list()
        self.pushButton.clicked.connect(
            lambda: self.mainwindow.scoring_select(students=self.group.members)
        )
        self.stu_list_update_timer = QTimer()
        self.student_list_update.connect(self.update_stu_list)
        self.stu_list_update_timer.timeout.connect(self.student_list_update.emit)
        self.stu_list_update_timer.start(1000)
        self.readonly = readonly
        self.pushButton.setDisabled(readonly)
        self.pushButton_2.setDisabled(readonly)
        self.pushButton_2.clicked.connect(
            lambda: self.mainwindow.send_to_students(self.group.members)
        )
        self.last_value: List[int] = []

    def show(self, readonly=False):
        Base.log("I", f"小组信息窗口显示：选中{self.group}", "GroupWindowInstance")
        super().show()
        self.pushButton.setDisabled(readonly)
        self.pushButton_2.setDisabled(readonly)
        self.readonly = readonly
        self.first_load = True

    def student_clicked(self, index: QModelIndex):
        """点击列表项操作
        :index: 传过来的索引，不用管（是自动的）"""
        student = self.listWidget_order[index.row()]
        Base.log(
            "I",
            f"点击列表项:{index.row()}, {repr(student)}",
            "MainWindow.click_opreation",
        )
        if hasattr(self, "student_window"):
            self.student_window.destroy()  # pylint: disable=access-member-before-definition
        self.student_window = StudentWidget(
            self.mainwindow, self, student
        )  # pylint: disable=attribute-defined-outside-init
        self.student_window.show(self.readonly)

    def update_label(self):
        self.label_6.setText(str(self.group.name))
        self.label_9.setText(str(len(self.group.members)))
        self.label_8.setText(
            str(self.group.total_score)
            + f"（均分{self.group.average_score}，去最低分{self.group.average_score_without_lowest}）"
        )
        self.label_7.setText(str(self.mainwindow.classes[self.group.belongs_to].name))
        self.label_11.setText(str(self.group.leader.name))

    def update_stu_list(self):
        if self.last_score == {}:
            for member in self.group.members:
                self.last_score[member] = member.score
            self.last_score["total"] = self.group.total_score
        self.listWidget.clear()
        self.listWidget_order = []
        end_value = []
        for member in sorted(self.group.members, key=lambda s: s.score, reverse=True):
            item = ProgressAnimatedListWidgetItem(
                f"{member.num}号 {member.name} {member.score}分"
            )
            self.listWidget.addItem(item)
            widget_item = item.getWidget()
            self.listWidget.setItemWidget(item, widget_item)
            try:
                start = self.last_value.pop(0)
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                start = min(
                    abs(
                        self.last_score[member]
                        / (
                            max(
                                self.last_score["total"],
                                *[abs(s.score) for s in self.group.members]
                            )
                            if (
                                self.last_score["total"] != 0
                                and max([abs(s.score) for s in self.group.members]) != 0
                            )
                            else max(
                                *[abs(s.score) for s in self.group.members], 0.1
                            )
                        )
                    ),
                    1
                )
            end = min(
                abs(
                    member.score
                    / (
                        max(
                            self.group.total_score,
                            *[abs(s.score) for s in self.group.members],
                        )
                        if (
                            self.group.total_score != 0
                            and max([abs(s.score) for s in self.group.members]) != 0
                        )
                        else max(*[abs(s.score) for s in self.group.members], 0.1)
                    )
                ),
                1
            )
            color = (
                QColor(222, 252, 222) if member.score >= 0 else QColor(252, 222, 222)
            )
            item.startProgressAnimation(
                start, end, color, duration=1000, curve=QEasingCurve.Type.OutCubic
            )
            self.listWidget_order.append(member)
            end_value.append(end)
        for member in self.group.members:
            self.last_score[member] = member.score
        self.last_value = end_value.copy()
        self.first_load = False
        self.last_score["total"] = self.group.total_score

    def closeEvent(self, event: QCloseEvent):
        super().closeEvent(event)


class SelectTemplateWidget(MyWidget, SelectTemplateWindow.Ui_Form):
    "选择模板窗口"

    return_result = Signal(tuple)
    "返回信号：(模板key，修改标题，修改描述，修改分数) (Tuple[str, str, str, float])"

    def __init__(
        self, mainwindow: ClassWindow = None, master_widget: Optional[WidgetType] = None
    ):
        """
        初始化

        :mainwindow: 主窗口
        :master_widget: 父窗口
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.setWindowTitle("选择模板")
        index = 0
        self.index_map = {}
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.show()
        self.comboBox.clear()
        for key in self.mainwindow.modify_templates:
            template = self.mainwindow.modify_templates[key]
            if template.is_visible:
                self.comboBox.addItem(template.title)
                self.index_map[index] = key
                index += 1
        self.select_finished = False
        self.return_title = None
        self.return_desc = None
        self.return_mod = None
        self.selected = None
        self.buttonBox.accepted.connect(self.finish)
        self.buttonBox.rejected.connect(self.close)
        self.comboBox.currentIndexChanged.connect(self.update_edit)
        self.result: Optional[Tuple[str, str, str, float]] = None

    def update_edit(self):
        index = self.comboBox.currentIndex()
        try:
            template = self.mainwindow.modify_templates[self.index_map[index]]
            self.lineEdit.setText(template.title)
            self.lineEdit_3.setText(template.desc)
            self.doubleSpinBox.setValue(template.mod)

        except KeyError as unused:
            pass

    def select(self):
        index = 0
        self.comboBox.clear()
        self.index_map = {}
        for key in self.mainwindow.modify_templates:
            template = self.mainwindow.modify_templates[key]
            if template.is_visible:
                self.comboBox.addItem(template.title)
                self.index_map[index] = key
                index += 1
        self.update_edit()

    def close(self):
        Base.log(
            "I",
            f"选择结果：{repr((self.selected, self.return_title, self.return_desc, self.return_mod))}",
            "SelectTemplateWidget",
        )
        self.select_finished = True
        Base.log("I", "选择模板窗口关闭", "SelectTemplateWidget")
        super(MyWidget, self).close()

    def closeEvent(self, event: QEvent):
        self.result = ()
        Base.log("I", "选择模板窗口关闭（通过关闭事件）", "SelectTemplateWidget")
        super().closeEvent(event)

    @Slot()
    def cancel(self):
        Base.log("I", "选择已取消", "SelectTemplateWidget")
        self.return_title = None
        self.return_desc = None
        self.return_mod = None
        self.select_finished = True
        self.close()

    def finish(
        self,
    ) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[float]]:
        self.selected_index = self.comboBox.currentIndex()
        self.selected = self.mainwindow.modify_templates[
            self.index_map[self.selected_index]
        ]
        if self.lineEdit.text() != self.selected.title:
            self.return_title = self.lineEdit.text()
        if self.lineEdit_3.text() != self.selected.desc:
            self.return_desc = self.lineEdit_3.text()
        if self.doubleSpinBox.value() != self.selected.mod:
            self.return_mod = self.doubleSpinBox.value()
        if not self.select_finished:  # 防止重复调用
            self.select_finished = True
            self.return_result.emit(
                (
                    self.selected.key,
                    self.return_title,
                    self.return_desc,
                    self.return_mod,
                )
            )
            self.result = (
                self.selected.key,
                self.return_title,
                self.return_desc,
                self.return_mod,
            )
        self.select_finished = True
        self.close()

    def exec(self) -> Optional[Tuple[str, str, str, float]]:
        """阻塞调用，返回 (key, title, desc, mod)"""
        self.show()
        while self.result is None:
            do_nothing()
        return self.result


class ListView(MyWidget):  # pylint: disable=function-redefined
    "列表视图，全程序用的最多的窗口"

    item_update = Signal(QListWidgetItem, QColor)

    command_update = Signal(list)

    def setupui(self, form: MyWidget):
        "设置UI"
        if not form.objectName():
            form.setObjectName("Form")
        form.resize(437, 551)
        self.listWidget = QListWidget(form)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setGeometry(QRect(0, 0, 341, 551))
        self.verticalLayoutWidget = QWidget(form)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(340, -1, 101, 551))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_2 = QPushButton(self.verticalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.verticalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QPushButton(self.verticalLayoutWidget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.verticalLayout.addWidget(self.pushButton_3)
        self.retranslateUi(form)
        QMetaObject.connectSlotsByName(form)

    def retranslateUi(self, form: MyWidget):
        "设置UI文本"
        form.setWindowTitle("\u5217\u8868")
        self.pushButton_2.setText("\u56de\u5230\u9876\u90e8")
        self.pushButton_3.setText("\u6eda\u52a8\u5230\u5e95\u90e8")

    def __init__(
        self,
        mainwindow: ClassWindow = None,
        master_widget: Optional[WidgetType] = None,
        title: str = "列表",
        data: List[
            Union[
                Tuple[str, Callable],
                Tuple[str, Callable, Optional[Tuple[QColor, QColor, int, int]]],
            ]
        ] = None,
        args: Any = None,
        commands: List[Tuple[str, Callable]] = None,
        allow_pre_action: bool = False,
        select_once_then_exit: bool = False,
    ):
        """
        初始化窗口

        :param mainwindow: 主窗口
        :param master_widget: 父窗口
        :param title: 窗口标题
        :param data: 数据，格式为 [(文本, 回调函数, 可选(起始颜色, 结束颜色, 总渐变步数, 每次变化间隔))]
        :param args: 随便传点什么参数用来存东西
        :param commands: 命令，格式为 [(文本, 回调函数)]
        :param allow_pre_action: 是否允许在动画完成前执行回调函数
        :param select_once_then_exit: 是否选中一次后退出
        """
        if data is None:
            data = [("空", lambda: None)]
        if commands is None:
            commands = []
        super().__init__(master=mainwindow)
        self.setupui(self)
        self.orig_height = self.height()
        self.data = data
        self.args = args
        self.title = title
        self.allow_pre_action = allow_pre_action
        self.setWindowTitle(title)
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.listWidget.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )  # 双击编辑有点逆天（这里禁了）
        self.listWidget.doubleClicked.connect(self.itemClicked)
        self.command_update.connect(self.setCommands)
        self.pushButton_2.clicked.connect(lambda: self.listWidget.scrollToTop())
        self.pushButton_3.clicked.connect(lambda: self.listWidget.scrollToBottom())
        self.item_update.connect(self.update_item_color)
        self.commands = commands
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.setSpacing(0)
        self.btn_list: List[QPushButton] = []
        self.cmd_list: List[Callable] = []
        self.ready = False
        self.setting_command = False
        self.setCommands(commands, force=True)
        self.commands = commands
        self.select_once_then_exit = select_once_then_exit
        self.widget_items: List[QListWidgetItem] = []

    @Slot()
    def setCommands(self, commands: List[Tuple[str, Callable]] = None, *, force=False):
        while self.setting_command and not force:
            """"""
        self.commands = commands
        self.setting_command = True
        commands = self.commands
        for btn in self.btn_list:
            btn.deleteLater()
        self.btn_list = []
        if commands is None:
            return
        for string, _callable in commands:
            btn = QPushButton(string)
            self.btn_list.append(btn)
            self.verticalLayout.addWidget(btn)
            self.cmd_list.append(_callable)
            btn.clicked.connect(
                lambda *, string=string, _callable=_callable: (
                    (
                        lambda string=string, _callable=_callable: (
                            Base.log(
                                "I",
                                f"执行命令：{string}，{_callable}",
                                "ListView.setCommands",
                            ),
                            _callable(),
                        )
                    )()
                    if self.ready or self.allow_pre_action
                    else (
                        lambda: Base.log(
                            "W",
                            f"正在初始化，忽略操作 ({string})",
                            "ListView.setCommands",
                        )
                    )()
                )
            )
        self.verticalLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.verticalLayout.update()
        self.setting_command = False

    @Slot(QListWidgetItem, QColor)
    def update_item_color(self, item: QListWidgetItem, color: QColor):
        try:
            if item is None:
                return
            item.setBackground(QBrush(color))

        except BaseException as unused:  # pylint: disable=broad-exception-caught
            pass

    def show(self):
        super().show()
        self.ready = False
        if (
            self.mainwindow.animation_speed <= 114514
        ):  # 114514 is a magic number :)   （AI说的不关我事）
            # 其实是因为float("inf")不好判等，所以用了这个数
            self.showStartAnimation()
            while True:
                try:
                    if (
                        self.startanimation_1.state()
                        != QAbstractAnimation.State.Running
                    ):
                        break

                except (
                    BaseException
                ) as unused:  # pylint: disable=broad-exception-caught
                    pass
                self.update()
                do_nothing()
        else:
            self.ready = True
        while (
            hasattr(self, "startanimation_2")
            and self.startanimation_2.state() != QAbstractAnimation.State.Running
        ):
            self.update()
            do_nothing()
        self.str_list = [item[0] for item in self.data]
        self.widget_items = [QListWidgetItem(string) for string in self.str_list]
        self.listWidget.clear()
        Thread(target=self.init_items, name="ListView.init_items").start()

    def init_items(self):
        Base.log("D", f"开始初始化项目，数量：{len(self.data)}", "ListView.init_items")
        self.anim_result = [False] * len(self.data)
        index = 0
        default_color_start = QColor(232, 255, 244)
        default_color_end = QColor(255, 255, 255)
        default_step = int(25 / self.mainwindow.animation_speed)
        default_interval = 10
        try:
            for item in self.data:
                if len(item) == 2 or (len(item) == 3 and item[2] is None):
                    self.data[index] = (
                        item[0],
                        item[1],
                        (
                            default_color_start,
                            default_color_end,
                            default_step,
                            default_interval,
                        ),
                    )
                elif len(item) == 3:
                    if len(item[2]) == 2:
                        self.data[index] = (
                            item[0],
                            item[1],
                            (item[2][0], item[2][1], default_step, default_interval),
                        )
                    elif len(item[2]) == 3:
                        self.data[index] = (
                            item[0],
                            item[1],
                            (item[2][0], item[2][1], item[2][2], default_interval),
                        )
                index += 1
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            Base.log_exc("初始化项目时发生错误", "ListView.init_items")
        index = 0
        items = self.widget_items
        try:
            for string, _callable, flash_args in self.data:
                widget_item = items[index]
                self.listWidget.addItem(widget_item)
                index += 1
                if self.mainwindow.animation_speed <= 114514:
                    Thread(
                        target=lambda widget_item=widget_item, flash=flash_args, index=index: (
                            self.insert_flash(
                                widget_item, flash[0], flash[1], flash[2], flash[3]
                            ),
                            self._set_anim_finished(index - 1),
                        ),
                        name="insert_flash",
                    ).start()

                    time.sleep(0.01 / self.mainwindow.animation_speed)
                else:
                    widget_item.setBackground(QBrush(flash_args[1]))
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            Base.log_exc("初始化项目时发生错误", "ListView.init_items")

        Base.log("D", "等待动画结束", "ListView.init_items")
        while not (all(self.anim_result)):
            do_nothing()
        Base.log(
            "D",
            f"初始化项目完成，len(anim_result) = {len(self.anim_result)}",
            "ListView.init_items",
        )
        self.ready = True

    def _set_anim_finished(self, index: int):
        try:
            self.anim_result[index] = True
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            pass

    def insert_flash(
        self,
        item: QListWidgetItem,
        from_color: QColor,
        to_color: QColor,
        step: int = 45,
        interval: int = 1,
    ):
        for r, g, b in list(
            zip(
                steprange(from_color.red(), to_color.red(), step),
                steprange(from_color.green(), to_color.green(), step),
                steprange(from_color.blue(), to_color.blue(), step),
            )
        ):
            try:

                self.item_update.emit(item, QColor(r, g, b))
                if interval:
                    time.sleep((interval / 1000))
                if not self.isVisible():
                    return

            except BaseException as unused:  # pylint: disable=broad-exception-caught
                pass

    def create_animation(
        self,
        property_name,
        duration,
        start_value,
        end_value,
        easing_curve=QEasingCurve.Type.OutCubic,
    ):
        """创建通用属性动画

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
            duration / widget.animation_speed
            if widget.animation_speed > 0
            else duration
        )
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        return animation

    def showStartAnimation(self):
        Base.log("D", "开始启动动画（阶段1）", "ListView.showStartAnimation")

        # 计算动画终点和起点
        endpoint = (
            self.master.geometry().topLeft()
            + QPoint(
                self.master.geometry().width() / 2, self.master.geometry().height() / 2
            )
            - QPoint(self.geometry().width() / 2, self.orig_height / 2)
        )

        startpoint = QPoint(
            endpoint.x(),
            QGuiApplication.primaryScreen().availableGeometry().height()
            + QGuiApplication.primaryScreen().availableGeometry().top(),
        )

        # 使用通用动画创建方法
        self.startanimation_1 = self.create_animation(b"pos", 400, startpoint, endpoint)

        self.setGeometry(self.x(), self.y(), self.width(), 1)
        self.startanimation_1.start()

        # 设置定时器启动第二阶段动画
        self.timer = QTimer()
        self.timer.timeout.connect(self.showStartAnimation2)
        self.timer.start(400 / widget.animation_speed)

    @Slot()
    def showStartAnimation2(self):
        Base.log("D", "开始启动动画（阶段2）", "ListView.showStartAnimation")
        self.timer.stop()

        # 获取当前尺寸信息
        width, height = self.width(), self.orig_height

        # 使用通用动画创建方法
        self.startanimation_2 = self.create_animation(
            b"size", 400, QSize(width, 1), QSize(width, height)
        )
        self.startanimation_2.start()

    def addData(self, item: Tuple[str, Callable]):
        self.data.append(item)
        self.str_list.append(item[0])
        self.listWidget.addItem(QListWidgetItem(item[0]))

    def addItem(self, item: QListWidgetItem):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.addItem")
            return
        self.listWidget.addItem(item)

    def setData(self, data: List[Tuple[str, Callable]]):
        self.data = data
        self.str_list = [item[0] for item in data]
        self.listWidget.clear()
        for item in self.str_list:
            self.listWidget.addItem(QListWidgetItem(item))

    def setText(self, index: int, text: str):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.setText")
            return
        self.str_list[index] = text
        item = self.listWidget.item(index)
        item.setText(text)

    def getText(self, index: int):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.getText")
            return
        return self.str_list[index]

    def getItem(self, index: int) -> QListWidgetItem:
        return self.listWidget.item(index)

    def getCallable(self, index: int):
        return self.data[index][1]

    def setCallable(self, index: int, func: Callable):
        self.data[index] = (self.str_list[index], func)

    def delete(self, index: int) -> QListWidgetItem:
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.delete")
            return
        self.str_list.pop(index)
        item = self.listWidget.takeItem(index)
        self.data.pop(index)
        return item

    def insert(self, index, data: Tuple[str, Callable]):
        if not self.ready:
            Base.log("E", "ListView未准备好", "ListView.insert")
            return
        self.str_list.insert(index, data[0])
        self.listWidget.insertItem(index, QListWidgetItem(data[0]))
        self.listWidget.item(index).setText(data[0])
        self.data.insert(index, data)

    def length(self):
        return len(self.str_list)

    @Slot(QModelIndex)
    def itemClicked(self, qModelIndex: QModelIndex):
        # 弹出消息框
        Base.log(
            "I",
            f"点击了{repr(self.str_list[qModelIndex.row()])}, 调用函数{repr(self.data[qModelIndex.row()][1])}",
            "ListView",
        )
        self.data[qModelIndex.row()][1]()
        if self.select_once_then_exit:
            self.close()

    def closeEvent(self, event: QEvent):
        Base.log("I", "ListView窗口关闭（通过关闭事件）", "ListView")
        super().closeEvent(event)


class HistoryWidget(MyWidget, ModifyHistoryWindow.Ui_Form):
    """历史记录窗口"""

    def __init__(
        self,
        mainwindow: ClassWindow = None,
        master_widget: Optional[WidgetType] = None,
        history: ScoreModification = None,
        listview_widget: ListView = None,
        listview_index: int = None,
        readonly: bool = False,
    ):
        """
        初始化一个分数修改历史记录窗口

        :param mainwindow: 主窗口
        :param master_widget: 父窗口
        :param history: 分数修改历史记录
        :param listview_widget: 所属的ListView
        :param listview_index: 在ListView中的索引
        :param readonly: 是否只读
        """

        super().__init__(master=mainwindow)
        self.setupUi(self)

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.history = history
        self.listview_index = listview_index
        self.listview_widget = listview_widget
        self.readonly = readonly or (not history.executed)
        self.setWindowTitle(
            f"历史记录 - {self.history.target.name} {self.history.title}"
        )
        self.label_11.setText(str(self.history.title))
        self.label_6.setText(str(self.history.desc))
        self.label_12.setText(str(self.history.mod))
        self.label_13.setText(
            str(self.history.target.name + f" ({self.history.target.num})")
        )
        self.label_8.setText(str(self.history.create_time))
        self.label_7.setText(
            (
                ("已执行（" + str(self.history.execute_time) + "）")
                if self.history.executed
                else "未执行"
            )
        )
        self.pushButton_3.clicked.connect(self.retract)
        self.update_status()

    def update_status(self):
        if not self.history.executed:
            self.pushButton_3.setEnabled(False)
            self.label_15.setText("无法撤回（未执行）")
        elif self.readonly:
            self.pushButton_3.setEnabled(False)
            self.label_15.setText("无法撤回（只读）")
        elif (
            self.history
            not in self.mainwindow.classes[self.history.target.belongs_to]
            .students[self.history.target.num]
            .history.values()
        ):
            self.pushButton_3.setEnabled(False)
            self.label_15.setText("无法撤回（不在历史记录中）")
        else:
            self.pushButton_3.setEnabled(True)
            self.label_15.setText("")

    def retract(self):
        Base.log("I", f"撤销：{repr(self.history)}", "HistoryWidget")
        status, result = self.mainwindow.retract_modify(self.history)
        Base.log("I", f"撤销结果：{repr((status, result))}", "HistoryWidget")

        if status:
            if self.listview_index is not None and self.listview_widget:
                self.listview_widget.setText(
                    self.listview_index,
                    (self.listview_widget.getText(self.listview_index) or "")
                    + "（已撤回）",
                )
            self.listview_widget.getItem(self.listview_index).setBackground(
                QColor(202, 202, 202)
            )
        self.pushButton_3.setEnabled(False)
        self.closeEvent(QCloseEvent())
        self.destroy()

    def closeEvent(self, event):
        Base.log("I", "关闭历史记录窗口（通过closeEvent）", "HistoryWidget")
        super().closeEvent(event)

    def show(self, readonly: bool = False):
        Base.log("I", "显示历史记录窗口", "HistoryWidget")
        self.update_status()
        super().show()


class StudentSelectorWidget(MultiSelectWindow.Ui_Form, MyWidget):
    """多选学生窗口"""

    return_result = Signal(list)
    "返回结果信号"

    def __init__(
        self,
        mainwindow: ClassWindow = None,
        master: Optional[WidgetType] = None,
        target_students: List[Student] = None,
        default_selection: List[Student] = None,
        allow_none: bool = False,
        title: str = "选择学生",
    ):
        """
        学生选择器

        :param mainwindow: 主窗口
        :param master_widget: 父窗口
        :param target_students: 目标学生列表
        :param default_selection: 默认选择的学生
        :param allow_none: 是否允许选择空列表
        :param title: 窗口标题
        """
        super().__init__(master=mainwindow)
        if target_students is None:
            target_students = []
        self.setupUi(self)
        self.setWindowTitle("学生选择器")
        self.label.setText(title)
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainwindow = mainwindow
        self.master_widget = master
        self.target_students = target_students
        self.default_selection = (
            default_selection if default_selection is not None else []
        )
        self.mapping = {}
        self.allow_none = allow_none
        row = 0
        col = 0
        self.checkbuttons: Dict[int, QCheckBox] = {}
        self.select_result: Optional[List[Student]] = None
        for num, stu in [(stu.num, stu) for stu in target_students]:
            self.mapping[num] = stu
            checkbox = QCheckBox(f"{stu.num}号 " + stu.name + f"\n{stu.score}分")
            checkbox.setGeometry(QRect(0, 0, 60, 60))
            checkbox.setChecked(stu in self.default_selection)
            self.gridLayout.addWidget(checkbox, row, col)
            self.checkbuttons[num] = self.gridLayout.itemAtPosition(row, col).widget()
            col += 1
            if col > 9:
                col = 0
                row += 1
        self.gridLayout.setSpacing(10)
        self.pushButton.clicked.connect(self.commit)
        self.pushButton_2.clicked.connect(self.cancel)
        self.pushButton_3.clicked.connect(self.select_opposite)
        self.pushButton_4.clicked.connect(self.select_all)
        self.pushButton_5.clicked.connect(self.select_none)
        self.comboBox.clear()
        self.comboBox.addItems(
            [
                str(8),
                str(9),
                str(10),
                str(11),
                str(12),
            ]
        )
        self.comboBox.setCurrentIndex(2)
        self.comboBox.currentIndexChanged.connect(self.width_changed)

    def exec(self, allow_none: bool = False) -> List[Student]:
        Base.log("I", "多选窗口开始执行", "MultiSelectWidget")
        self.allow_none = allow_none
        self.show()
        while self.select_result is None:
            do_nothing()
        Base.log(
            "I",
            f"多选窗口执行结束，结果：{repr(self.select_result)}",
            "MultiSelectWidget",
        )
        return self.select_result

    @Slot()
    def width_changed(self):
        Base.log(
            "I",
            f"多选窗口宽度设置为：{self.comboBox.currentText()}",
            "MultiSelectWidget.width_changed",
        )
        for i in range(self.gridLayout.count()):
            if isinstance(self.gridLayout.itemAt(i).widget(), QCheckBox):
                self.gridLayout.itemAt(i).widget().deleteLater()
        row = 0
        col = 0
        for num, stu in [(stu.num, stu) for stu in self.target_students]:
            self.mapping[num] = stu
            checkbox = QCheckBox(f"{stu.num}号 " + stu.name + f"\n{stu.score}分")
            checkbox.setGeometry(QRect(0, 0, 60, 60))
            self.gridLayout.addWidget(checkbox, row, col)
            self.checkbuttons[num] = checkbox
            col += 1
            if col > self.comboBox.currentIndex() + 8 - 1:
                col = 0
                row += 1
        self.gridLayout.setSpacing(0)

    @Slot()
    def commit(self):
        if (
            not len(
                [
                    self.mapping[num]
                    for num, checkbutton in self.checkbuttons.items()
                    if checkbutton.isChecked()
                ]
            )
            and not self.allow_none
        ):
            Base.log("W", "提交多选窗口，未选择任何学生", "MultiSelectWidget.commit")
            QMessageBox.warning(self, "警告", "虽然但是，你真的不选点什么吗？")
            return
        Base.log(
            "I",
            f"提交多选窗口，结果：{repr([num for num, checkbutton in self.checkbuttons.items() if checkbutton.isChecked()])}",
            "MultiSelectWidget.commit",
        )
        self.return_result.emit(
            [
                self.mapping[num]
                for num, checkbutton in self.checkbuttons.items()
                if checkbutton.isChecked()
            ]
        )
        self.select_result = [
            self.mapping[num]
            for num, checkbutton in self.checkbuttons.items()
            if checkbutton.isChecked()
        ]
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def cancel(self):
        Base.log("I", "取消多选窗口", "MultiSelectWidget.cancel")
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def select_opposite(self):
        Base.log("I", "反选多选窗口", "MultiSelectWidget.select_opposite")
        for checkbutton in self.checkbuttons.values():
            checkbutton.setChecked(not checkbutton.isChecked())

    @Slot()
    def select_all(self):
        Base.log("I", "全选多选窗口", "MultiSelectWidget.select_all")
        for checkbutton in self.checkbuttons.values():
            checkbutton.setChecked(True)

    @Slot()
    def select_none(self):
        Base.log("I", "全不选多选窗口", "MultiSelectWidget.select_none")
        for checkbutton in self.checkbuttons.values():
            checkbutton.setChecked(False)

    def closeEvent(self, event):
        Base.log("I", "关闭多选窗口（通过closeEvent）", "MultiSelectWidget")
        super().closeEvent(event)


class NewTemplateWidget(NewTemplateWindow.Ui_Form, MyWidget):
    """创建新模板的窗口"""

    def __init__(
        self, mainwindow: ClassWindow = None, master_widget: Optional[WidgetType] = None
    ):
        """
        初始化

        :param mainwindow: 程序的主窗口，方便传参
        :param master_widget: 这个窗口的父窗口
        :param student: 这个学生窗口对应的学生
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.show()
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.cancel)
        self.lineEdit.setText("")
        self.lineEdit_3.setText("")
        self.setWindowTitle("创建新模板")

    @Slot()
    def commit(self):
        Base.log("I", "提交新模板窗口", "NewTemplateWidget.commit")
        if self.lineEdit.text() == "":
            Base.log("W", "提交新模板窗口时，模板名称为空", "NewTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板名称不能为空")
            return

        if self.lineEdit_3.text() == "":
            Base.log("W", "提交新模板窗口时，模板描述为空", "NewTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板描述不能为空")
            return

        self.mainwindow.add_template(
            "userset_" + str(Base.utc()),
            self.lineEdit.text(),
            self.doubleSpinBox.value(),
            self.lineEdit_3.text(),
            "为用户创建",
        )
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def cancel(self):
        Base.log("I", "取消创建新模板", "NewTemplateWidget.cancel")
        self.closeEvent(QCloseEvent())
        self.destroy()


class EditTemplateWidget(EditTemplateWindow.Ui_Form, MyWidget):
    """编辑模板的窗口"""

    def __init__(
        self,
        mainwindow: ClassWindow = None,
        master_widget: Optional[WidgetType] = None,
        template: ScoreModificationTemplate = None,
        in_listview: ListView = None,
        listview_index: int = None,
    ):
        """
        初始化

        :param mainwindow: 程序的主窗口，方便传参
        :param master_widget: 这个窗口的父窗口
        :param template: 要修改的模板
        :param in_listview: 模板所在的listview
        :param listview_index: 模板在listview中的位置
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.show()
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.template = template
        self.in_listview = in_listview
        self.listview_index = listview_index
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.cancel)
        self.pushButton_4.clicked.connect(self.delete)
        self.lineEdit.setText(self.template.title)
        self.lineEdit_3.setText(self.template.desc)
        self.doubleSpinBox.setValue(self.template.mod)
        self.label_7.setText(self.template.key)
        self.pushButton.clicked.connect(
            lambda: self.lineEdit.setText(self.template.title)
        )
        self.pushButton_3.clicked.connect(
            lambda: self.lineEdit_3.setText(self.template.desc)
        )
        self.pushButton_2.clicked.connect(
            lambda: self.doubleSpinBox.setValue(self.template.mod)
        )
        self.setWindowTitle(self.template.title)

    @Slot()
    def commit(self):
        Base.log("I", "提交修改模板窗口", "EditTemplateWidget.commit")
        if self.lineEdit.text() == "":
            Base.log("W", "提交新模板窗口时，模板名称为空", "EditTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板名称不能为空")
            return

        if self.lineEdit_3.text() == "":
            Base.log("W", "提交新模板窗口时，模板描述为空", "EditTemplateWidget.commit")
            QMessageBox.warning(self, "警告", "模板描述不能为空")
            return

        self.mainwindow.add_template(
            self.template.key,
            self.lineEdit.text(),
            self.doubleSpinBox.value(),
            self.lineEdit_3.text(),
            "修改原模版",
        )
        self.in_listview.setText(self.listview_index, self.lineEdit.text())
        self.closeEvent(QCloseEvent())
        self.destroy()

    @Slot()
    def cancel(self):
        Base.log("I", "取消创建新模板", "NewTemplateWidget.cancel")
        self.closeEvent(QCloseEvent())
        self.destroy()

    def delete(self):
        Base.log("I", "询问是否删除模板", "EditTemplateWidget.delete")
        if question_yes_no(self, "警告", "确认删除模板？", False, "warning"):
            Base.log("I", "删除模板", "EditTemplateWidget.delete")
            self.mainwindow.del_template(self.template.key, "模板编辑器中删除")
            self.in_listview.setText(self.listview_index, "(已删除)")
            self.in_listview.setCallable(self.listview_index, lambda: None)
            self.closeEvent(QCloseEvent())
            self.destroy()


class SettingWidget(SettingWindow.Ui_Form, MyWidget):
    """设置窗口"""

    def __init__(
        self, master_widget: Optional[WidgetType] = None, mainwindow: ClassWindow = None
    ):
        """初始化

        :param master_widget: 这个窗口的父窗口
        :param mainwindow: 程序的主窗口，方便传参"""
        super().__init__(master=master_widget)
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.setupUi(self)
        self.show()
        self.save.clicked.connect(self.accept_save)
        self.cancel.clicked.connect(self.cancel_save)
        self.reset.clicked.connect(self.reset_settings)
        self.setWindowTitle("设置")
        self.init()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(66)

    def reset_settings(self):
        if question_yes_no(self, "警告", "确认重置设置？", False, "warning"):
            Base.log("I", "重置设置", "SettingWidget.reset")
            self.mainwindow.reset_settings()
            self.init()

    def init(self):
        # 哇，是shitcode，我们有救了
        self.score_up_color_r.setValue(self.mainwindow.score_up_color_mixin_begin[0])
        self.score_up_color_g.setValue(self.mainwindow.score_up_color_mixin_begin[1])
        self.score_up_color_b.setValue(self.mainwindow.score_up_color_mixin_begin[2])

        self.score_down_color_r.setValue(
            self.mainwindow.score_down_color_mixin_begin[0]
        )
        self.score_down_color_g.setValue(
            self.mainwindow.score_down_color_mixin_begin[1]
        )
        self.score_down_color_b.setValue(
            self.mainwindow.score_down_color_mixin_begin[2]
        )

        self.score_up_color_end_r.setValue(self.mainwindow.score_up_color_mixin_end[0])
        self.score_up_color_end_g.setValue(self.mainwindow.score_up_color_mixin_end[1])
        self.score_up_color_end_b.setValue(self.mainwindow.score_up_color_mixin_end[2])

        self.score_down_color_end_r.setValue(
            self.mainwindow.score_down_color_mixin_end[0]
        )
        self.score_down_color_end_g.setValue(
            self.mainwindow.score_down_color_mixin_end[1]
        )
        self.score_down_color_end_b.setValue(
            self.mainwindow.score_down_color_mixin_end[2]
        )

        self.score_up_color_mixin_start.setValue(
            self.mainwindow.score_up_color_mixin_start
        )
        self.score_down_color_mixin_start.setValue(
            self.mainwindow.score_down_color_mixin_start
        )

        self.score_up_color_step.setValue(self.mainwindow.score_up_color_mixin_step)
        self.score_down_color_step.setValue(self.mainwindow.score_down_color_mixin_step)

        self.opacity.setValue(self.mainwindow.opacity)

        self.autosave.setChecked(self.mainwindow.auto_save_enabled)
        self.autosavetime.setValue(self.mainwindow.auto_save_interval)

        self.savepath.clear()
        self.savepath.addItem("工具箱目录下")
        self.savepath.addItem("用户目录下")
        self.savepath_2.clear()
        self.savepath_2.addItem("无")
        self.savepath_2.addItem("仅保存存档")
        self.savepath_2.addItem("把整个工具备份了（NCW式暴力备份）")

        self.log_keep.setValue(self.mainwindow.log_keep_linecount)
        self.log_update.setValue(self.mainwindow.log_update_interval)
        self.savepath.setCurrentIndex(int(self.mainwindow.auto_save_path != "folder"))

        self.savepath_2.setCurrentIndex(
            0
            if self.mainwindow.auto_backup_scheme == "none"
            else (1 if self.mainwindow.auto_backup_scheme == "only_data" else 2)
        )
        self.horizontalSlider.setValue(
            self.speed_to_index(self.mainwindow.animation_speed)
        )
        self.horizontalSlider.actionTriggered.connect(
            lambda: self.label_26.setText(
                self.update_animation_speed_desc(self.horizontalSlider.value())[1]
            )
        )
        self.label_26.setText(
            self.update_animation_speed_desc(self.horizontalSlider.value())[1]
        )
        self.spinBox.setValue(self.mainwindow.subwindow_x_offset)
        self.spinBox_2.setValue(self.mainwindow.subwindow_y_offset)
        self.spinBox_3.setValue(self.mainwindow.max_framerate)
        self.checkBox.setChecked(self.mainwindow.use_animate_background)

    def update(self):
        self.label_26.setText(
            self.update_animation_speed_desc(self.horizontalSlider.value())[1]
        )
        super().update()

    def update_animation_speed_desc(self, num) -> Tuple[int, str]:
        if num == 1:
            return (0.1, "0.1倍")
        if num == 2:
            return (0.1, "0.1倍")
        if num == 3:
            return (0.2, "0.2倍")
        if num == 4:
            return (0.5, "0.5倍")
        if num == 5:
            return (0.6, "0.6倍")
        if num == 6:
            return (0.8, "0.8倍")
        if num == 7:
            return (0.9, "0.9倍")
        if num == 8:
            return (1, "1倍")
        if num == 9:
            return (1.1, "1.1倍")
        if num == 10:
            return (1.2, "1.2倍")
        if num == 11:
            return (1.5, "1.5倍")
        if num == 12:
            return (1.8, "1.8倍")
        if num == 13:
            return (2, "2倍")
        if num == 14:
            return (3, "3倍")
        if num == 15:
            return (4, "4倍")
        if num == 16:
            return (6, "6倍")
        if num == 17:
            return (8, "8倍")
        if num == 18:
            return (10, "10倍")
        if num == 19:
            return (float("inf"), "关闭")
        if num == 20:
            return (float("inf"), "关闭")

    def speed_to_index(self, animationspeed: float):
        if 0.05 <= animationspeed <= 0.15:
            return 2
        if 0.15 <= animationspeed <= 0.25:
            return 3
        if 0.45 <= animationspeed <= 0.55:
            return 4
        if 0.55 <= animationspeed <= 0.65:
            return 5
        if 0.75 <= animationspeed <= 0.85:
            return 6
        if 0.85 <= animationspeed <= 0.95:
            return 7
        if 0.95 <= animationspeed <= 1.05:
            return 8
        if 1.09 <= animationspeed <= 1.11:
            return 9
        if 1.15 <= animationspeed <= 1.25:
            return 10
        if 1.45 <= animationspeed <= 1.55:
            return 11
        if 1.75 <= animationspeed <= 1.85:
            return 12
        if animationspeed == 2:
            return 13
        if animationspeed == 3:
            return 14
        if animationspeed == 4:
            return 15
        if animationspeed == 6:
            return 16
        if animationspeed == 8:
            return 17
        if animationspeed == 10:
            return 18
        if animationspeed > 114514:
            return 19

    def closeEvent(self, event: QCloseEvent, tip=True):
        if tip:
            if question_yes_no(self, "警告", "退出前保存？", True, "warning"):
                self.accept_save()
        else:
            super().closeEvent(event)

    @Slot()
    def accept_save(self):
        self.mainwindow.score_up_color_mixin_begin = (
            self.score_up_color_r.value(),
            self.score_up_color_g.value(),
            self.score_up_color_b.value(),
        )
        self.mainwindow.score_down_color_mixin_begin = (
            self.score_down_color_r.value(),
            self.score_down_color_g.value(),
            self.score_down_color_b.value(),
        )
        self.mainwindow.score_up_color_mixin_end = (
            self.score_up_color_end_r.value(),
            self.score_up_color_end_g.value(),
            self.score_up_color_end_b.value(),
        )
        self.mainwindow.score_down_color_mixin_end = (
            self.score_down_color_end_r.value(),
            self.score_down_color_end_g.value(),
            self.score_down_color_end_b.value(),
        )
        self.mainwindow.score_up_color_mixin_step = self.score_up_color_step.value()

        self.mainwindow.score_down_color_mixin_step = self.score_down_color_step.value()

        self.mainwindow.score_up_color_mixin_start = (
            self.score_up_color_mixin_start.value()
        )

        self.mainwindow.score_down_color_mixin_start = (
            self.score_down_color_mixin_start.value()
        )

        self.mainwindow.opacity = self.opacity.value()

        self.mainwindow.log_keep_linecount = self.log_keep.value()
        self.mainwindow.log_update_interval = self.log_update.value()

        self.mainwindow.auto_save_enabled = self.autosave.isChecked()
        self.mainwindow.auto_save_interval = self.autosavetime.value()
        self.mainwindow.auto_save_path = (
            "folder" if self.savepath.currentIndex() == 0 else "user"
        )
        self.mainwindow.auto_backup_scheme = (
            "none"
            if self.savepath_2.currentIndex() == 0
            else "only_data" if self.savepath_2.currentIndex() == 1 else "all"
        )

        self.mainwindow.animation_speed = self.update_animation_speed_desc(
            self.horizontalSlider.value()
        )[0]

        # 这个弃用了，因为懒得写
        if self.mainwindow.auto_save_path == "user":
            self.save_path = (
                os.environ.get("USERPROFILE")
                + f"\\AppData\\Roaming\\ClassManager\\chunks\\{default_user}"
            )
        else:
            self.save_path = os.getcwd() + os.sep + f"chunks/{default_user}"

        self.mainwindow.subwindow_x_offset = self.spinBox.value()
        self.mainwindow.subwindow_y_offset = self.spinBox_2.value()

        self.mainwindow.max_framerate = self.spinBox_3.value()
        self.mainwindow.use_animate_background = self.checkBox.isChecked()

        self.mainwindow.save_current_settings()

        self.closeEvent(QCloseEvent(), tip=False)

    @Slot()
    def cancel_save(self):
        Base.log("I", "取消保存", "SettingWidget.cancel_save")
        self.closeEvent(QCloseEvent(), tip=False)


class WTFWidget(WTF.Ui_Form, MyWidget):
    "我愿称之为世界上最抽象的UI"

    def __init__(self, master_widget: ClassWindow = None):
        """
        初始化

        :param mainwindow: 程序的主窗口，方便传参
        :param master_widget: 这个窗口的父窗口
        """
        super().__init__(master=master_widget)
        self.setupUi(self)
        self.pushButton_18.clicked.connect(
            lambda: QMessageBox.information(self, "6", "恭喜你发现了一个没什么用的彩蛋")
        )
        self.setWindowTitle("1145141919810")
        self.show()


class AchievementWidget(AchievementWindow.Ui_Form, MyWidget):
    def __init__(
        self,
        master_widget: Optional[WidgetType] = None,
        mainwindow: ClassWindow = None,
        achievement: Union[Achievement, AchievementTemplate] = None,
    ):
        """
        初始化

        :param master_widget: 这个窗口的父窗口
        :param mainwindow: 程序的主窗口，方便传参
        """
        super().__init__(master=master_widget)
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.achievement = achievement
        self.setupUi(self)
        self.show()
        self.setWindowTitle("成就详情")
        if isinstance(self.achievement, Achievement):
            self.label_11.setText(self.achievement.target.name)
            self.label_13.setText(str(self.achievement.target.score))
            self.label_15.setText("不到啊，可能是侦测器爆了")
            self.label_7.setText(str(self.achievement.time))

            for i, s in self.mainwindow.class_obs.rank_non_dumplicate:
                if (
                    s.num == self.achievement.target.num
                    and s.belongs_to == self.achievement.target.belongs_to
                ):
                    self.label_15.setText(str(i))
                    break
            self.achievement = self.achievement.temp

        self.label_5.setText(self.achievement.name)
        self.label_6.setText(self.achievement.desc)
        self.textBrowser.setPlainText(
            self.achievement.condition_desc(self.mainwindow.class_obs)
        )
        self.textBrowser_2.setPlainText(self.achievement.further_info)


class CleaningScoreSumUpWidget(CleaingScoreSumUp.Ui_Form, MyWidget):
    def __init__(
        self, master_widget: Optional[WidgetType] = None, mainwindow: ClassWindow = None
    ):
        """
        初始化

        :param master_widget: 这个窗口的父窗口
        :param mainwindow: 程序的主窗口，方便传参
        """
        super().__init__(master=master_widget)
        self.mainwindow = mainwindow
        self.master_widget = master_widget
        self.setupUi(self)
        self.finished = False
        self.leader = []
        self.member = []
        self.comboBox.clear()
        self.comboBox.addItems(["星期一", "星期二", "星期三", "星期四", "星期五"])
        self.comboBox_2.clear()
        self.comboBox_2.addItems(["5.0", "4.9", "4.8", "4.7", "4.6及以下"])
        self.mod_leader = [
            "cleaning_5.0_leader",
            "cleaning_4.9_leader",
            "cleaning_4.8_leader",
            "cleaning_4.7_leader",
            "cleaning_4.6_and_lower_leader",
        ]

        self.mod_member = [
            "cleaning_5.0_member",
            "cleaning_4.9_member",
            "cleaning_4.8_member",
            "cleaning_4.7_member",
            "cleaning_4.6_and_lower_member",
        ]

        self.comboBox.setCurrentIndex(
            min((time.localtime().tm_wday + 7 - 1) % 7, 4)
        )  # 因为第二天才会出分数所以要减1（会人性化很多）
        self.comboBox_2.setCurrentIndex(1)
        self.update_students()
        self.buttonBox.accepted.connect(self.commit)
        self.buttonBox.rejected.connect(self.cancel)
        self.comboBox.currentIndexChanged.connect(
            lambda: self.update_students(refresh_stu=True)
        )
        self.comboBox_2.currentIndexChanged.connect(
            lambda: self.update_students(refresh_stu=False)
        )

        self.listWidget.itemDoubleClicked.connect(self.remove_from_list)
        self.show()

    def show(self):
        super().show()
        self.finished = False
        self.update_students()

    def update_students(self, refresh_stu=True):
        "更新学生"
        self.label_5.setText(
            self.mainwindow.modify_templates[
                self.mod_member[self.comboBox_2.currentIndex()]
            ].desc
        )
        selected = self.comboBox.currentIndex() + 1
        if refresh_stu:
            self.leader = copy.deepcopy(
                self.mainwindow.target_class.cleaning_mapping[selected]["leader"]
            )
            self.member = copy.deepcopy(
                self.mainwindow.target_class.cleaning_mapping[selected]["member"]
            )

        self.listWidget.clear()
        for s in self.leader:
            index = self.comboBox_2.currentIndex()
            if index == 0:
                score = self.mainwindow.modify_templates["cleaning_5.0_leader"].mod
            elif index == 1:
                score = self.mainwindow.modify_templates["cleaning_4.9_leader"].mod
            elif index == 2:
                score = self.mainwindow.modify_templates["cleaning_4.8_leader"].mod
            elif index == 3:
                score = self.mainwindow.modify_templates["cleaning_4.7_leader"].mod
            else:
                score = self.mainwindow.modify_templates[
                    "cleaning_4.6_and_lower_leader"
                ].mod
            self.listWidget.addItem(
                QListWidgetItem(f"{s.num}号 {s.name} ({score:+.1f}) <组长>")
            )

        for s in self.member:
            index = self.comboBox_2.currentIndex()
            if index == 0:
                score = self.mainwindow.modify_templates["cleaning_5.0_member"].mod
            elif index == 1:
                score = self.mainwindow.modify_templates["cleaning_4.9_member"].mod
            elif index == 2:
                score = self.mainwindow.modify_templates["cleaning_4.8_member"].mod
            elif index == 3:
                score = self.mainwindow.modify_templates["cleaning_4.7_member"].mod
            else:
                score = self.mainwindow.modify_templates[
                    "cleaning_4.6_and_lower_member"
                ].mod
            self.listWidget.addItem(
                QListWidgetItem(f"{s.num}号 {s.name} ({score:+.1f})")
            )

    def remove_from_list(self):
        "从列表中移除"
        if self.listWidget.currentRow() == 0 and self.leader != []:
            s = self.leader.pop(0)
            Base.log(
                "I",
                f"从组长列表移除{s.num}，" 
                f"当前列表：{[s.num for s in self.leader]}",
                "CleaningScoreSumUpWidget",
            )
            self.update_students(refresh_stu=False)
        else:
            s = self.member.pop(
                self.listWidget.currentRow() - (1 if self.leader != [] else 0)
            )
            Base.log(
                "I",
                f"从成员列表移除{s.num}，" 
                f"当前列表：{[s.num for s in self.member]}",
                "CleaningScoreSumUpWidget",
            )
            self.update_students(refresh_stu=False)

    @Slot()
    def commit(self):
        "提交按钮"
        Base.log(
            "I",
            f"提交按钮被点击，结果：组长{[s.num for s in self.leader]} 成员{[s.num for s in self.member]}",
            "CleaningScoreSumUpWidget",
        )
        if not self.finished:
            self.finished = True

            self.mainwindow.send_modify(
                self.mod_leader[self.comboBox_2.currentIndex()],
                [
                    self.mainwindow.classes[l.belongs_to].students[l.num]
                    for l in self.leader
                ],
            )

            self.mainwindow.send_modify(
                self.mod_member[self.comboBox_2.currentIndex()],
                [
                    self.mainwindow.classes[m.belongs_to].students[m.num]
                    for m in self.member
                ],
            )

            self.closeEvent(QCloseEvent())

    @Slot()
    def cancel(self):
        "取消按钮"
        self.closeEvent(QCloseEvent())


class AttendanceInfoWidget(AttendanceInfoEdit.Ui_Form, MyWidget):
    "考勤信息窗口"

    grid_button_signal = Signal()
    "排列按钮的信号"

    def __init__(
        self,
        master: Optional[WidgetType] = None,
        mainwindow: ClassWindow = None,
        attendanceinfo: AttendanceInfo = None,
    ):
        """
        构造新窗口

        :param parent: 父窗口
        :param mainwindow: 主窗口
        :param attendanceinfo: 考勤信息
        """
        super().__init__(master)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.attendanceinfo = attendanceinfo
        self.finished = False
        self.stu_buttons: Dict[int, ObjectButton] = {}
        self.stu_states: Dict[
            int,
            Literal[
                "normal",  # 到校正常
                "early",  # 提前到校
                "late",  # 迟到
                "late_more",  # 迟到过久
                "absent",  # 请假/缺勤
                "leave",  # 临时请假
                "leave_early",  # 未知早退
                "leave_late",  # 晚退
            ],
        ] = {}
        self.target_class = self.mainwindow.classes[attendanceinfo.target_class]
        for s in self.target_class.students.values():
            self.stu_states[s.num] = "normal"
        for s in self.attendanceinfo.is_absent:
            self.stu_states[s.num] = "absent"
        for s in self.attendanceinfo.is_late:
            self.stu_states[s.num] = "late"
        for s in self.attendanceinfo.is_leave:
            self.stu_states[s.num] = "leave"
        for s in self.attendanceinfo.is_early:
            self.stu_states[s.num] = "early"
        for s in self.attendanceinfo.is_leave_early:
            self.stu_states[s.num] = "leave_early"
        for s in self.attendanceinfo.is_leave_late:
            self.stu_states[s.num] = "leave_late"
        for s in self.attendanceinfo.is_late_more:
            self.stu_states[s.num] = "late_more"
        self.grid_button_signal.connect(self._grid_buttons)
        self.grid_buttons()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_text)
        self.update_timer.start(100)
        self.radioButton.setChecked(True)
        self.pushButton.clicked.connect(self.show_attending_list)

    @staticmethod
    def attending_state_to_string(
        state: Literal[
            "normal",  # 到校正常
            "early",  # 提前到校
            "late",  # 迟到
            "late_more",  # 迟到过久
            "absent",  # 请假/缺勤
            "leave",  # 临时请假
            "leave_early",  # 未知早退
            "leave_late",  # 晚退
        ]
    ):
        "考勤状态转字符串"
        if state == "normal":
            return "到校正常"
        elif state == "early":
            return "提前到校"
        elif state == "late":
            return "迟到"
        elif state == "late_more":
            return "迟到过久"
        elif state == "absent":
            return "请假/缺勤"
        elif state == "leave":
            return "临时请假"
        elif state == "leave_early":
            return "未知早退"
        elif state == "leave_late":
            return "晚退"
        else:
            return "未知状态"

    def show(self):
        "显示窗口"
        super().show()
        self.update_text()
        self.grid_buttons()

    @Slot()
    def show_attending_list(self):
        attending_list = [
            (day.attendance_info, day.utc) for day in self.mainwindow.weekday_record
        ]
        self.listview = ListView(
            self.mainwindow,
            self,
            "考勤记录",
            [
                (
                    time.strftime("%Y年%m月%d日的考勤记录", time.localtime(utc)),
                    lambda att=att: self.show_attendance(att),
                )
                for att, utc in attending_list
            ],
        )
        self.listview.show()

    def show_attendance(self, attendanceinfo: AttendanceInfo):
        self.view = AttendanceInfoViewWidget(
            self.listview, self.mainwindow, attendanceinfo
        )
        self.view.show()

    def set_state(
        self,
        num: int,
        state: Literal[
            "normal",  # 到校正常
            "early",  # 提前到校
            "late",  # 迟到
            "late_more",  # 迟到过久
            "absent",  # 请假/缺勤
            "leave",  # 临时请假
            "leave_early",  # 未知早退
            "leave_late",  # 晚退
        ],
    ):
        # 这写的是什么爆炸东西

        stu = self.mainwindow.target_class.students[num]

        if self.stu_states[num] == "early" and state != "early":
            for h in reversed(stu.history.values()):  # 从最近的开始遍历
                if (
                    h.temp.key == "go_to_school_early"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    # 防止今天把昨天的撤掉了
                    self.mainwindow.retract_modify(h, info="<考勤撤回早到>")
                    break  # 因为只要撤回一个就行了

        if self.stu_states[num] != "early" and state == "early":
            self.mainwindow.send_modify(
                "go_to_school_early",
                self.mainwindow.target_class.students[num],
                info="<考勤早到>",
            )

        if self.stu_states[num] == "late" and state != "late":
            for h in reversed(stu.history.values()):
                if (
                    h.temp.key == "go_to_school_late"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    self.mainwindow.retract_modify(h, info="<考勤撤回迟到>")
                    break

        if self.stu_states[num] != "late" and state == "late":
            self.mainwindow.send_modify(
                "go_to_school_late",
                self.mainwindow.target_class.students[num],
                info="<考勤迟到>",
            )

        if self.stu_states[num] == "late_more" and state != "late_more":
            for h in reversed(stu.history.values()):
                if (
                    h.temp.key == "go_to_school_late_more"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    self.mainwindow.retract_modify(h, info="<考勤撤回迟到过久>")
                    break

        if self.stu_states[num] != "late_more" and state == "late_more":
            self.mainwindow.send_modify(
                "go_to_school_late_more",
                self.mainwindow.target_class.students[num],
                info="<考勤迟到过久>",
            )

        self.stu_states[num] = (
            state  # 把原来的撤回了再更新状态（你猜猜是我已经知道了还是踩过坑）
        )

        # Base.log("I", f"设置学生{num}的状态为{state}", "AttendanceInfoWidget.set_state")

        if state != "early":
            index = 0
            for s in self.attendanceinfo.is_early:
                if s.num == num:
                    self.attendanceinfo.is_early.pop(index)
                    # 不要break，宁可错杀一千也不放过一个
                index += 1

        if state != "late":
            index = 0
            for s in self.attendanceinfo.is_late:
                if s.num == num:
                    self.attendanceinfo.is_late.pop(index)
                index += 1

        if state != "late_more":
            index = 0
            for s in self.attendanceinfo.is_late_more:
                if s.num == num:
                    self.attendanceinfo.is_late_more.pop(index)
                index += 1

        if state != "absent":
            index = 0
            for s in self.attendanceinfo.is_absent:
                if s.num == num:
                    self.attendanceinfo.is_absent.pop(index)
                index += 1

        if state != "leave":
            index = 0
            for s in self.attendanceinfo.is_leave:
                if s.num == num:
                    self.attendanceinfo.is_leave.pop(index)
                index += 1

        if state != "leave_early":
            index = 0
            for s in self.attendanceinfo.is_leave_early:
                if s.num == num:
                    self.attendanceinfo.is_leave_early.pop(index)
                index += 1

        if state != "leave_late":
            index = 0
            for s in self.attendanceinfo.is_leave_late:
                if s.num == num:
                    self.attendanceinfo.is_leave_late.pop(index)
                index += 1

        if state == "early" and num not in [
            s.num for s in self.attendanceinfo.is_early
        ]:
            self.attendanceinfo.is_early.append(stu)
        elif state == "late" and num not in [
            s.num for s in self.attendanceinfo.is_late
        ]:
            self.attendanceinfo.is_late.append(stu)
        elif state == "late_more" and num not in [
            s.num for s in self.attendanceinfo.is_late_more
        ]:
            self.attendanceinfo.is_late_more.append(stu)
        elif state == "absent" and num not in [
            s.num for s in self.attendanceinfo.is_absent
        ]:
            self.attendanceinfo.is_absent.append(stu)
        elif state == "leave" and num not in [
            s.num for s in self.attendanceinfo.is_leave
        ]:
            self.attendanceinfo.is_leave.append(stu)
        elif state == "leave_early" and num not in [
            s.num for s in self.attendanceinfo.is_leave_early
        ]:
            self.attendanceinfo.is_leave_early.append(stu)
        elif state == "leave_late" and num not in [
            s.num for s in self.attendanceinfo.is_leave_late
        ]:
            self.attendanceinfo.is_leave_late.append(stu)

        self.stu_buttons[num].setText(
            f"{stu.num} {stu.name}\n{f'{self.attending_state_to_string(self.stu_states[stu.num])}'}"
        )
        self.stu_buttons[num]._set_color(
            QColor(232, 244, 232)
            if self.stu_states[stu.num] == "normal"
            else (
                QColor(202, 255, 202)
                if self.stu_states[stu.num] == "early"
                else (
                    QColor(255, 244, 232)
                    if self.stu_states[stu.num] == "late"
                    else (
                        QColor(255, 232, 232)
                        if self.stu_states[stu.num] == "late_more"
                        else (
                            QColor(196, 196, 196)
                            if self.stu_states[stu.num] == "absent"
                            else (
                                QColor(255, 255, 232)
                                if self.stu_states[stu.num] == "leave"
                                else (
                                    QColor(244, 255, 232)
                                    if self.stu_states[stu.num] == "leave_early"
                                    else (
                                        QColor(244, 244, 202)
                                        if self.stu_states[stu.num] == "leave_late"
                                        else QColor(255, 255, 255)
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

    def grid_buttons(self):
        """显示按钮（虽然不算真正意义上的grid）"""
        self.grid_button_signal.emit()

    def _grid_buttons(self):
        "显示按钮的接口"
        for b in self.stu_buttons.values():
            b.destroy()
            do_nothing()
        row = 0
        col = 0
        for num, stu in self.target_class.students.items():
            self.stu_buttons[num] = ObjectButton(
                f"{stu.num} {stu.name}\n{f'{self.attending_state_to_string(self.stu_states[stu.num])}'}",
                self,
                object=stu,
            )
            self.stu_buttons[num].opacity = 255
            self.stu_buttons[num].setObjectName("AttendingStudentButton" + str(stu.num))
            self.stu_buttons[num].setGeometry(
                QRect(10 + col * (81 + 6), 8 + row * (51 + 4), 81, 51)
            )
            self.stu_buttons[num].setParent(self.widget)
            self.stu_buttons[num].clicked.connect(
                lambda *, num=num: (
                    self.set_state(
                        num,
                        (
                            "normal"
                            if self.radioButton.isChecked()
                            else (
                                "early"
                                if self.radioButton_2.isChecked()
                                else (
                                    "late"
                                    if self.radioButton_3.isChecked()
                                    else (
                                        "late_more"
                                        if self.radioButton_4.isChecked()
                                        else (
                                            "absent"
                                            if self.radioButton_5.isChecked()
                                            else (
                                                "leave"
                                                if self.radioButton_6.isChecked()
                                                else (
                                                    "leave_early"
                                                    if self.radioButton_7.isChecked()
                                                    else (
                                                        "leave_late"
                                                        if self.radioButton_8.isChecked()
                                                        else "unknown"
                                                    )
                                                )
                                            )
                                        )
                                    )
                                )
                            )
                        ),
                    )
                )
            )
            self.set_state(num, self.stu_states[stu.num])
            self.stu_buttons[num].show()
            col += 1
            if col > 7:
                col = 0
                row += 1

    @Slot()
    def update_text(self):
        "更新文本"
        for num, stu in self.target_class.students.items():
            try:
                assert num == stu.num, "。。又对我代码干啥了"
                self.stu_buttons[num].setText(
                    f"{stu.num} {stu.name}\n{f'{self.attending_state_to_string(self.stu_states[stu.num])}'}"
                )
            except KeyError as unused:
                Base.log(
                    "W",
                    "疑似添加/减少学生，正在重新加载",
                    "AttendanceInfoWidget.update_text",
                )

        self.label_2.setText(
            f"{self.target_class.name} {time.strftime('%Y-%m-%d %H:%M:%S（%A）', time.localtime())}"
        )
        self.label_3.setText(f"应到：{len(self.target_class.students)}")
        self.label_5.setText(
            f"实到：{len(self.attendanceinfo.is_normal(self.target_class))}"
        )
        self.label_8.setText(f"早到：{len(self.attendanceinfo.is_early)}")
        self.label_7.setText(
            f"迟到：{len(self.attendanceinfo.is_late) + len(self.attendanceinfo.is_late_more)}"
        )
        self.label_10.setText(f"请假：{len(self.attendanceinfo.is_absent)}")
        self.label_6.setText(f"临时请假：{len(self.attendanceinfo.is_leave)}")
        self.label_4.setText(f"早退：{len(self.attendanceinfo.is_leave_early)}")
        self.label_9.setText(f"晚退：{len(self.attendanceinfo.is_leave_late)}")


class AttendanceInfoViewWidget(AttendanceInfoView.Ui_Form, MyWidget):
    """考勤信息查看器"""

    def __init__(
        self,
        master: Optional[WidgetType] = None,
        mainwindow: ClassWindow = None,
        attendanceinfo: AttendanceInfo = None,
    ):
        """构造新窗口

        :param master: 父窗口
        :param mainwindow: 主窗口
        :param attendanceinfo: 考勤信息
        """
        super().__init__(master)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.attendanceinfo = attendanceinfo

        self.listWidget.addItems(
            [f"{stu.num}号 {stu.name}" for stu in self.attendanceinfo.is_early]
        )

        self.listWidget_2.addItems(
            [f"{stu.num}号 {stu.name}" for stu in self.attendanceinfo.is_late]
        )

        self.listWidget_3.addItems(
            [f"{stu.num}号 {stu.name}" for stu in self.attendanceinfo.is_late_more]
        )

        self.listWidget_4.addItems(
            [f"{stu.num}号 {stu.name}" for stu in self.attendanceinfo.is_absent]
        )

        self.listWidget_5.addItems(
            [f"{stu.num}号 {stu.name}" for stu in self.attendanceinfo.is_leave]
        )

        self.listWidget_6.addItems(
            [f"{stu.num}号 {stu.name}" for stu in self.attendanceinfo.is_leave_early]
        )

        self.listWidget_7.addItems(
            [f"{stu.num}号 {stu.name}" for stu in self.attendanceinfo.is_leave_late]
        )


class NoiseDetectorWidget(NoiseDetector.Ui_Form, MyWidget):
    """噪音检测器"""

    # 定义音频参数

    try:
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNKSIZE = 1024
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNKSIZE,
        )
    except BaseException as unused:  # pylint: disable=broad-exception-caught
        p = None
        stream = None

    @staticmethod
    def caculate_db(data):
        try:
            samples = np.frombuffer(data, dtype=np.int16)
            peak_amplitude = np.abs(samples).max()
            if peak_amplitude == 0:
                return -np.inf
            else:
                return 20 * np.log10(peak_amplitude / 32768.0)
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            return -np.inf

    @staticmethod
    def caculate_abs(data):
        samples = np.frombuffer(data, dtype=np.int16)
        peak_amplitude = np.abs(samples).max()
        return peak_amplitude / 32768

    def __init__(
        self, master: Optional[WidgetType] = None, mainwindow: ClassWindow = None
    ):
        """构造新窗口

        :param master: 父窗口
        :param mainwindow: 主窗口
        """
        super().__init__(master)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_window)
        self.update_timer.start(40)
        self.read_data_thread = Thread(target=self.read_data)
        self.last_length = 0
        self.pushButton.clicked.connect(lambda: play_sound("audio/sounds/boom.mp3"))
        self.pushButton_2.clicked.connect(lambda: play_sound("audio/sounds/gl.mp3"))
        self.pushButton_3.clicked.connect(self.call_my_army)
        self.read_data_thread.start()

    def read_data(self):
        if not HAS_PYAUDIO:
            return
        while True:
            try:
                self.data = self.stream.read(self.CHUNKSIZE)
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                if self.stream is not None:
                    self.data = b"wdnmd"  # 抽象的音频信号
                else:
                    p = pyaudio.PyAudio()
                    self.stream = p.open(
                        format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNKSIZE,
                    )

    def update_window(self):
        data = self.data
        db = self.caculate_db(data)
        abs_d = self.caculate_abs(data)
        try:
            label_len = 350 * abs_d
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            label_len = 350

        if label_len >= 350:
            self.label.setStyleSheet(
                "background-color: rgb(232, 99, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 350 > label_len >= 200:
            self.label.setStyleSheet(
                "background-color: rgb(232, 172, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 190 > label_len >= 110:
            self.label.setStyleSheet(
                "background-color: rgb(232, 232, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 110 > label_len >= 60:
            self.label.setStyleSheet(
                "background-color: rgb(172, 232, 99); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 60 > label_len >= 30:
            self.label.setStyleSheet(
                "background-color: rgb(99, 232, 172); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )
        elif 30 > label_len >= 0:
            self.label.setStyleSheet(
                "background-color: rgb(99, 232, 232); border-radius: 6px; border: 2px solid rgb(0, 0, 0);"
            )

        self.label_3.setText(
            f"当前噪音：{db:.2f}db （{int(abs_d * 65536)}, {int(label_len)}）"
        )
        start = QSize(self.last_length, 21)
        end = QSize(min(label_len + 20, 350), 21)
        self.last_length = end.width()
        self.anim = QPropertyAnimation(self.label, b"size")
        self.anim.setDuration(33)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.anim.setLoopCount(1)
        self.anim.start()

    def call_my_army(self):
        "呼叫班主任"
        teacher_ip = "172.62.114.51"
        teacher_email = "1145141919@qq.com"
        Base.log(
            "I",
            f"准备呼叫班主任，班主任设备IP：{teacher_ip}, 邮箱：{teacher_email}",
            "NoiseDetectorWidget.call_my_army",
        )


class HomeworkScoreSumUpWidget(HomeworkScoreSumUp.Ui_Form, MyWidget):

    def __init__(
        self,
        master: Optional[WidgetType] = None,
        mainwindow: ClassWindow = None,
        target_class: Class = None,
        target_students: Dict[int, Student] = None,
    ):
        super().__init__(master)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.master = master
        self.target_class = target_class
        self.target_students = target_students
        self.mapping: Dict[int, Student] = {}
        self.buttons: Dict[int, ObjectButton] = {}
        self.comboBox_3.clear()
        self.comboBox_3.addItems(
            [
                str(8),
                str(9),
                str(10),
                str(11),
                str(12),
            ]
        )
        self.homework_rules = target_class.homework_rules
        self.comboBox_4.clear()
        self.comboBox_4.addItems(["添加一项", "删除一项", "查看信息", "全部删除"])
        self.comboBox.clear()
        self.sent_list: Dict[int, List[ScoreModification]] = {}
        "已经发送的列表"
        error_template = ScoreModificationTemplate(
            "error",
            0,
            "没有内置的作业常规分方案",
            "请完善default.py中Class的homework_rule",
        )
        self.subject_list: Dict[int, HomeworkRule] = {
            -1: HomeworkRule("error", "列表为空", "", {"列表为空": error_template})
        }
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_buttons)
        self.update_timer.start(100)
        self.current_template: Optional[ScoreModificationTemplate] = None
        for index, rule in enumerate(self.homework_rules.values()):
            self.subject_list[index] = rule
            self.comboBox.addItem(rule.subject_name)

        self.pushButton.clicked.connect(
            lambda: QMessageBox.information(
                self, "emm", "懒得写，要不你帮我写吧\n（不要用奇怪的眼神看我）"
            )
        )
        self.optional_template_mapping: Dict[int, ScoreModificationTemplate] = {
            -1: error_template
        }
        self.comboBox_13.clear()
        for t in [
            _t for _t in self.mainwindow.modify_templates.values() if _t.is_visible
        ]:
            self.comboBox_13.addItem(t.title)
            # -1的原因：有一个是error_template
            self.optional_template_mapping[len(self.optional_template_mapping) - 1] = t

        self.anims: Dict[int, QPropertyAnimation] = {}

        self.comboBox.setCurrentIndex(0)
        self.comboBox_3.setCurrentIndex(2)
        self.comboBox_4.setCurrentIndex(0)
        self.comboBox_13.setCurrentIndex(0)

        self.subject_changed()
        self.modification_changed()
        self.width_changed()

        self.comboBox.currentIndexChanged.connect(self.subject_changed)
        self.comboBox_2.currentIndexChanged.connect(self.modification_changed)
        self.comboBox_3.currentIndexChanged.connect(self.width_changed)
        self.comboBox_13.currentIndexChanged.connect(self.modification_changed)
        self.tabWidget_2.currentChanged.connect(self.modification_changed)

    def subject_changed(self):

        index = self.comboBox.currentIndex()
        Base.log("I", f"选中项目：{index}", "HomeworkSumpWidget.subject_changed")

        self.current_subject = self.subject_list[index]
        Base.log(
            "I",
            f"对应科目：{self.current_subject.subject_name}",
            "HomeworkSumpWidget.subject_changed",
        )

        self.current_modifacion_list: Dict[int, ScoreModificationTemplate] = {
            -1: ScoreModificationTemplate("error", 0, "出错了", "出错了")
        }
        Base.log("I", "清空列表", "HomeworkSumpWidget.subject_changed")

        self.comboBox_2.clear()
        Base.log("I", "清空comboBox", "HomeworkSumpWidget.subject_changed")

        for index, (subject, template) in enumerate(
            self.current_subject.rule_mapping.items()
        ):
            self.current_modifacion_list[index] = template
            self.comboBox_2.addItem(subject)

        Base.log(
            "I",
            f"多选窗口规则列表长度：{len(self.current_modifacion_list)}",
            "HomeworkSumpWidget.subject_changed",
        )

        self.comboBox_2.setCurrentIndex(0)

        self.modification_changed()

    def modification_changed(self):
        if self.tabWidget_2.currentIndex() == 0:
            Base.log(
                "I",
                f"作业等第模式模板更换，index = {self.comboBox_2.currentIndex()}",
                "HomeworkSumpWidget.modification_changed",
            )
            index = self.comboBox_2.currentIndex()
            self.current_template = self.current_modifacion_list[index]
            self.lineEdit.setText(str(self.current_template.title))
            self.lineEdit_2.setText(str(self.current_template.desc))
            self.doubleSpinBox.setValue(self.current_template.mod)
        else:
            Base.log(
                "I",
                f"自定义模板模式模板更换，index = {self.comboBox_13.currentIndex()}",
                "HomeworkSumpWidget.modification_changed",
            )
            index = self.comboBox_13.currentIndex()
            self.current_template = self.optional_template_mapping[index]
            self.lineEdit.setText(str(self.current_template.title))
            self.lineEdit_2.setText(str(self.current_template.desc))
            self.doubleSpinBox.setValue(self.current_template.mod)

    def width_changed(self):
        Base.log(
            "I",
            f"多选窗口宽度设置为：{self.comboBox_3.currentText()}",
            "HomeworkSumpWidget.width_changed",
        )
        for i in range(self.widget.count()):
            if isinstance(self.widget.itemAt(i).widget(), ObjectButton):
                self.widget.itemAt(i).widget().deleteLater()
        row = 0
        col = 0
        for num, stu in self.target_students.items():
            if num not in self.sent_list:
                self.sent_list[num] = []
            self.mapping[num] = stu
            button = ObjectButton(f"{stu.num}号 {stu.name}\n{stu.score}分", self.tab)
            self.widget.addWidget(button, row, col, 1, 1)
            self.buttons[num] = button
            self.buttons[num].clicked.connect(
                lambda _=None, num=num: self.do_action(num)
            )
            self.buttons[num].setFixedSize(QSize(81, 51))
            col += 1
            if col > self.comboBox_3.currentIndex() + 8 - 1:
                col = 0
                row += 1

    def update_buttons(self):
        for num, button in self.buttons.items():
            button.setText(
                f"{self.mapping[num].num}号 "
                + self.mapping[num].name
                + f"\n{self.mapping[num].score}分"
            )

    def do_action(self, num: int):
        Base.log(
            "I",
            f"进行操作：学生学号为{num}",
            "HomeworkSumpWidget.show_stu_homework_info",
        )
        mode = self.comboBox_4.currentIndex()
        if mode == 0:
            mode = "add"
        elif mode == 1:
            mode = "sub"
        elif mode == 2:
            mode = "info"
        elif mode == 3:
            mode = "clear"

        Base.log("I", "操作模式：" + mode, "HomeworkSumpWidget.show_stu_homework_info")
        if mode == "add":
            self.sent_list[num].append(
                ScoreModification(
                    self.current_template,
                    self.target_students[num],
                    (
                        self.lineEdit.text()
                        if self.lineEdit.text() != self.current_template.title
                        else None
                    ),
                    (
                        self.lineEdit_2.text()
                        if self.lineEdit_2.text() != self.current_template.desc
                        else None
                    ),
                    (
                        self.doubleSpinBox.value()
                        if self.doubleSpinBox.value() != self.current_template.mod
                        else None
                    ),
                )
            )
            self.mainwindow.send_modify_instance(self.sent_list[num][-1], "<作业登分>")
            self.anims[num] = QPropertyAnimation(self.buttons[num], b"color")
            self.anims[num].setDuration(300)
            self.anims[num].setStartValue(
                QColor(216, 255, 216)
                if self.sent_list[num][-1].mod > 0
                else (
                    QColor(255, 216, 216)
                    if self.sent_list[num][-1].mod < 0
                    else QColor(216, 244, 255)
                )
            )
            self.anims[num].setEndValue(QColor(255, 255, 255))
            self.anims[num].start()

        if mode == "sub":
            self.list_view = ListView(
                self.mainwindow, self, "已发送的作业等第点评", None
            )

            self.list_view.setData(
                [
                    (text, func, args)
                    for text, func, args in [
                        (
                            f"{m.title} {m.execute_time.split('.')[0]} {m.mod:+.1f}",
                            lambda m=m: (
                                self.mainwindow.retract_modify(m, "<作业登分>"),
                                self.sent_list[num].remove(m),
                                self.list_view.close(),
                            ),
                            (
                                (
                                    QColor(202, 255, 222)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 202, 202)
                                        if m.mod < 0
                                        else QColor(201, 232, 255)
                                    )
                                ),
                                (
                                    QColor(232, 255, 232)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 232, 232)
                                        if m.mod < 0
                                        else QColor(233, 244, 255)
                                    )
                                ),
                            ),
                        )
                        for m in reversed(self.sent_list[num])
                        if m.executed
                    ]
                ]
            )

            self.list_view.show()

        if mode == "info":
            self.list_view = ListView(
                self.mainwindow, self, "已发送的作业等第点评", None
            )
            self.list_view.setData(
                [
                    (text, func, args)
                    for text, func, args in [
                        (
                            f"{m.title} {m.execute_time.split('.')[0]} {m.mod:+.1f}",
                            lambda m=m, index=index: (
                                self.mainwindow.history_window(
                                    m, index, self.list_view, master=self
                                ),
                            ),
                            (
                                (
                                    QColor(202, 255, 222)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 202, 202)
                                        if m.mod < 0
                                        else QColor(201, 232, 255)
                                    )
                                ),
                                (
                                    QColor(232, 255, 232)
                                    if m.mod > 0
                                    else (
                                        QColor(255, 232, 232)
                                        if m.mod < 0
                                        else QColor(233, 244, 255)
                                    )
                                ),
                            ),
                        )
                        for index, m in enumerate(reversed(self.sent_list[num]))
                        if m.executed
                    ]
                ]
            )

            self.list_view.show()

        if mode == "clear":
            if not len([m for m in self.sent_list[num] if m.executed]):
                QMessageBox.information(
                    self.mainwindow,
                    "提示",
                    f"烫知识：你选择的{num}号并没有发送任何作业等第点评",
                )
                return
            if question_yes_no(
                self.mainwindow,
                "确认",
                f"确定要把刚刚所有的作业等第点评全部删除吗？\n（选中了{num}号，已经发送了{len([m for m in self.sent_list[num] if m.executed])}个）",
                False,
                "warning",
            ):
                self.mainwindow.retract_modify(
                    [m for m in self.sent_list[num] if m.executed], "<作业登分>"
                )
                self.sent_list[num] = []


class AboutWidget(About.Ui_Form, MyWidget):
    """ "关于"窗口

    做的最轻松的一个
    """

    def __init__(
        self, master: Optional[WidgetType] = None, mainwindow: ClassWindow = None
    ):

        super().__init__(master)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.master = master
        self.versioninfo.setText(
            f"客户端版本：{CLIENT_VERSION} ({CLIENT_VERSION_CODE})       核心版本: {CORE_VERSION} ({CORE_VERSION_CODE})"
        )
        self.pushButton.clicked.connect(lambda: QMessageBox.aboutQt(self))


class RandomSelectWidget(RandomSelector.Ui_Form, MyWidget):
    """随机点名窗口"""

    def __init__(
        self, master: Optional[WidgetType] = None, mainwindow: ClassWindow = None
    ):
        super().__init__(master)
        self.mainwindow = mainwindow
        self.master = master
        self.setupUi(self)
        self.from_students: List[Student] = list(
            mainwindow.target_class.students.values()
        )
        self.includes_students: List[Student] = []
        self.excludes_students: List[Student] = []
        self.result: List[Student] = []
        self.pushButton.clicked.connect(self.start)
        self.pushButton_2.clicked.connect(self.select_source)
        self.pushButton_3.clicked.connect(self.select_include)
        self.pushButton_4.clicked.connect(self.select_exclude)
        self.listWidget.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(
                self.from_students[self.listWidget.row(item)]
            )
        )
        self.listWidget_2.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(
                self.includes_students[self.listWidget_2.row(item)]
            )
        )
        self.listWidget_3.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(
                self.excludes_students[self.listWidget_3.row(item)]
            )
        )
        self.listWidget_4.itemDoubleClicked.connect(
            lambda item: self.show_stu_info(self.result[self.listWidget_4.row(item)])
        )
        self.select_window: Optional[StudentSelectorWidget] = None
        self.update_widgets()

    def update_widgets(self):
        self.listWidget.clear()
        for s in self.from_students:
            self.listWidget.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))

        self.listWidget_2.clear()
        for s in self.includes_students:
            self.listWidget_2.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))

        self.listWidget_3.clear()
        for s in self.excludes_students:
            self.listWidget_3.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))

    def select_source(self):
        self.select_window = StudentSelectorWidget(
            self,
            self,
            self.mainwindow.target_class.students.values(),
            self.from_students,
        )
        self.from_students = self.select_window.exec()
        self.listWidget.clear()
        for s in self.from_students:
            self.listWidget.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def select_include(self):
        self.select_window = StudentSelectorWidget(
            self,
            self,
            self.mainwindow.target_class.students.values(),
            self.includes_students,
        )
        self.includes_students = self.select_window.exec(allow_none=True)
        self.listWidget_2.clear()
        for s in self.includes_students:
            self.listWidget_2.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def select_exclude(self):
        self.select_window = StudentSelectorWidget(
            self,
            self,
            self.mainwindow.target_class.students.values(),
            self.excludes_students,
        )
        self.excludes_students = self.select_window.exec(allow_none=True)
        self.listWidget_3.clear()
        for s in self.excludes_students:
            self.listWidget_3.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.result = []
        self.update_widgets()

    def start(self):
        self.result = self.mainwindow.random_choose_stu(
            min(
                self.spinBox.value(),
                (len(self.from_students) - len(self.excludes_students)),
            ),
            self.from_students,
            self.includes_students,
            self.excludes_students,
        )
        if not isinstance(self.result, list):
            self.result = [self.result]
        self.listWidget_4.clear()
        for s in self.result:
            self.listWidget_4.addItem(QListWidgetItem(f"{s.num}号 {s.name}"))
        self.update_widgets()

    def show_stu_info(self, stu: Student):
        Base.log("I", f"显示学生信息：{stu.name}", "RandomSelectWindow.show_stu_info")
        self.stu_info_window = StudentWidget(self.mainwindow, self, stu)
        self.stu_info_window.show()


class DebugWidget(DebugWindow.Ui_Form, MyWidget):
    """调试窗口"""

    output_lines = []
    last_line = 0
    command_history = []

    def __init__(
        self, master: Optional[WidgetType] = None, mainwindow: ClassWindow = None
    ):
        super().__init__(master)
        self.setupUi(self)
        self.mainwindow = mainwindow
        self.master = master
        self.pushButton.clicked.connect(self.send_command)
        self.pushButton_4.clicked.connect(self.send_command_in_thread)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(60)
        self.textbroser_last = DebugWidget.last_line
        # self.textBrowser.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.last_text = ""
        self.history_index = len(self.command_history) - 1
        self.pushButton_2.clicked.connect(self.prev_history)
        self.pushButton_3.clicked.connect(self.next_history)
        self.textEdit.installEventFilter(self)
        self.textEdit.setTabChangesFocus(False)
        self.textEdit.setTabStopDistance(
            self.fontMetrics().size(0, " " * 4).width()
        )  # 把tab设为4个空格
        self.textBrowser.setTabStopDistance(self.fontMetrics().size(0, " " * 4).width())
        self.textEdit.setAcceptRichText(False)
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.textEdit.setPlaceholderText("输入命令...")
        self.textEdit.setFocus()
        self.comboBox.currentIndexChanged.connect(self.change_command)
        cmds = [
            ("self.findstu()", "查找学生"),
            ("os._exit(0)", "原地爆炸"),
            ('os.system("shutdown -s -f -t 114514")', "原地爆炸升级版"),
            ("self.reset_scores()", "重置"),
            (
                """\
[ s.num for s in
self.random_choose_stu(
    5,
    includes=[self.findstu(9)],
    excludes=[self.findstu(7)]
)]""",
                "随机抽学生",
            ),
            (
                """\
import math
print(math.sqrt(114514))""",
                "计算114514的平方根",
            ),
            (
                """\
DataObject.saved_objects = 0
c = Chunk("chunks/test_chunk/example", self.database)
t = time.time()
c.save()
print("时间:", time.time() - t)
print("数量:", DataObject.saved_objects)
print("速率:", (DataObject.saved_objects / (time.time() - t)))""",
                "测试保存数据分组",
            ),
            (
                """\
self.achievement_obs.stop()
for i in range(15):
    for _ in range(114):
        self.send_modify("wearing_bad", list(self.target_class.students.values()))
""",
                "大数据测试",
            ),
            (
                """\
c = Chunk("chunks/test_chunk/example", self.database)
t = time.time()
c.load_history()
print("时间:", time.time() - t)
""",
                "测试数据保存",
            ),
            (
                """
for i in range(100):
    self.add_student(
    f"{max(*self.target_class.students) + 1}号学生",
    default_class_key,
    max(*self.target_class.students) + 1
)
""",
                "添加学生",
            ),
        ]
        self.comboBox.clear()
        self.comboBox.addItem("快捷命令")
        for cmd, name in cmds:
            self.comboBox.addItem(name, cmd)
        self.comboBox.setCurrentIndex(0)
        if len(self.command_history):
            self.textEdit.setText(self.command_history[self.history_index])
        self.update()

    def show(self):
        super().show()
        self.output_lines = []

    def change_command(self):
        index = self.comboBox.currentIndex()
        if (
            index <= 0
        ):  # 一定要 <= 0，因为clear()的时候可能会传过来一个-1让程序爆掉，别问我怎么知道的
            return
        self.textEdit.setText(self.comboBox.itemData(index))
        self.comboBox.setCurrentIndex(0)
        self.textEdit.setFocus()

    def update(self):
        self.label_5.setText(str(self.mainwindow.sidenotice_waiting_order.qsize()))
        self.label_6.setText(str(SideNotice.showing))
        self.label_7.setText(str(SideNotice.waiting))
        self.label_8.setText(str(SideNotice.current))
        self.label_21.setText(str(round(self.mainwindow.class_obs.tps, 3)))
        self.label_22.setText(str(round(self.mainwindow.achievement_obs.tps, 3)))
        self.label_23.setText(str(round(time.time() - self.mainwindow.create_time, 3)))
        self.label_24.setText(
            str(self.mainwindow.achievement_obs.display_achievement_queue.qsize())
        )
        self.label_27.setText(str(round(self.mainwindow.class_obs.mspt, 3)))
        self.label_28.setText(str(round(self.mainwindow.achievement_obs.mspt, 3)))

        self.textbroser_last = len(output_list)
        self.label_9.setText(
            str(f"{self.history_index + 1}/{len(DebugWidget.command_history)}")
        )
        text = "\n".join(output_list[DebugWidget.last_line :])
        if text != self.last_text:
            self.textBrowser.setText(text)
            self.last_text = text
            self.textBrowser.verticalScrollBar().setValue(
                self.textBrowser.verticalScrollBar().maximum()
            )
        super().update()

    def closeEvent(self, event):
        super().closeEvent(event)
        DebugWidget.last_line = self.textbroser_last
        self.update_timer.stop()

    def prev_history(self):
        if len(DebugWidget.command_history) == 0 or self.history_index == 0:
            return
        self.history_index = max(0, self.history_index - 1)
        if not (self.history_index == 0 and not self.textEdit.toPlainText().strip()):
            self.textEdit.setText(DebugWidget.command_history[self.history_index])

    def next_history(self):
        if len(DebugWidget.command_history) == 0:
            return
        self.history_index = min(
            len(DebugWidget.command_history) - 1, self.history_index + 1
        )
        if not (
            self.history_index == len(DebugWidget.command_history) - 1
            and not self.textEdit.toPlainText().strip()
        ):
            self.textEdit.setText(DebugWidget.command_history[self.history_index])

    @Slot()
    def send_command(self):
        if not self.textEdit.toPlainText().strip():
            return
        cmd = self.textEdit.toPlainText()
        if len(cmd.splitlines()) > 1:
            sys.stdout.write(">> " + cmd.splitlines()[0] + "\n")
            for l in cmd.splitlines()[1:]:
                sys.stdout.write(">> " + l + "\n")
        else:
            sys.stdout.write(">> " + cmd + "\n")
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        ret = None
        try:
            ret = self.mainwindow.exec_command(cmd)
        except BaseException as unused:  # pylint: disable=broad-exception-caught
            sys.stderr.write(traceback.format_exc() + "\n")
            sys.stderr.write("-----------------------------------------" + "\n")
            sys.stderr.write("\n".join(format_exc_like_java(sys.exc_info()[1])) + "\n")
        else:
            if ret is not None:
                sys.stdout.write(repr(ret) + "\n")
        self.command_history.append(cmd)
        self.history_index = len(self.command_history) - 1
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)

    @Slot()
    def send_command_in_thread(self):
        self.pushButton.setEnabled(False)
        cmd = self.textEdit.toPlainText()
        if not cmd.strip():
            return
        if len(cmd.splitlines()) > 1:
            sys.stdout.write(">> " + cmd.splitlines()[0] + "\n")
            for l in cmd.splitlines()[1:]:
                sys.stdout.write(">> " + l + "\n")
        else:
            sys.stdout.write(">> " + cmd + "\n")
        self.pushButton.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        ret = None
        finished = False

        def _send():
            nonlocal ret, finished
            try:
                ret = self.mainwindow.exec_command(cmd)
            except BaseException as unused:  # pylint: disable=broad-exception-caught
                sys.stderr.write(traceback.format_exc() + "\n")
                sys.stderr.write("-----------------------------------------" + "\n")
                sys.stderr.write(
                    "\n".join(format_exc_like_java(sys.exc_info()[1])) + "\n"
                )
            else:
                if ret is not None:
                    sys.stdout.write(repr(ret) + "\n")
            finished = True

        Thread(target=_send).start()
        while not finished:
            do_nothing()
        self.command_history.append(cmd)
        self.history_index = len(self.command_history) - 1
        self.pushButton.setEnabled(True)
        self.pushButton_4.setEnabled(True)


@profile(precision=4)
def main():
    global widget
    # 登录模块写在这里，用户名存在user里面就行
    user = login()
    class_key = DEFAULT_CLASS_KEY
    widget = ClassWindow(*sys.argv, current_user=user, class_key=class_key)
    # 其实MainWindow也只是做了个接口，整个程序还没做完（因为还有分班和添加/删除学生）

    try:
        stat = widget.mainloop()
    except BaseException as unused:  # pylint: disable=broad-exception-caught
        stat = 1
        Base.log("E", "程序异常退出", "MainThread")
        Base.log("E", traceback.format_exc(), "MainThread")
    Base.log("I", f"程序结束，返回值：{stat}", "MainThread")
    Base.log("I", "等待自动保存...", "MainThread")
    while widget.auto_saving:
        "等待自动保存完成"
        time.sleep(0.1)
    Base.log("I", "自动保存完成，趋势", "MainThread")
    return stat


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
