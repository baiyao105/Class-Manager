"""
小组窗口所在模块
"""

from __future__ import annotations

from utils.basetypes import Base
from utils.classobjects import ClassDataSet, Group, Student
from utils.qtconfig import (Signal, QWidget, QVBoxLayout, QTimer, QCloseEvent,
                            QListWidgetItem, QModelIndex, QEasingCurve, QColor)


from widgets.basic.widgets import ProgressAnimatedListWidgetItem
from widgets.custom.StudentWidget import StudentWidget
from widgets.custom.StudentSelectorWidget import StudentSelectorWidget
from widgets.custom.SelectTemplateWidget import SelectTemplateWidget
from widgets.basic import MyWidget
from widgets.templates import GroupWindow 



class GroupWidget(GroupWindow.Ui_Form, MyWidget):
    "小组窗口"

    student_list_update = Signal()
    "学生列表更新信号"

    def __init__(
        self,
        group: Group,
        dataset: ClassDataSet,
        master: QWidget | None = None,
        readonly: bool = False,
    ):
        """
        初始化。

        :param main_window: 程序的主窗口，方便传参
        :param master_widget: 这个窗口的父窗口
        :param group: 这个学生窗口对应的小组
        """
        super().__init__(master=master)
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
        self.group = group
        self.show()
        self.mainLayout = QVBoxLayout()
        self.setWindowTitle("小组信息 - " + str(group.name))
        self.setLayout(self.mainLayout)
        self.first_load = True
        self.update_timer = QTimer(self)
        self.last_score: dict[str | Student, float] = {}
        self.update_timer.timeout.connect(self.update_label)
        self.update_timer.start(100)
        self.main_window = dataset
        self.master_widget = master
        self.listWidget_order: list[Student] = []
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
        self.pushButton.clicked.connect(self.select_member_and_send)
        self.stu_list_update_timer = QTimer(self)
        self.student_list_update.connect(self.update_stu_list)
        self.stu_list_update_timer.timeout.connect(self.student_list_update.emit)
        self.stu_list_update_timer.start(1000)
        self.readonly = readonly
        self.pushButton.setDisabled(readonly)
        self.pushButton_2.setDisabled(readonly)
        self.pushButton_2.clicked.connect(self.send_to_all_members)
        self.last_value: list[float] = []
        self.stu_selector: StudentSelectorWidget | None = None
        self.tmp_selector: SelectTemplateWidget | None = None
        self.destroyed.connect(self.stu_list_update_timer.stop)
        self.destroyed.connect(self.update_timer.stop)

    def show(self, readonly: bool = False):
        Base.log("I", f"小组信息窗口显示：选中{self.group}", "GroupWidget.show")
        super().show()
        self.pushButton.setDisabled(readonly)
        self.pushButton_2.setDisabled(readonly)
        self.readonly = readonly
        self.first_load = True
    

    def select_member_and_send(self):
        "选择当前组员并发送"
        self.stu_selector = StudentSelectorWidget(self.main_window, self, self.group.members, title="选择组员")
        result = self.stu_selector.exec()
        self.tmp_selector = SelectTemplateWidget(self.main_window, self)
        key, title, desc, mod = self.tmp_selector.exec()
        if key is None:
            Base.log("I", "取消发送点评，exec() 返回了None或者key是None", "GroupWidget.select_member_and_send")
            return
        self.main_window.send_modify(key, result, title, desc, mod, "选组员发送")

    def send_to_all_members(self):
        "发送至所有组员"
        self.tmp_selector = SelectTemplateWidget(self.main_window, self)
        key, title, desc, mod = self.tmp_selector.exec()
        if key is None:
            Base.log("I", "取消发送点评，exec() 返回了None或者key是None", "GroupWidget.send_to_all_members")
            return
        self.main_window.send_modify(key, self.group.members, title, desc, mod, "选组员发送")



    def student_clicked(self, index: QModelIndex):
        """
        点击列表项操作

        :index: 传过来的索引，不用管（是自动的）
        """
        student = self.listWidget_order[index.row()]
        Base.log(
            "I",
            f"点击列表项:{index.row()}, {repr(student)}",
            "GroupWidget.student_clicked",
        )
        if hasattr(self, "student_window"):
            self.student_window.destroy()  # pylint: disable=access-member-before-definition
        self.student_window = StudentWidget(
            dataset=self.main_window, master=self, student=student
        )  # pylint: disable=attribute-defined-outside-init
        self.student_window.show(self.readonly)

    def update_label(self):
        self.label_6.setText(str(self.group.name))
        self.label_9.setText(str(len(self.group.members)))
        self.label_8.setText(
            str(self.group.total_score)
            + f"（均分{self.group.average_score}，去最低分{self.group.average_score_without_lowest}）"
        )
        self.label_7.setText(str(self.main_window.classes[self.group.belongs_to].name))
        self.label_11.setText(str(self.group.leader.name))

    def update_stu_list(self):
        if self.last_score == {}:
            for member in self.group.members:
                self.last_score[member] = member.score
            self.last_score["total"] = self.group.total_score
        self.listWidget.clear()
        self.listWidget_order: list[Student] = []
        end_value: list[float] = []
        for member in sorted(self.group.members, key=lambda s: s.score, reverse=True):
            item = ProgressAnimatedListWidgetItem(
                f"{member.num}号 {member.name} {member.score}分"
            )
            self.listWidget.addItem(item)
            widget_item = item.getWidget()
            self.listWidget.setItemWidget(item, widget_item)
            try:
                start = self.last_value.pop(0)
            except Exception:
                start = min(
                    abs(
                        self.last_score[member]
                        / (
                            max(
                                self.last_score["total"],
                                *[abs(s.score) for s in self.group.members],
                            )
                            if (
                                self.last_score["total"] != 0
                                and max([abs(s.score) for s in self.group.members]) != 0
                            )
                            else max(*[abs(s.score) for s in self.group.members], 0.1)
                        )
                    ),
                    1,
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
                1,
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

__all__ = ["GroupWidget"]
