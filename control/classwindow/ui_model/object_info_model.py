"""
和对象信息相关的模型。
"""

from __future__ import annotations

import time
from typing import Iterable

from utils.basetypes import Base
from utils.functions import wait_until
from utils.algorithm import Thread
from utils.classobjects import Student, Group, Chunk, Class, ScoreModification
from utils.qtconfig import QWidget, QColor


from widgets import StudentWidget, GroupWidget, AttendanceInfoWidget, ListView, HistoryWidget
from widgets.custom.ListView import ListViewItemDataType
from .basic_models import RecoveryPoint


from .class_ui_model import MixinSuperType


class ObjectInfoModel(MixinSuperType):
    """
    和分数模板相关的模型。
    """

    def __init__(
        self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化ObjectInfoModel", "ObjectInfoModel.__init__")

        self.student_info_window: StudentWidget | None = None
        "学生信息窗口"
        self.group_info_window: GroupWidget | None = None
        "小组信息窗口"
        self.listview_history_classes: ListView | None = None
        "所有班级的历史记录列表"
        self.listview_history_class: ListView | None = None
        "单个班级的历史记录列表"
        self.is_loading_all_history: bool = False
        "是不是正在加载所有历史记录"
        self.history_detail_window: HistoryWidget | None = None
        "历史记录详情窗口"
        self.CardWidget.clicked.connect(self.show_attendance)



    def student_info(
        self, 
        student: Student, 
        master: QWidget | None = None, 
        readonly: bool = False
    ) -> None:
        """
        展示学生信息

        :param student: 学生
        """
        Base.log("I", f"打开学生信息窗口，学生名：{student.name}", "ObjectInfoModel.student_info")
        self.student_info_window = StudentWidget(
            dataset=self,
            student=student,
            master=master or self,
            readonly=readonly,
        )
        self.student_info_window.set_student(student)
        self.student_info_window.pushButton_3.setDisabled(readonly)
        self.student_info_window.show(readonly)

    def group_info(
        self,
        group: Group,
        master: QWidget | None = None,
        readonly: bool = False,
    ) -> None:
        """
        展示小组信息。

        :param group: 小组
        ::param master_widget: 父窗口
        :param readonly: 是否只读
        """
        Base.log("I", f"打开小组信息窗口，小组名：{group.name}", "ObjectInfoModel.group_info")
        self.group_info_window = GroupWidget(
            dataset=self, 
            master=master or self, 
            group=group, 
            readonly=readonly
        )
        self.group_info_window.show(readonly)

    def show_attendance(self, master: QWidget | None = None) -> None:
        """
        显示考勤。
        """
        self.attendance_window = AttendanceInfoWidget(
            dataset=self, 
            master=master or self, 
            attendanceinfo=self.current_day_attendance[self.target_class_id]
        )
        self.attendance_window.show()


    def show_all_history(self) -> None:
        """
        显示所有历史。
        """

        if self.is_loading_all_history:
            Base.log("I", "还正在加载历史记录", "ObjectInfoModel.show_all_history")
        
        finished = False

        def _load_history():
            nonlocal finished
            self.show_tip("提示", "正在保存当前数据以保证完整性", duration=2000)
            self.save_data()
            self.show_tip("提示", "历史记录正在加载中，请稍等", duration=2000)
            self.config_data(
                load_full_histories=True,
                reset_current=False,
                strict=True
            )
            finished = True

        self.is_loading_all_history = True
        Thread(target=_load_history, name="HistoryLoader").start()
        self.is_loading_all_history = False
        wait_until(lambda: finished)

        listview_data: list[ListViewItemDataType] = []
        for history in self.history_data.values():
            text =  f"位于{time.localtime(history.time).tm_year}/"  \
                    f"{time.localtime(history.time).tm_mon}/"       \
                    f"{time.localtime(history.time).tm_mday} "      \
                    f"{time.localtime(history.time).tm_hour}:"      \
                    f"{time.localtime(history.time).tm_min:02}:"    \
                    f"{time.localtime(history.time).tm_sec:02}的历史记录"
            func = lambda h=history: self.show_classes_history(h.classes) # type: ignore
            listview_data.append((text, func))

        view = ListView("所有历史记录", self, listview_data)

        def delete_earliest_record():
            nonlocal view
            def _confirm_deletion():
                nonlocal view
                uuid = list(self.history_data.values())[0].uuid
                assert uuid is not None, "怎么可能？？？历史记录列表中的UUID怎么会是None？？？"
                Chunk(self.save_path, None).del_history(uuid)
                self.history_data.pop(list(self.history_data)[0])
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
                )
                self.information("提示", "删除成功，请重新加载此窗口！")
                view.close()
            if len(self.history_data):
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
                    _confirm_deletion,
                )
            else:
                self.information("提示", "没有历史记录可以删除...")

        def delete_all_records():
            def _confirm_deletion():
                self.insert_action_history_info(
                    f"删除所有的历史记录（{len(self.history_data)}）",
                    self.show_all_history,
                    (142, 30, 114, 246, 139, 219),
                    4
                )
                self.history_data.clear()
                self.information(
                    "提示", "删除成功，请重新加载此窗口！"
                )
                view.close()
            if len(self.history_data):
                self.question_if_exec(
                    "警告",
                    "你确定要删除所有记录吗？\n"
                    "接下来的操作将会彻底删除所有记录，没错，是所有，请慎重！\n\n"
                    f"当前共有{len(self.history_data)}条历史记录, "
                    "你确定要删除吗？",
                    _confirm_deletion
                )
            else:
                self.information("提示", "没有历史记录可以删除...")



        view.setCommands(
            [
                ("删除最早记录", delete_earliest_record),
                ("删除所有记录", delete_all_records)
            ]
        )
        view.show()

    def show_classes_history(self, classes: dict[str, Class]) -> None:
        """
        显示所有班级的历史记录。
        """
        all_class_view_data: list[ListViewItemDataType] = []
        for _class in classes.values():
            text = _class.name
            func = lambda *, _class=_class: self.show_class_history(
                _class, _class.groups.values()
            )
            all_class_view_data.append((text, func))


        self.listview_history_classes = ListView("所有班级历史记录", self, all_class_view_data)
        self.listview_history_classes.show()

    def show_class_history(self, target_class: Class, groups: Iterable[Group]) -> None:
        """
        显示单个班级的历史。
        """
        groups = list(groups)
        listview_data: list[ListViewItemDataType] = []
        listview_data.append(("所有学生", lambda: None))
        listview_data.append(("", lambda: None))
        for ranking, stu in target_class.rank_non_dumplicate:
            text = f"第{ranking}名 {stu.name} {stu.score}"
            func = lambda *, stu=stu: self.student_info(
                stu, master=self, readonly=True
            )
            listview_data.append((text, func))

        listview_data.append(("", lambda: None))
        listview_data.append(("", lambda: None))
        listview_data.append(("所有小组", lambda: None))
        listview_data.append(("", lambda: None))

        for ranking, grp in [
            (ranking, grp)
            for ranking, grp in enumerate(
                sorted(groups, key=lambda grp: grp.total_score, reverse=True),
                start=1,
            )
            if grp.belongs_to == target_class.key
        ]:
            text = f"第{ranking}名 {grp.name} {grp.total_score}"
            func = lambda *, grp=grp: self.group_info(
                grp, master=self, readonly=True
            )
            listview_data.append((text, func))

        self.listview_history_class = ListView(
            f"班级 {target_class.name} 的历史记录",
            self,
            listview_data,
        )
        self.listview_history_class.show()


    def get_anim_color_for_ranking(self, stu: Student, rank: int) -> tuple[QColor, QColor]:
        """
        获取排名对应的颜色动画。
        """
        if rank == 1 and stu.score > 0:
            return (QColor(255, 255, 222), QColor(251, 220, 95))
        elif rank == 2 and stu.score > 0:
            return (QColor(244, 244, 244), QColor(232, 232, 232))
        elif rank == 3 and stu.score > 0:
            return (QColor(255, 255, 255), QColor(223, 162, 140))
        elif stu.score > 0:
            return                  \
            QColor(222, 255, 222),  \
            QColor(
                max(202, int(242 - ((stu.score) * (255 - 202) / 30))),
                255,
                max(202, int(242 - ((stu.score) * (255 - 202) / 30)))
            )
        else:
            return (QColor(255, 222, 222), QColor(255, 0, 0))
        


    def student_rank(self):
        """
        显示学生排名。
        """
        assert self.class_obs is not None, "还没有设置侦测器的时候就尝试打开学生排名窗口"
        list_view_data: list[ListViewItemDataType] = []
        for rank, stu in self.class_obs.rank_non_dumplicate:
            text = f"第{rank}名 {stu.name} {stu.score}"
            func = lambda *, stu=stu: self.student_info(stu, master=self, readonly=True)
            color_args = self.get_anim_color_for_ranking(stu, rank)
            list_view_data.append((text, func, color_args))
        self.list_view(list_view_data, "学生排名", self)

    def show_recover_points(self):
        """
        显示还原点列表。
        """
        Base.log("I", "读取列表", "ObjectInfoModel.show_recovery_point")

        self.recovery_points: dict[float, RecoveryPoint] = self.read_recovery_point_list()
        Base.log("I", "检查各个还原点", "ObjectInfoModel.show_recovery_point")

        Base.log("I", "显示列表", "ObjectInfoModel.show_recovery_point")
        list_view_data: list[ListViewItemDataType] = []
        for point in self.recovery_points.values():
            text = f"在 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(point.time))} 创建的还原点"
            func = lambda point=point: self.load_recovery_point(point)
            list_view_data.append((text, func))

        self.list_view(list_view_data, "还原点", self)

    def history_window(
        self,
        modify: ScoreModification,
        listbox_index: int,
        listbox_widget: ListView | None = None,
        readonly: bool = False,
        master: QWidget | None = None,
        remove_in_listbox_when_retracted: bool = True,
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
            modify,
            self.lastest_listview if listbox_widget is None else listbox_widget,
            listbox_index,
            self,
            readonly or (not modify.executed),
        )
        self.history_detail_window.show(readonly)

    
    def stop(self):
        widgets: list[QWidget | None] = [
            self.student_info_window,
            self.group_info_window,
            self.listview_history_classes,
            self.listview_history_class
        ]
        for widget in widgets:
            if widget is not None:
                widget.close()
        super().stop()
        