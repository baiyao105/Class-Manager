"""
数据集有关的模型。
"""
from __future__ import annotations

import os
import time
import traceback
from typing import Literal

from utils.basetypes import Base
from utils.algorithm import Thread
from utils.classobjects import ClassDataSet, Student, OptExcInfo, DayRecord, UserDataBase, AttendanceInfo
from utils.classobjects.dataloaders import Chunk
from utils.functions import question_yes_no, wait_until
from utils.qtconfig import InfoBarIcon, QMessageBox, Qt, QFileDialog


from widgets import LoadingScreenWidget, AttendanceInfoWidget

from .logic import LogicModel
from .basic_ui import BasicUIModel


class DataSetModel(BasicUIModel, ClassDataSet, LogicModel):
    """
    数据集模型。
    """

    def __init__(
        self,
        current_user: str,
        class_name: str,
        class_key: str,
        save_path: str | None = None
    ):
        """
        初始化。
        
        :param current_user: 当前用户
        :param class_name: 班级名称
        :param class_key: 班级的id

        """
        Base.log("D", "初始化数据集模型", "DataSetModel.__init__")
        BasicUIModel.__init__(self)
        LogicModel.__init__(self, user=current_user)
        ClassDataSet.__init__(self, user=current_user, save_path=save_path)
        self.init_class_data(
            class_name=class_name,
            class_id=class_key,
            current_user=current_user,
            class_obs_tps=10,
            achievement_obs_tps=10,
        )
        self.setup_observer_overload_handler()
        self.setup_achievement_displayer()
        self.attendance_window: AttendanceInfoWidget | None = None


    def setup_observer_overload_handler(self):
        # 给成就侦测器过载的时候增加一个提示（覆写原来的on_observer_overloaded）
        assert self.achievement_obs is not None, \
            "按道理来说init_class_data之后应该已经设置了侦测器，为什么会是None?"
        orig_func = self.achievement_obs.on_observer_overloaded
        last_tip = 0.0

        def on_achievement_obs_overloaded(
            last_fr_time: float, 
            last_op_time: float, 
            cur_mspt: float
        ):
            "当成就侦测器过载时执行的操作"
            nonlocal last_tip
            if time.time() - last_tip >= 30:
                self.show_tip(
                    "警告",
                    "成就侦测器过载，已降低侦测速度",
                    self,
                    duration=8000,
                    icon=InfoBarIcon.WARNING,
                    further_info=f"详细信息：\n\n帧耗时：{last_fr_time}s\n操作耗时："
                    f"{last_op_time}s\n帧耗时：{cur_mspt}ms",
                )
                last_tip = time.time()
            orig_func(last_fr_time, last_op_time, cur_mspt)

        self.achievement_obs.on_observer_overloaded = on_achievement_obs_overloaded

    def on_auto_save_failure(self, exc_info: OptExcInfo):
        "处理自动保存失败的情况"
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


    def setup_achievement_displayer(self):
        assert self.achievement_obs is not None, \
            "按道理来说init_class_data之后应该已经设置了侦测器，为什么会是None?"
        self.achievement_obs.achievement_displayer = self.display_achievement

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


    def retract_lastest(self):
        """
        撤回上步，覆写的是ClassDataSet.retract_lastest。
        """
        assert self.class_obs is not None, \
            "按道理来说init_class_data之后应该已经设置了侦测器，为什么会是None?"
        
        if self.class_obs.opreation_record.size() == 0:
            Base.log("I", "暂无可以撤回的操作", "DataSetModel.retract_last")
            QMessageBox.information(self, "提示", "暂无可以撤回的操作")
            return False, "没有操作需要撤回"
        
        Base.log("I", "询问是否撤销上一次操作", "DataSetModel.retract_last")
        if question_yes_no(
            self,
            "提示",
            f'是否撤销上一次操作？'
            f'（共计{len(self.class_obs.opreation_record.peek())}条，'
            f'包含"{self.class_obs.opreation_record.peek()[0].title}"等点评）',
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
            
            return result, reason
        return False, "用户取消了操作"
    
    def reset_scores(self):
        """
        重置，覆写的是ClassDataSet.reset
        """
        Base.log("I", "询问是否重置", "DataSetModel.reset")
        if question_yes_no(self, "提示", "是否进行周结算？"):
            assert self.achievement_obs is not None, "成就侦测器未初始化，无法重置分数"
            loading_widget = LoadingScreenWidget(self, "indeterminate", stage_desc="重置分数中...")
            # 这个不能关掉
            loading_widget.setWindowFlag(loading_widget.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
            finished = False
            self.achievement_obs.stop()
            def _task():
                nonlocal finished
                self.reset_score_data()
                finished = True
            Thread(target=_task, name="ResetScoreThread").start()
            loading_widget.show()
            wait_until(lambda: finished)
            self.achievement_obs.start()
            loading_widget.close()

    def config_data(
        self,
        path: str | None = None, 
        silent: bool = False,
        strict: bool = False,
        reset_missing: bool = False,
        mode: Literal["sqlite", "pickle", "auto"] = "sqlite",
        load_full_histories: bool = False,
        reset_current: bool = True,
    ) -> UserDataBase:
        "加载数据并设置"
        self.load_succeed = False
        Base.log("I", "加载数据并设置", "DataSetModel.config_data")
        d = super().config_data(
            path or os.path.join("chunks", self.current_user),
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
            Base.log("I", "数据加载成功", "RecoverModel.config_data")
        else:
            self.show_tip(
                "警告", "数据加载失败", self, duration=5000, icon=InfoBarIcon.WARNING
            )
            Base.log("E", "数据加载失败", "RecoverModel.config_data")
        return d
    
    def day_end(self, weekday: int, utc: float, show_msgbox: bool = True):
        """
        每日结算

        :param weekday: 星期几
        :param utc: UTC时间
        """
        assert self.target_class is not None, "未设置目标班级就尝试每日结算"
        if self.target_class_id not in self.weekday_record:
            self.weekday_record[self.target_class_id] = {}
        if len(self.weekday_record[self.target_class_id]):
            if any([utc <= day.utc for day in self.weekday_record[self.target_class_id].values()]):  # 时间倒流了？？
                self.information(
                    "提示",
                    "时间倒流了？给我干哪天来了？\n\n"
                    f"（结算时间：{utc:.1f}, 历史记录记录到了"
                    f"{max([day.utc for day in self.weekday_record[self.target_class_id].values()]):.1f}）\n"
                    "（如果这是你第一次使用本程序，那么请忽略此提示）",
                )

        Base.log("I", "准备每日结算", "RecoverModel.day_end")
        yesterday = DayRecord(
            self.target_class, weekday, utc, self.current_day_attendance[self.target_class_id]
        )
        if self.target_class_id not in self.weekday_record:
            self.weekday_record[self.target_class_id] = {}
        self.weekday_record[self.target_class_id][yesterday.utc] = yesterday
        self.current_day_attendance[self.target_class_id] = AttendanceInfo(
            self.target_class_id, [], [], [], [], [], []
        )
        try:
            if self.attendance_window:
                self.attendance_window.close()
        except Exception:  # pylint: disable=broad-exception-caught
            Base.log_exc("在尝试关闭未关闭的考勤窗口时发生了错误", "RecoverModel.day_end")
        if show_msgbox:
            self.information(
                "提示",
                f"{time.strftime('%Y年%m月%d日（%A）', time.localtime(utc))} 结束了！\n"
                f"考勤系统已经重置，今天又是没好的一天！\n"
                f"\n"
                f"（今天的日期：{time.strftime('%Y年%m月%d日，%A')}",
            )

    def save(self):
        "保存当前存档。"
        if self.last_save_from_action - time.time() < -3:
            Chunk.reset_progress()
            Chunk.update_progress(
                stage="保存存档",
                obj_name="存档",
                current=1,
                total=1,
                percentage=0,
            )
            loading_screen = LoadingScreenWidget(
                self,
                progress_condition=lambda: Chunk.get_progress().total_percentage,
                stage_desc_condition=lambda: Chunk.get_progress().history_stage,
                stage_progress_desc_condition=lambda: (
                    "保存" +
                    Chunk.get_progress().current_saving_obj_name + 
                    "（" +
                    str(Chunk.get_progress().current_saving_obj_current) +
                    "/" +
                    str(Chunk.get_progress().current_saving_obj_total) +
                    "）"
                ))
            loading_screen.show()
            finished = False
            def _set_finished():
                nonlocal finished
                finished = True
            Base.log("I", "保存当前存档", "DataSetModel.save")
            self.last_save_from_action = time.time()
            Thread(
                target=lambda: (
                    self.save_current_settings(),
                    self.save_data(self.save_path),
                    self.show_tip(
                        "提示",
                        "保存成功",
                        icon=InfoBarIcon.SUCCESS,
                        duration=2500,
                        further_info="保存成功，没什么好说的",
                    ),
                    Base.log("I", "存档保存完成", "DataSetModel.save"),
                    _set_finished()
                ),
                name="SaveThread"
            ).start()
            wait_until(lambda: finished)
            loading_screen.close()

    def save_data_as(self):
        """
        将存档另存为数据目录。
        """
        path = QFileDialog.getExistingDirectory(
            self, "另存为", self.save_path,
        )
        if path and path.strip() != "":
            self.load_data(load_full_histories=True)
            self.save_data(path)

    def stop(self):
        ClassDataSet.stop(self)
        BasicUIModel.stop(self)
        


