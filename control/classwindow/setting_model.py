"""
和设置存储有关的模型。
"""

from __future__ import annotations
import os
import time
from typing import Literal, Any

from utils.update_check import CLIENT_VERSION_CODE
from utils.basetypes import Base
from utils.settings import SettingsInfo
from utils.update_check import CLIENT_VERSION

from utils.qtconfig import Slot


settings = SettingsInfo.get_global_settings()

class SettingModel:

    def __init__(self, current_user: str):
        """
        构造函数。
        
        :param current_user: 当前的用户名
        """

        self.create_time = time.time()
        "程序创建时间"
        self.framerate_update_time = 0
        "帧率上次更新时间"
        self.framecount = 0
        "自上一秒以来的更新帧数"
        self.framerate = 0
        "帧率"
        self.video_framecount = 0
        "动态背景帧数"
        self.video_framerate = 0
        "动态背景帧率"
        self.video_framerate_update_time = 0
        "动态背景帧数上次更新时间"
        self.displayed_on_the_log_window = 0
        "在小日志窗口上已经体现的日志条数，用来判断是否刷新"
        self.last_save_from_action = time.time()
        "上次手动保存的时间"
        self.auto_save_last_time = time.time()
        "上次自动保存的时间"

        self.opacity = 0.88
        "背景透明度"
        self.current_user = current_user
        "当前用户"
        # self.background_pixmap: Optional[QPixmap] = None
        # "背景图片"
        # self.lastest_pixmap_update_time: float = 0.0
        # "上次更新背景图片的时间"
        # self.window_info: ClassWindow.WindowInfo = ClassWindow.WindowInfo()
        # "窗口信息"
        # self.btns_anim_group: Optional[QParallelAnimationGroup] = QParallelAnimationGroup()
        # "按钮动画组"
        # self.running_btns_anim_group: Optional[QParallelAnimationGroup] = QParallelAnimationGroup()
        # "运行中的按钮动画组"
        # self.exit_action_finished: bool = False
        # "退出动作是否完成"
        # self.exit_tip: Optional[QLabel] = None
        # "退出时正在保存数据的提示"
        # self.capture: Optional[cv2.VideoCapture] = None
        # "动态背景的捕获对象"
        # self.current_video_frame: Optional[QImage] = None
        # "当前的动态背景视频帧"
        # self.tip_viewer_window: Optional[TipViewerWindow] = None
        # "提示查看窗口"
        # self.template_listbox: Optional[ListView] = None
        # "模板列表框"
        # self.manage_template_cursel_index: Optional[int] = None
        # "管理模板时选中的索引"
        # self.new_template_window: Optional[NewTemplateWidget] = None
        # "新建模板窗口"
        # self.history_detail_window: Optional[HistoryWidget] = None
        # "历史详情窗口"
        # self.multi_select_window: Optional[StudentSelectorWidget] = None
        # "多选学生窗口"
        # self.multi_select_template_window: Optional[SelectTemplateWidget] = None
        # "多选学生打开的模板窗口（以前不会写信号和槽弄的）"
        # self.setting_window: Optional[SettingWidget] = None
        # "设置窗口"
        # self.cleaning_sumup_window: Optional[CleaningScoreSumUpWidget] = None
        # "卫生分总结窗口"
        # self.group_info_window: Optional[GroupWidget] = None
        # "小组信息窗口"
        # self.icon: Optional[QIcon] = None
        # "窗口图标"
        # self.random_select_window: Optional[RandomSelectWidget] = None
        # "随机选择窗口"
        # self.homework_sumup_window: Optional[HomeworkScoreSumUpWidget] = None
        # "作业分总结窗口"
        # self.attendance_window: Optional[AttendanceInfoWidget] = None
        # "考勤窗口"
        # self.is_loading_all_history: bool = False
        # "是否正在加载所有历史记录"
        # self.listview_history_classes: Optional[ListView] = None
        # "历史记录查看的所有班级列表"
        # self.listview_history_class: Optional[ListView] = None
        # "历史记录查看的班级列表"
        # self.recovery_points: Optional[Dict[float, RecoveryPoint]] = None
        # "所有的恢复点"
        # self.about_window: Optional[AboutWidget] = None
        # "关于窗口"
        # self.debug_window: Optional[DebugWidget] = None
        # "调试窗口"
        # self.music_listview: Optional[ListView] = None
        # "音乐列表"
        # self.noise_detector: Optional[NoiseDetectorWidget] = None
        # "噪音检测窗口"
        # self.stu_buttons: Optional[Dict[int, ObjectButton]] = {}
        # "学生按钮列表"
        # self.grp_buttons: Optional[Dict[str, ObjectButton]] = {}
        # "小组按钮列表"
        Base.log("I", "程序创建", "SettingsModel.__init__")


        # self.app = app
        # "应用程序对象"
        # if qt_version in ("PySide6", "PyQt6"):
        #     self.app.setStyle(QStyleFactory.create(app_style))
        #     self.app.setStyleSheet(app_stylesheet)
        # self.save_path = f"chunks/{current_user}/"  # 可能在加载过之后变更
        # "存档路径"
        # self.backup_path = "backups/"
        # "备份路径"
        # super().__init__(user=current_user)

        # 初始化设置信息
        self.client_version = CLIENT_VERSION
        "客户端版本号"
        self.client_version_code = CLIENT_VERSION_CODE
        "客户端版本号"
        self.opacity: float = 0.88
        "窗口透明度"
        self.score_up_color_mixin_begin: tuple[int, int, int] = (0xCA, 0xFF, 0xCA)
        "加分动画颜色渐变开始颜色"
        self.score_up_color_mixin_end: tuple[int, int, int] = (0x33, 0xCF, 0x6C)
        "加分动画颜色渐变结束颜色"
        self.score_up_color_mixin_start: float = 2
        "加分动画颜色渐变开始值（分）"
        self.score_up_color_mixin_step: float = 15
        "加分动画颜色渐变开始值（分）"
        self.score_up_flash_framelength_base: int = 300
        "加分动画基础持续时间（毫秒）"
        self.score_up_flash_framelength_step: int = 100
        "加分动画每多加一分增加动画时间（毫秒）"
        self.score_up_flash_framelength_max: int = 2000
        "加分动画基础持续时间（毫秒）"

        self.score_down_color_mixin_begin: tuple[int, int, int] = (0xFC, 0xB5, 0xB5)
        "扣分动画颜色渐变开始颜色"
        self.score_down_color_mixin_end: tuple[int, int, int] = (0xA9, 0x00, 0x00)
        "扣分动画颜色渐变结束颜色"
        self.score_down_color_mixin_start: float = 2
        "扣分动画颜色渐变开始值（分）"
        self.score_down_color_mixin_step: float = 15
        "扣分动画颜色渐变总步长（分）"
        self.score_down_flash_framelength_base: int = 300
        "扣分动画基础持续时间（毫秒）"
        self.score_down_flash_framelength_step: int = 100
        "扣分动画每多扣一分增加动画时间（毫秒）"
        self.score_down_flash_framelength_max: int = 2000
        "扣分动画最长持续时间（毫秒）"
        self.log_keep_linecount: int = 100
        "日志窗口保留行数"
        self.log_update_interval: float = 0.1
        "日志窗口更新间隔（秒）"
        self.auto_save_enabled: bool = False
        "是否启用自动保存"
        self.auto_save_interval: float = 120
        "自动保存间隔（秒）"
        self.auto_save_path: Literal["folder", "user"] = "folder"
        "自动保存路径"
        self.auto_backup_scheme: Literal["none", "only_data", "all"] = "only_data"
        "自动备份方案"
        self.animation_speed: float = 1.0
        "动画速度"
        self.subwindow_x_offset: int = 0
        "子窗口x偏移量"
        self.subwindow_y_offset: int = 0
        "子窗口y偏移量"
        self.use_animate_background: bool = False
        "是否使用动态背景"
        self.max_framerate: int = 60
        "动态背景最大帧率"
        # self.saving = False
        # "正在保存"
        self.load_settings()
        # self.init_class_data(
        #     class_name=class_name,
        #     class_id=class_key,
        #     current_user=current_user,
        #     class_obs_tps=10,
        #     achievement_obs_tps=10,
        # )

        # # 给成就侦测器过载的时候增加一个提示（覆写原来的on_observer_overloaded）
        # orig_func = self.achievement_obs.on_observer_overloaded
        # last_tip = 0.0

        # def on_achievement_obs_overloaded(fr, op, mspt):
        #     "当成就侦测器过载时执行的操作"
        #     nonlocal last_tip
        #     if time.time() - last_tip >= 30:
        #         self.show_tip(
        #             "警告",
        #             "成就侦测器过载，已降低侦测速度",
        #             self,
        #             duration=8000,
        #             icon=InfoBarIcon.WARNING,
        #             further_info=f"详细信息：\n\n帧耗时：{fr}s\n操作耗时：{op}s\n帧耗时：{mspt}ms",
        #         )
        #         last_tip = time.time()
        #     orig_func(fr, op, mspt)

        # self.achievement_obs.on_observer_overloaded = on_achievement_obs_overloaded

        # self.signal_stu_list_update.connect(self._grid_buttons)
        # self.setup()
        # self.achievement_obs.achievement_displayer = self.display_achievement
        # self.is_running = True
        # "窗口是否在运行"
        # self.updator_thread = UpdateThread(main_window=self)
        # "更新线程"
        # self.command_list = command_list
        # self.action.triggered.connect(self.student_rank)
        # self.action_2.triggered.connect(self.manage_templates)
        # self.action_3.triggered.connect(self.open_setting_window)
        # self.action_5.triggered.connect(self.scoring_select)
        # self.action_7.triggered.connect(self.retract_lastest)
        # self.action_8.triggered.connect(lambda: self.tabWidget_2.setCurrentIndex(1))
        # self.action_9.triggered.connect(lambda: self.tabWidget_2.setCurrentIndex(0))
        # self.action_10.triggered.connect(self.save)
        # self.action_12.triggered.connect(self.reset_scores)
        # self.action_13.triggered.connect(self.show_all_history)
        # self.action_14.triggered.connect(self.save_data_as)
        # self.action_15.triggered.connect(self.music_selector)
        # self.action_16.triggered.connect(self.show_recover_points)
        # self.action_17.triggered.connect(self.create_recover_point)
        # self.action_18.triggered.connect(self.cleaning_score_sum_up)
        # self.action_19.triggered.connect(self.show_attendance)
        # self.action_20.triggered.connect(self.show_noise_detector)
        # self.action_21.triggered.connect(self.random_select)
        # self.action_22.triggered.connect(self.homework_score_sum_up)
        # self.action_23.triggered.connect(self.about_this)
        # self.action_24.triggered.connect(self.show_update_log)
        # self.action_25.triggered.connect(
        #     lambda: Thread(
        #         target=lambda: self.updator_thread.detect_new_version(False)
        #     ).start()
        # )
        # self.action_26.triggered.connect(self.refresh_window)
        # self.action_28.triggered.connect(self.show_debug_window)
        # self.actionNew_Template.triggered.connect(
        #     self.new_template
        # )  # 笑死唯一一个不是默认名字的action控件
        # self.signal_show_new_tip.connect(lambda tip: tip.show())
        # self.selected_quick_command: List[Optional[Command]] = [
        #     [c for c in self.command_list if c.key == "new_template"][0],
        #     [c for c in self.command_list if c.key == "manage_templates"][0],
        #     [c for c in self.command_list if c.key == "show_all_history"][0],
        #     [c for c in self.command_list if c.key == "scoring_select"][0],
        #     [c for c in self.command_list if c.key == "homework_score_sum_up"][0],
        #     [c for c in self.command_list if c.key == "cleaning_score_sum_up"][0],
        #     [c for c in self.command_list if c.key == "show_attendance"][0],
        #     [c for c in self.command_list if c.key == "detect_new_version"][0],
        #     [c for c in self.command_list if c.key == "show_update_log"][0],
        # ]
        # self.fast_command_edit_state = False
        # self.refresh_quick_command_btns()
        # self.HyperlinkLabel.clicked.connect(self.edit_fast_command_btns)
        # self.CardWidget.clicked.connect(self.show_attendance)
        # self.pushButton_3.clicked.connect(self.about_this)
        # self.pushButton_4.clicked.connect(self.open_setting_window)
        # try:
        #     self.load_quick_settings_from_list(
        #         pickle.load(
        #             open(
        #                 os.getcwd()
        #                 + os.sep
        #                 + f"chunks/{self.current_user}/quick_commands.pkl",
        #                 "rb",
        #             )
        #         )
        #     )
        # except FileNotFoundError:
        #     Base.log("W", "未找到快速命令文件，重置为默认", "SettingsModel.load_settings")
        # self.listWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # self.listWidget.doubleClicked.connect(self.click_opreation)
        # self.signal_tip_update.connect(lambda args: self._show_tip(*args))
        # self.signal_button_update.connect(self.btn_anim)
        # self.signal_log_window_refresh.connect(self._refresh_logwindow)
        # self.pushButton.clicked.connect(self.dont_click)
        # self.listView_data: List[Callable] = []
        # "ListView数据，用于存储主窗口侧边ListView里面的命令（对应里面的每一项）"
        # self.lastest_listview: Optional[ListView] = None
        # "最近一次用self.list_view()开启的ListView"
        # self.textBrowser.setReadOnly(True)
        # self.textBrowser.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        # self.setFixedSize(self.width(), self.height())
        # Base.log("I", f"设置透明度为{self.opacity}", "SettingsModel.__init__")
        # self.listWidget.setHorizontalScrollBarPolicy(
        #     Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        # )
        # self.insert_queue = Queue()
        # "在主窗口右侧ListWidget插入项的队列"
        # self.logger_queue = Queue()
        # "要插入到主窗口日志的队列"
        # self.signal_log_update.connect(self.logwindow_add_newline)
        # self.signal_log_update.emit("这里是日志")
        # self.signal_show_info.connect(lambda args: self._information(*args))
        # self.signal_show_warning.connect(lambda args: self._warning(*args))
        # self.signal_show_error.connect(lambda args: self._critical(*args))
        # self.signal_show_question.connect(lambda args: self._question_if_exec(*args))
        # self.signal_exiting.connect(self.on_exit)
        # self.signal_dont_click_btn_clicked.connect(self._dont_click)
        # self.signal_refresh_hint_widget.connect(self._refresh_hint_widget)
        # self.signal_anim_group_state_changed.connect(self._anim_group_state_changed)
        # self.tip_handler = self.TipHandler(self)
        # "提示处理器"
        # self.tip_handler.start()
        # self.logwindow_content: List[str] = ["这里是日志"]
        # "主窗口日志内容"
        # self.auto_saving = False
        # "是否正在自动保存"
        # self.setWindowTitle(f"班寄管理 - {self.target_class.name}")
        # self.terminal_locals = {}
        # "终端的本地变量"
        # self.update_timer = QTimer(self)
        # "更新定时器"
        # self.update_timer.timeout.connect(self.update)
        # self.update_timer.start(100)
        # self.recent_command_update_timer = QTimer(self)
        # "最近命令更新定时器"
        # self.recent_command_update_timer.timeout.connect(
        #     self.update_recent_command_btns
        # )
        # self.recent_command_update_timer.start(300)
        # self.tip_history: List[SideNotice] = []
        # "提示历史"
        # self.show_tip(
        #     "", "双击项目查看消息记录", duration=0, further_info="孩子真聪明（bushi"
        # )
        # self.ListWidget.itemDoubleClicked.connect(self.view_tip_hisory)
        # self.ListWidget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # self.student_info_window: Optional[StudentWidget] = None
        # "学生信息窗口"
        # self.CardWidget_2.clicked.connect(
        #     lambda: Thread(target=self.refresh_hint_widget).start()
        # )
        # PromptUtils.send_notice = lambda title, content, msg_type: (
        #     self.show_tip(
        #         title,
        #         content,
        #         (
        #             InfoBarIcon.INFORMATION
        #             if msg_type == "info"
        #             else (
        #                 InfoBarIcon.WARNING
        #                 if msg_type == "warn"
        #                 else (
        #                     InfoBarIcon.ERROR
        #                     if msg_type == "error"
        #                     else InfoBarIcon.SUCCESS
        #                 )
        #             )
        #         ),
        #     )
        # )

        # self.exception_window: Optional[ExceptionHandler] = None

        # set_show_exc_window_callback(lambda excinfo: self.show_exception(excinfo[1]))

        # if self.auto_save_enabled:
        #     Thread(
        #         target=lambda: self.auto_save(timeout=int(self.auto_save_interval)),
        #         name="AutoSave",
        #         daemon=True,
        #     ).start()
        # Thread(
        #     target=self.insert_action_history_info_while_alive,
        #     name="InsertOpreationHandler",
        #     daemon=True,
        # ).start()
        # Thread(
        #     target=self.read_video_while_alive, daemon=True, name="VideoReader"
        # ).start()
        # Thread(
        #     target=self.refresh_logwindow_while_alive,
        #     daemon=True,
        #     name="RefreshLogWindow",
        # ).start()


    def save_settings(self):
        """
        保存当前的全局设置对象到设置存档文件。
        """
        Base.log("I", "保存设置到文件", "SettingsModel.save_settings")
        os.makedirs(os.path.abspath(f"chunks/{self.current_user}"), exist_ok=True)
        settings.save_to(
            os.path.abspath(f"chunks/{self.current_user}/settings.dat")
        )

    @Slot()
    def reset_settings(self):
        """
        重置全局设置，并将主窗口的设置重置为全局设置当前的默认值。
        """
        settings.reset_settings()
        version = self.client_version
        version_code = self.client_version_code
        self.set_settings(**settings.get_dict())
        self.set_settings(client_version_code=version_code, client_version=version)
        self.save_settings()

    def load_settings(self) -> SettingsInfo:
        """
        加载设置存档文件到全局设置对象后应用在主窗口。
        """
        Base.log("I", "从文件中加载设置", "SettingsModel.load_settings")
        settings.load_from(
            os.path.abspath(f"chunks/{self.current_user}/settings.dat")
        )
        self.set_settings(**settings.get_dict())
        return settings

    def set_settings(self, **kwargs: Any):
        """
        依照kwargs设置全局设置对象和主窗口的设置信息并保存当前设置到文件。
        
        （调用save_settings）
        """
        Base.log("I", "设置设置信息", "SettingsModel.set_settings")
        for key, value in kwargs.items():
            if settings.get(key) != kwargs[key]:
                Base.log(
                    "I",
                    f"{key} 变更： "
                    f"{settings.get(key)} "
                    f"-> {repr(getattr(self, key, None))} (self) "
                    f"/ {repr(kwargs[key])} (kwargs)",
                    "SettingsModel.set_settings",
                )
            setattr(self, key, value)
            setattr(settings, key, value)
        self.save_settings()

    def save_current_settings(self):
        """
        保存此窗口当前的设置到全局设置对象并保存设置。
        """
        Base.log("I", "保存当前设置", "SettingsModel.save_settings")
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