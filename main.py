"""
____，启动！
"""

# -*- coding: utf-8 -*-
# 奇怪的癖好：把import语句的顺序按长短排列（？
import os
import sys
import time
import math
import enum
import random
import pickle
import signal
import warnings
import traceback
import threading
import functools
from queue import Queue
from typing import Optional, Union, List, Tuple, Dict, Callable, Literal, Type
from shutil import copytree, rmtree, copy as shutil_copy
from concurrent.futures import ThreadPoolExecutor
from types import TracebackType
from typing import Mapping, Any, Iterable


import psutil
import requests
import numpy as np
import customtkinter  # pylint: disable=unused-import
import dill as pickle  # pylint: disable=shadowed-import
from qfluentwidgets.common import *  # pylint: disable=wildcard-import, unused-wildcard-import
from qfluentwidgets.components import *  # pylint: disable=wildcard-import, unused-wildcard-import
from qfluentwidgets.window import *  # pylint: disable=wildcard-import, unused-wildcard-import
from qfluentwidgets.multimedia import *  # pylint: disable=wildcard-import, unused-wildcard-import

from widgets.ui.pyside6 import (
    MainClassWindow,
    NoticeViewer
)

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "114514" # 可以让pygame闭嘴

from utils.basetypes import logger # pylint: disable=wrong-import-position

from utils.classobjects import (  # pylint: disable=unused-import, disable=wrong-import-position
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
    default_user
)


from utils.functions import steprange, play_sound, play_music, stop_music
from utils.classobjects import (
    CORE_VERSION,
    CORE_VERSION_CODE,
    VERSION_INFO,
    CLIENT_UPDATE_LOG,
    DEFAULT_CLASS_KEY
)
from utils.classobjects import Chunk, UserDataBase
from utils.consts import (
    app_style,
    app_stylesheet,
    nl,
    enable_memory_tracing,
    runtime_flags
)
from widgets.basic.widgets import ObjectButton, ProgressAnimatedListWidgetItem, SideNotice
from utils.functions import question_yes_no as question_yes_no_orig, question_chooose
from utils.functions import format_exc_like_java
from utils.settings import SettingsInfo
from utils.system import output_list
from utils.basetypes import DataObject
from utils.algorithm import Thread
import utils.functions.prompts as PromptUtils
from widgets.custom.NoiseDetectorWidget import HAS_PYAUDIO
from widgets import *

try:
    from utils.login import login
except ImportError:
    from utils.bak.login import login

    warnings.warn(
        "没有自定义登录模块，将使用默认，"
        "如果需要自定义登录模块请创建/修改utils/login.py"
    )


ExceptionInfoType = Tuple[Type[BaseException], BaseException, TracebackType]
"""异常信息类型"""

CLIENT_VERSION: str = VERSION_INFO["client_version"]
"应用程序界面版本"
CLIENT_VERSION_CODE: str = VERSION_INFO["client_version_code"]
"应用程序界面版本编码"

settings: SettingsInfo = SettingsInfo.current
"全局设置对象"


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



HAS_CV2: bool = False
"OpenCV库可用性标志"


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
        app: QApplication,
        *args: str,
        class_name: str = "测试班级",
        current_user: str = default_user,
        class_key: str ="CLASS_TEST",
    ):
        """
        窗口初始化
        :param app: QApplication
        :param args: 命令行参数
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
        "背景透明度"
        self.current_user = current_user
        "当前用户"
        self.background_pixmap: Optional[QPixmap] = None
        "背景图片"
        self.lastest_pixmap_update_time: float = 0.0
        "上次更新背景图片的时间"
        self.window_info: ClassWindow.WindowInfo = ClassWindow.WindowInfo()
        "窗口信息"
        self.btns_anim_group: Optional[QParallelAnimationGroup] = QParallelAnimationGroup()
        "按钮动画组"
        self.running_btns_anim_group: Optional[QParallelAnimationGroup] = QParallelAnimationGroup()
        "运行中的按钮动画组"
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
        self.stu_buttons: Optional[Dict[int, ObjectButton]] = None
        "学生按钮列表"
        self.grp_buttons: Optional[Dict[str, ObjectButton]] = None
        "小组按钮列表"
        Base.log("I", "程序创建", "MainWindow.__init__")
        self.app = app
        if qt_version in ("PySide6", "PyQt6"):
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
        self.button_update.connect(self.btn_anim)
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
        self.anim_group_state_changed.connect(self._anim_group_state_changed)

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
        self.tip_handler = self.TipHandler(self)
        self.tip_handler.start()
        self.logwindow_content: List[str] = ["这里是日志"]
        self.auto_saving = False
        self.setWindowTitle(f"班寄管理 - {self.target_class.name}")
        self.terminal_locals = {}
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start(100)
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

    def __repr__(self):  # 其实是因为直接继承ClassObjects的repr会导致无限递归
        return super(MyMainWindow, self).__repr__()

    def init_display_data(self):
        """ "初始化显示数据和存储数据"""
        Base.log("I", "初始化本地显示数据", "MainWindow.init_display_data")
        self.target_class: Class
        if not self.stu_buttons:
            self.stu_buttons: Dict[int, ObjectButton] = {}
            self.grp_buttons: Dict[str, ObjectButton] = {}
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
        settings.reset_settings()
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

    ##### Qt相关 #####

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
            wait_loop = QEventLoop()
            wait_timer = QTimer()
            def _check_if_finished():
                "检查是否完成退出操作"
                if self.exit_action_finished:
                    wait_loop.quit()
                    wait_timer.stop()
            wait_timer.timeout.connect(_check_if_finished)
            wait_timer.start(33)
            wait_loop.exec()
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
            self.background_pixmap = self.current_video_frame
    
        else:
            if not os.path.exists("./img/main/background.jpg"):
                # 为了防止更新的时候给原有的background.jpg覆盖了
                shutil_copy(
                    "./img/main/default/background.jpg", 
                    "./img/main/background.jpg"
                )
                
        
            if not self.background_pixmap:
                self.background_pixmap = QPixmap("./img/main/background.jpg")

            # 距离上一次更新差了一秒以上就更新
            if time.time() - self.lastest_pixmap_update_time >= 1:
                self.background_pixmap = time.time()
                self.background_pixmap = QPixmap("./img/main/background.jpg")

        t3 = time.time()

        painter = QPainter(self)
        t4 = time.time()

        painter.drawPixmap(
            -padding,
            -padding,
            self.width() + padding * 2,
            self.height() + padding * 2,
            self.background_pixmap,
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
                self.current_video_frame = QPixmap(QImage(
                    frame.data, w, h, 3 * w, QImage.Format.Format_BGR888
                ))

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
        row = 0
        col = 0
        max_col = (self.scrollArea.width() + 6) // (81 + 6)
        height = 0
        self.scrollAreaWidgetContents_2.setGeometry(
            0, 0, 901, max((51 + 4) * len(self.target_class.students), 410)
        )
        for key, stu in self.target_class.students.items():
            self.stu_buttons[key] = ObjectButton(
                f"{stu.num}号 {stu.name}\n{stu.score}分", self, object=stu
            )
            self.stu_buttons[key].setObjectName("StudentButton" + str(stu.num))
            self.stu_buttons[key].setGeometry(
                QRect(10 + col * (81 + 6), 8 + row * (51 + 4), 81, 51)
            )
            self.stu_buttons[key].setParent(self.scrollAreaWidgetContents_2)
            self.stu_buttons[key].clicked.connect(
                lambda *, stu=stu: self.student_info(stu)
            )
            self.stu_buttons[key].show()
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
        for key, grp in self.target_class.groups.items():
            if grp.belongs_to == self.target_class.key:
                self.grp_buttons[key] = ObjectButton(
                    f"{grp.name}\n{stu.score}分", self, object=stu
                )
                self.grp_buttons[key].setObjectName("GroupButton" + str(stu.num))
                self.grp_buttons[key].setGeometry(
                    QRect(10 + col * (162 + 6), 8 + row * (102 + 4), 162, 102)
                )
                self.grp_buttons[key].setParent(self.tab_4)
                self.grp_buttons[key].clicked.connect(
                    lambda *, grp=grp: self.group_info(grp)
                )
                self.grp_buttons[key].show()
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
    def btn_anim(self, obj: ObjectButton, args: tuple):
        """闪烁按钮"""
        # self.btns_anim_group.addAnimation(obj.get_flash_anim(*args, from_self=False))
        obj.flash(*args)
    
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
        if self.btns_anim_group is None:
            return
        if state == self.AnimationGroupStatement.CREATE_NEW:
            self.btns_anim_group = QParallelAnimationGroup(self)
        elif state == self.AnimationGroupStatement.START:
            self.running_btns_anim_group = self.btns_anim_group
            self.running_btns_anim_group.start(QParallelAnimationGroup.DeletionPolicy.KeepWhenStopped)
        elif state == self.AnimationGroupStatement.STOP:
            self.running_btns_anim_group.stop()
        elif state == self.AnimationGroupStatement.DELETE:
            self.running_btns_anim_group.deleteLater()
            self.btns_anim_group = None

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
        self.refresh_hint_widget()
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
        wait_timer = QTimer()
        wait_loop = QEventLoop()
        def _check_if_finished():
            if not t.is_alive():
                wait_loop.quit()
        wait_timer.timeout.connect(_check_if_finished)
        wait_timer.start(33)
        wait_loop.exec()
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
            if self.attendance_window:
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
        wait_timer = QTimer()
        wait_loop = QEventLoop()
        def _check_if_finished():
            if finished:
                wait_timer.stop()
                wait_loop.quit()
        wait_timer.timeout.connect(_check_if_finished)
        wait_timer.start(33)
        wait_loop.exec()
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
                QCoreApplication.processEvents()
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
                QCoreApplication.processEvents()
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

    def exec_command(self, command: str) -> Any:
        """
        执行一行字符串形式的Python命令。
        
        :param command: 要执行的命令
        :return: 命令的返回值
        """
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
        "刷新窗口"
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
        path = QFileDialog.getExistingDirectory(
            self, "另存为", self.save_path,
        )
        if path and path.strip() != "":
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
        from utils.update_check import AUTHOR, REPO_NAME
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
        wait_loop = QEventLoop()
        wait_timer = QTimer()
        def _check_if_finished():
            if not widget.auto_saving:
                wait_loop.quit()
                wait_timer.stop()
        wait_timer.timeout.connect(_check_if_finished)
        wait_timer.start(33)
        wait_loop.exec()
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

        wait_loop = QEventLoop()
        wait_timer = QTimer()
        def _check_if_finished():
            if not widget.auto_saving:
                wait_loop.quit()
                wait_timer.stop()
        wait_timer.timeout.connect(_check_if_finished)
        wait_timer.start(33)
        wait_loop.exec()
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

app = QApplication(sys.argv)


@profile(precision=4)
def main():
    # 登录模块写在这里，用户名存在user里面就行
    global widget
    user = "default"
    class_key = DEFAULT_CLASS_KEY
    widget = ClassWindow(app, *sys.argv, current_user=user, class_key=class_key)
    # 其实MainWindow也只是做了个接口，整个程序还没做完（因为还有分班和添加/删除学生）

    try:
        stat = widget.mainloop()
    except BaseException as unused:  # pylint: disable=broad-exception-caught
        stat = 1
        Base.log("E", "程序异常退出", "MainThread")
        Base.log("E", traceback.format_exc(), "MainThread")
    Base.log("I", f"程序结束，返回值：{stat}", "MainThread")
    Base.log("I", "等待自动保存...", "MainThread")
    loop = QEventLoop()
    timer = QTimer()
    def _check_if_finished():
        if not widget.auto_saving:
            loop.quit()
            timer.stop()
    timer.timeout.connect(_check_if_finished)
    timer.start(33)
    loop.exec()
    Base.log("I", "自动保存完成，趋势", "MainThread")
    return stat


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
