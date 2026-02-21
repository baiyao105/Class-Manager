"""
更新控件有关的模型。
"""

from __future__ import annotations

import enum
import os
import sys
import time
import traceback
import threading
from typing import Tuple, TypeAlias

import psutil

from utils.algorithm import Thread
from utils.basetypes import Base
from utils.functions.sounds import play_sound
from utils.qtconfig import (
    QPushButton, Signal, Slot, QTimer, 
    QRect, QThread, QWidget, InfoBarIcon, QPixmap,
    QParallelAnimationGroup
)


from utils.update_check import (
    CLIENT_UPDATE_LOG, CLIENT_VERSION, 
    CLIENT_VERSION_CODE, CORE_VERSION, 
    CORE_VERSION_CODE
)
from widgets.basic import ObjectButton

from .object_info_model import ObjectInfoModel

FlashArgType: TypeAlias = Tuple[Tuple[int, int, int], Tuple[int, int, int], int]

class UpdateWidgetModel(ObjectInfoModel):
    """
    更新控件有关的模型。
    """

    signal_button_anim = Signal(ObjectButton, tuple)
    """
    按钮状态更新信号，用于控制按钮闪烁效果（这个应该是吃性能最多的信号了）
    """

    signal_grid_buttons = Signal()
    """
    学生列表按钮更新信号
    """

    signal_anim_group_state_changed = Signal(int)
    """
    动画组状态改变信号
    """

    def __init__(
            self, 
            current_user: str, 
            class_name: str, 
            class_key: str, 
            save_path: str | None = None
        ):
        Base.log("D", "初始化UpdateWidgetModel", "UpdateWidgetModel.__init__")
        
        self.stu_buttons: dict[int, ObjectButton] = {}
        "学生按钮列表"
        self.grp_buttons: dict[str, ObjectButton] = {}
        "小组按钮列表"
        self.btns_anim_group: QParallelAnimationGroup | None = QParallelAnimationGroup()
        "按钮动画组"
        self.running_btns_anim_group: QParallelAnimationGroup = QParallelAnimationGroup()
        "运行中的按钮动画组"
        self.updator_thread: UpdateThread = UpdateThread(self)
        self.update_label_timer = QTimer(self)
        self.update_label_timer.timeout.connect(self.update_labels)
        self.update_label_timer.start(50)
        self.signal_button_anim.connect(self.slot_button_anim)
        self.signal_grid_buttons.connect(self.slot_grid_buttons)
        self.signal_anim_group_state_changed.connect(self.slot_anim_group_state_changed)
        self.grid_buttons()
        self.updator_thread.start()

    def grid_buttons(self):
        """
        显示所有学生按钮（虽然不算真正意义上的grid）
        """
        self.signal_grid_buttons.emit()

    Slot()
    def slot_grid_buttons(self):
        """
        grid_buttons的接口，不要用Thread调用，不然会炸
        """
        assert self.target_class is not None, "在还没有设置班级的时候就尝试更新了按钮"
        Base.log("I", "准备显示按钮", "UpdateWidgetModel.grid_buttons")
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
            if grp.belongs_to == self.target_class_id:
                self.grp_buttons[key] = ObjectButton(
                    f"{grp.name}\n{grp.total_score}分", self, object=grp
                )
                self.grp_buttons[key].setObjectName("GroupButton" + str(grp.key))
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
        
    Slot()
    def slot_anim_group_state_changed(self, state: int):
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
        
    Slot()
    def update_labels(self):
        "更新界面"
        t = time.time()
        self.label_2.setText(self.target_class.name if self.target_class else "未选择班级")
        self.label_3.setText(str(len(self.target_class.students) if self.target_class else "未选择班级"))
        self.label_4.setText(self.target_class.owner if self.target_class else "未选择班级")
        self.label_5.setText(f"{self.target_class.student_avg_score:.2f}" if self.target_class else "未选择班级")
        self.label_6.setText(
            str(max(*[float(self.target_class.students[num].score)for num in self.target_class.students]))
            + "/"
            + str(min(*[float(self.target_class.students[num].score) for num in self.target_class.students]))
            if self.target_class
            else "未选择班级"
        )
        self.label_7.setText(f"{self.framerate}fps; {self.video_framerate}fps")
        self.label_8.setText(f"{time.time() - self.create_time:.3f} s")
        self.label_9.setText(f"{threading.active_count()}")
        self.label_10.setText(
            str(round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 1)) + " MB"
        )
        self.label_11.setText(
            (f"{self.class_obs.tps:.2f}/"
             f"{self.class_obs.limited_tps}tps;"
             f" {str(round(self.achievement_obs.tps, 2)).rjust(5)}/"
             f"{self.achievement_obs.limited_tps}tps")
            if self.achievement_obs and self.class_obs
            else "没有加载侦测器"
        )
        self.BodyLabel_2.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        self.BodyLabel.setText("{}好，欢迎回来".format(self.get_day_period_name(time.time())))
            
        t2 = time.time()
        super().update()
        t3 = time.time()
        v = self.window_info.video.last_update_event
        v.widget_updating = t2 - t
        v.super = t3 - t2
        v.total_time = t3 - t

    def get_day_period_name(self, timestamp: float):
        lt = time.localtime(timestamp)
        hour = lt.tm_hour
        if hour in range(5, 9+1):
            return "早上"
        elif hour in range(9, 12+1):
            return "上午"
        elif hour in range(12, 14+1):
            return "中午"
        elif hour in range(14, 18+1):
            return "下午"
        else:
            return "晚上"

    @Slot(QPushButton, tuple)
    def slot_button_anim(self, obj: ObjectButton, args: FlashArgType):
        """
        使按钮进行一次闪烁动画。
        """
        # self.btns_anim_group.addAnimation(obj.get_flash_anim(*args, from_self=False))
        obj.flash(*args)

    
    def show_update_log(self):
        "展示更新日志"
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
                    else "貌似没写更新日志...\n（这种一般都是例行维护）\n\n\n"
                )
                + (
                    '\n\n在顶边栏的"其他"中可以再次查看更新日志。'
                    if self.client_version_code < CLIENT_VERSION_CODE
                    else ""
                )
            ).strip(),
        )

    def refresh_window(self):
        "刷新窗口"
        Base.log("I", "刷新窗口", "UpdateWidgetModel.refresh_window")
        self.updator_thread.terminate()
        self.updator_thread.deleteLater()
        self.updator_thread = UpdateThread(self, self)
        self.updator_thread.start()

    def detect_new_version(self):
        "检测新版本"
        Base.log("I", "检测新版本", "UpdateWidgetModel.detect_new_version")
        Thread(target=self.updator_thread.detect_new_version).start()

    def stop(self):
        super().stop()
        self.updator_thread.requestInterruption()
        if not self.updator_thread.wait(1000):
            self.updator_thread.terminate()
        self.update_label_timer.stop()

class UpdateThread(QThread):
    """更新线程，更新主界面的按钮什么之类的东西"""

    first_loop = True
    "是否是第一次循环"

    def __init__(
        self, 
        model: UpdateWidgetModel,
        parent: QWidget | None = None
    ):
        "初始化"
        super().__init__(parent=parent)
        Base.log("I", "更新线程初始化完成", "UpdateThread.__init__")
        self.model = model
        self.running = True
        self.stopped = False
        self.last_day_time = 0
        self.button_shown = False
        assert self.model.target_class is not None, "更新线程在还没有设置目标班级的时候被初始化了"
        self.target_class = self.model.target_class
        self.button_state_last_change = time.time()
        self.last_student_list = list(self.model.target_class.students)
        self.last_group_list = list(self.model.target_class.groups)
        self.lastest_score: dict[int, float] = {}
        self.lastest_grp_score: dict[str, float] = {}

    def calc_start_color(self, delta: float):
        if delta == 0:
            return (255, 255, 255)
        begin = (self.model.score_up_color_mixin_begin if delta > 0 
                else self.model.score_down_color_mixin_begin)
        end = (self.model.score_up_color_mixin_end if delta > 0 
                else self.model.score_down_color_mixin_end)
        step = (self.model.score_up_color_mixin_step if delta > 0 
                else self.model.score_down_color_mixin_step)
        mixin_start = (self.model.score_up_color_mixin_start if delta > 0 
                else self.model.score_down_color_mixin_start)
        delta = abs(delta)
        r = int(
                min(begin[0],
                    max(
                        end[0],
                        begin[0] - max(delta - mixin_start, 0) * ((begin[0] - end[0]) / step)
                    )
                )
            )
        g = int(
                min(begin[1],
                    max(
                        end[1],
                        begin[1] - max(delta - mixin_start, 0) * ((begin[1] - end[1]) / step)
                    )
                )
            )
        b = int(
                min(
                    begin[2],
                    max(
                        end[2],
                        begin[2] - max(delta - mixin_start, 0) * ((begin[2] - end[2]) / step)
                    )
                )
            )
        return (r, g, b)

    def calc_duration(self, delta: float):
        delta = abs(delta)
        return min(
            self.model.score_up_flash_framelength_max,
            int(
                delta * self.model.score_up_flash_framelength_step
                + self.model.score_up_flash_framelength_base
            ),
        )
    
    def update_stu_btns(self):
        "更新主窗口的学生按钮"
        if self.last_student_list != list(self.target_class.students):
            Base.log("I", "学生列表变动, 准备更新", "UpdateThread.run")
            self.last_student_list = list(self.target_class.students)
            self.lastest_score = dict.fromkeys(self.target_class.students.keys(), 0)
            self.model.grid_buttons()
            Base.log("I", "学生列表更新完成", "UpdateThread.run")

        for num, stu in self.target_class.students.items():
            self.model.stu_buttons[num].setText(
                f"{stu.num}号 {stu.name}\n{stu.score}分"
            )
            diff = float(stu.score - self.lastest_score[stu.num])
            if diff != 0:
                self.model.signal_button_anim.emit(
                    self.model.stu_buttons[num],
                    (self.calc_start_color(diff),
                    (255, 255, 255),
                    self.calc_duration(diff))
                )
            self.lastest_score[stu.num] = stu.score
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
            time.sleep(0.002)

    def update_grp_btns(self):
        "更新主界面的小组按钮"
        if self.last_group_list != list(self.target_class.groups):
            Base.log("I", "小组列表变动, 准备更新", "UpdateThread.run")
            self.last_group_list = list(self.target_class.groups)
            self.lastest_grp_score = dict.fromkeys(self.target_class.groups.keys(), 0)
            self.model.grid_buttons()
            Base.log("I", "小组列表更新完成", "UpdateThread.run")

        for key, grp in self.target_class.groups.items():
            self.model.grp_buttons[key].setText(
                f"{grp.name}\n\n总分 {grp.total_score:.1f}分\n"
                f"平均 {grp.average_score:.2f}分\n"
                f"去最低平均 {grp.average_score_without_lowest:.2f}分"
            )
            diff = float(grp.total_score - self.lastest_grp_score[key])
            if diff != 0:
                self.model.signal_button_anim.emit(
                    self.model.grp_buttons[key],
                    (self.calc_start_color(diff),
                    (255, 255, 255),
                    self.calc_duration(diff))
                )
            self.lastest_grp_score[key] = grp.total_score

    def detect_update(self):
        "检测是否有更新过"
        if self.model.client_version_code < CLIENT_VERSION_CODE:
            play_sound("audio/sounds/orb.ogg")
            self.model.show_update_log()
            self.model.client_version_code = CLIENT_VERSION_CODE
            self.model.client_version = CLIENT_VERSION
            self.model.save_current_settings()

    def detect_new_version(self):
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
            assert isinstance(info, BaseException), "出错的时候按道理来说应该返回Exception对象的"
            Base.log_exc(
                "检测更新出现错误", "UpdateThread.detect_new_version", exc=info
            )
            self.model.show_tip(
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
            assert isinstance(info, dict), "返回结果应该是字典"
            self.model.show_tip("提示", "发现新版本！", duration=5000)

            def update_self(self: UpdateThread):

                self.model.show_tip("提示", "正在下载更新...", duration=5000)

                def _update(self: UpdateThread):
                    try:
                        get_update_zip()
                        unzip_to_dir()
                        self.model.information(
                            "更新下载完成",
                            "10秒之后将会重启程序以完成更新。（按任意键关闭后开始计时）",
                        )
                        time.sleep(10)
                        self.model.save_data()
                        self.model.save_current_settings()
                        while self.model.auto_saving:
                            time.sleep(0.1)
                        update()

                    except (OSError, IOError) as e:
                        Base.log_exc("更新出现错误", "UpdateThread.update_self")
                        self.model.show_tip(
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
                self.model.question_if_exec(
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
                self.model.question_if_exec(
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
            self.model.show_tip("提示", "当前已是最新版本。", duration=5000)

        elif res == UpdateInfo.VERSION_IS_AHEAD:  # 版本号比服务器高，不过一般应该不会吧
            self.model.show_tip(
                "?",
                "你对版本号文件做什么了。。。",
                duration=5000,
                icon=InfoBarIcon.ERROR,
            )

    def detect_newday(self):
        "检测是否是新的一天"
        if time.localtime(
            self.model.last_start_time
        ).tm_wday != time.localtime().tm_wday or (  # 不是一周的同一天
            time.time() - self.model.last_start_time
            >= 86400  # 是一周的同一天旦超过一天
            and time.localtime(self.model.last_start_time).tm_wday
            == time.localtime().tm_wday
        ):

            # 没好的一天又开始力

            self.model.show_tip(
                "日期刷新",
                time.strftime(
                    "%Y年%m月%d日过去了，",
                    time.localtime(self.model.last_start_time),
                )
                + "新的一天开始了！",
                self.model,
                duration=6000,
                sound="audio/sounds/orb.ogg",
                icon=InfoBarIcon.INFORMATION,
            )

            self.model.day_end(
                time.localtime(self.model.last_start_time).tm_wday,
                self.model.last_start_time,
                time.time() - self.model.last_start_time <= 86400,
            )
            self.model.last_start_time += min(
                time.time() - self.model.last_start_time, 86400
            )

        else:
            self.model.last_start_time += min(
                time.time() - self.model.last_start_time, 86400
            )

    def run(self):
        "线程运行"
        Base.log("I", "更新线程开始运行", "UpdateThread.run")
        self.lastest_score = {stu.num: 0.0 for stu in self.target_class.students.values()}
        self.lastest_grp_score = {grp.key: 0.0 for grp in self.target_class.groups.values()}

        while not self.isInterruptionRequested():
            try:
                self.detect_newday()
                try:
                    self.update_stu_btns()
                    self.update_grp_btns()
                except IndexError as e:
                    Base.log_exc_short("疑似添加/减少学生，正在重新加载: ", "UpdateThread.run", "W", e)
                    self.model.grid_buttons()
                if self.first_loop:
                    Thread(target=self.detect_new_version).start()
                    Thread(target=self.detect_update).start()
                    self.first_loop = False
                self.model.signal_anim_group_state_changed.emit(self.model.AnimationGroupStatement.START)
                time.sleep(0.5)
                self.model.signal_anim_group_state_changed.emit(self.model.AnimationGroupStatement.CREATE_NEW)


            except Exception as exc:  # pylint: disable=broad-exception-caught
                self.model.handle_exception((exc.__class__, exc, exc.__traceback__))
