"""
和操作相关的模型。
"""

from __future__ import annotations
import os
from typing import Callable

from utils.basetypes import Base
from utils.classobjects import Student

from utils.functions.prompts import question_yes_no
from utils.functions.sounds import play_music, stop_music
from utils.qtconfig import InfoBarIcon, QWidget

from widgets import (SelectTemplateWidget, StudentSelectorWidget, 
                     CleaningScoreSumUpWidget, RandomSelectWidget,
                     HomeworkScoreSumUpWidget, NoiseDetectorWidget,
                     ListView, DebugWidget)
from widgets.custom.NoiseDetectorWidget import HAS_PYAUDIO

from .object_info_model import ObjectInfoModel


class OperationModel(ObjectInfoModel):
    """
    和用户操作相关的模型。
    """

    def __init__(
        self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化OperationModel", "OperationModel.__init__")

        self.multi_select_template_window: SelectTemplateWidget | None = None
        "多选学生的选择模板窗口"
        self.cleaning_sumup_window: CleaningScoreSumUpWidget | None = None
        "卫生分结算窗口"
        self.random_select_window: RandomSelectWidget | None = None
        "随机选择学生窗口"
        self.debug_window: DebugWidget | None = None
        "调试窗口"
        self.music_listview: ListView | None = None
        "音乐列表"
        self.music_path: str = os.path.join("audio", "music")
        "音乐文件路径"
        self.music_file_suffix: tuple[str, ...] = (".mp3", ".ogg", ".wav", ".flac", ".m4a", ".ape")
        "音乐文件后缀"


    def scoring_select(self, *, students: list[Student] | None = None):
        """
        多选学生并发送点评。
        """
        assert self.target_class is not None, "尝试在还没有选择目标班级的时候多选学生"
        if students is None:
            # 如果没有传入学生则默认为当前班级的所有学生
            students = list(self.target_class.students.values())
        self.multi_select_window = StudentSelectorWidget(self, self, students)
        self.multi_select_window.return_result.connect(self.send_to_students)
        self.multi_select_window.show()

    def send_to_students(self, students: list[Student]):
        """
        选择点评发给指定学生。
        """
        self.multi_select_template_window = SelectTemplateWidget(self, self)
        self.multi_select_template_window.show()
        def _on_return(selection: tuple[str, str, str, float]):
            self.send_modify(
                selection[0], students, selection[1], selection[2], selection[3]
            )
        self.multi_select_template_window.return_result.connect(_on_return)
        self.multi_select_template_window.select()

    def cleaning_score_sum_up(self):
        """
        打开卫生打扫分数结算窗口。
        """
        Base.log("I", "打开打扫分数结算窗口", "OperationModel.cleaning_sumup")
        self.cleaning_sumup_window = CleaningScoreSumUpWidget(dataset=self, master=self)
        self.cleaning_sumup_window.show()

    def random_select(self):
        """
        打开随机选择学生窗口。
        """
        Base.log("I", "打开随机选择学生窗口", "OperationModel.random_select")
        self.random_select_window = RandomSelectWidget(dataset=self, master=self)
        self.random_select_window.show()

    
    def homework_score_sum_up(self):
        """
        打开作业总分结算窗口。
        """
        assert self.target_class is not None, "尝试在没有设置目标班级的情况下打开作业总分结算窗口"
        Base.log("I", "打开作业总分结算窗口", "OperationModel.homework_sumup")
        self.homework_sumup_window = HomeworkScoreSumUpWidget(
            dataset=self,
            master=self,
            target_class=self.target_class,
            target_students=self.target_class.students,
        )
        self.homework_sumup_window.show()

    def show_noise_detector(self):
        """
        打开噪音检测器窗口。
        """
        if HAS_PYAUDIO:
            Base.log("I", "启动噪声检测器", "OperationModel.show_noise_detector")
            self.noise_detector = NoiseDetectorWidget(self, self)
            self.noise_detector.show()
        else:
            self.warning("提示", "没有找到pyaudio库，无法启动噪声检测器...")

    def show_debug_window(self):
        """
        显示调试窗口。
        """
        Base.log("I", "显示调试窗口", "OperationModel.show_debug_window")
        self.debug_window = DebugWidget(dataset=self, master=self)
        self.debug_window.show()
    

    def music_selector(self):
        """
        打开音乐选择器。
        """
        Base.log("I", "按钮被点击", "OperationModel.music_selector")
        music_list: list[tuple[str, Callable[[], None]]] = []
        for f in os.listdir(self.music_path):
            if f.endswith(self.music_file_suffix):
                def _play_music(f: str = f):
                    assert self.music_listview is not None, "不应该啊，点击了就应该有列表啊，怎么会是None呢？？"
                    play_music(os.path.join(self.music_path, f), volume=0.8, loop=2**31 - 1)
                    self.music_listview.close()
                    self.show_tip("提示", f"播放音乐：{f.rsplit('.', 1)[0]}")
                music_list.append((f.rsplit(".", 1)[0], _play_music))
        def _stop_music():
            assert self.music_listview is not None, "不应该啊，点击了就应该有列表啊，怎么会是None呢？？"
            stop_music()
            self.music_listview.close()
            self.show_tip("提示", "停止播放音乐")
        music_list.sort()
        music_list.append(("<停止播放>", _stop_music))

        if len(music_list) == 0:
            Base.log("W", "没有找到音乐文件", "OperationModel.music_selector")
            return
        Base.log("I", f"找到{len(music_list)}个音乐文件", "OperationModel.music_selector")
        Base.log("I", "正在选择音乐", "OperationModel.music_selector")
        self.music_listview = ListView("选择音乐", self, music_list)
        self.music_listview.show()


    def create_recover_point(self):
        """
        创建还原点。
        """
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


    def stop(self):
        widgets: list[QWidget | None] = [
            self.multi_select_template_window,
            self.cleaning_sumup_window,
            self.random_select_window,
            self.debug_window,
            self.music_listview,
        ]
        for widget in widgets:
            if widget is not None:
                widget.close()
        super().stop()
    