"""
考勤信息展示窗口所在模块
"""

from __future__ import annotations

import time
from typing import Literal, TypeAlias

from utils.basetypes import Base
from utils.classobjects import AttendanceInfo, ClassDataSet
from utils.qtconfig import (Signal, QWidget, QTimer, Slot, 
                            QMessageBox, QColor, QRect, QRadioButton)

from widgets.custom.ListView import ListView
from widgets.custom.AttendanceInfoViewWidget import AttendanceInfoViewWidget
from widgets.basic import *
from widgets.templates import AttendanceInfoEdit


class TargetClassNotSetError(UIError):
    "还没有设置目标班级。"    

class NoSelectedStateError(UIError):
    "没有选中学生的状态。"

StudentState: TypeAlias = Literal [
    "normal",       # 到校正常
    "early",        # 提前到校
    "late",         # 迟到
    "late_more",    # 迟到过久
    "absent",       # 请假/缺勤
    "leave",        # 临时请假
    "leave_early",  # 未知早退
    "leave_late"    # 晚退
]

class AttendanceInfoWidget(AttendanceInfoEdit.Ui_Form, MyWidget):
    "考勤信息窗口"

    grid_button_signal = Signal()
    "排列按钮的信号"



    def __init__(
        self,
        attendanceinfo: AttendanceInfo,
        dataset: ClassDataSet,
        master: QWidget | None = None
    ):
        """
        构造新窗口。

        :param attendanceinfo: 考勤信息
        :param dataset: 数据集
        :param master: 父窗口
        """
        super().__init__(master)
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
        self.dataset = dataset
        self.attendanceinfo = attendanceinfo
        self.finished = False
        self.stu_buttons: dict[int, ObjectButton] = {}
        self.stu_states: dict[int, StudentState] = {}
        self.target_class = self.dataset.classes[attendanceinfo.target_class]
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
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_text)
        self.update_timer.start(100)
        self.radioButton.setChecked(True)
        self.pushButton.clicked.connect(self.show_attending_list)

    @staticmethod
    def attending_state_to_string(state: StudentState):
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
        try:
            attending_list = [
                (day.attendance_info, day.utc) for day in self.dataset.weekday_record[self.target_class.key].values()
            ]
        except:
            QMessageBox.information(self, "提示", f"当前班级（{self.target_class.name}）没有考勤记录")
            return
        self.listview = ListView(
            "考勤记录",
            self,
            [
                (
                    time.strftime("%Y年%m月%d日的考勤记录", time.localtime(utc)),
                    lambda att=att: self.show_attendance(att) # type: ignore
                )
                for att, utc in attending_list
            ],
        )
        self.listview.show()

    def show_attendance(self, attendanceinfo: AttendanceInfo):
        self.view = AttendanceInfoViewWidget(
             attendanceinfo, self.listview
        )
        self.view.show()

    def set_state(self, num: int, state: StudentState):
        # 这写的是什么爆炸东西

        if self.dataset.target_class is None:
            raise TargetClassNotSetError("还没设置目标班级就打开了这个窗口")
        
        stu = self.dataset.target_class.students[num]

        if self.stu_states[num] == "early" and state != "early":
            for h in reversed(stu.history.values()):  # 从最近的开始遍历
                if (
                    h.temp.key == "go_to_school_early"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    # 防止今天把昨天的撤掉了
                    self.dataset.retract_modify(h, info="<考勤撤回早到>")
                    break  # 因为只要撤回一个就行了

        if self.stu_states[num] != "early" and state == "early":
            self.dataset.send_modify(
                "go_to_school_early",
                self.dataset.target_class.students[num],
                info="<考勤早到>",
            )

        if self.stu_states[num] == "late" and state != "late":
            for h in reversed(stu.history.values()):
                if (
                    h.temp.key == "go_to_school_late"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    self.dataset.retract_modify(h, info="<考勤撤回迟到>")
                    break

        if self.stu_states[num] != "late" and state == "late":
            self.dataset.send_modify(
                "go_to_school_late",
                self.dataset.target_class.students[num],
                info="<考勤迟到>",
            )

        if self.stu_states[num] == "late_more" and state != "late_more":
            for h in reversed(stu.history.values()):
                if (
                    h.temp.key == "go_to_school_late_more"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    self.dataset.retract_modify(h, info="<考勤撤回迟到过久>")
                    break

        if self.stu_states[num] != "late_more" and state == "late_more":
            self.dataset.send_modify(
                "go_to_school_late_more",
                self.dataset.target_class.students[num],
                info="<考勤迟到过久>",
            )

        self.stu_states[num] = (
            state  # 把原来的撤回了再更新状态（你猜猜是我已经知道了还是踩过坑）
        )

        Base.log("I", f"设置学生{num}的状态为{state}", "AttendanceInfoWidget.set_state")

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
        self.stu_buttons[num].set_color(self.get_state_color(self.stu_states[num]))

    def get_state_color(self, state: StudentState) -> QColor:
        mapping: dict[StudentState, QColor] = {
            "normal": QColor(232, 244, 232),
            "early":  QColor(202, 255, 202),
            "late": QColor(255, 244, 232),
            "late_more": QColor(255, 232, 232),
            "absent": QColor(196, 196, 196),
            "leave": QColor(255, 255, 232),
            "leave_early": QColor(244, 255, 232),
            "leave_late": QColor(244, 244, 202)
        }
        return mapping.get(state, QColor(255, 255, 255))

    def get_current_selected_state(self) -> StudentState:
        mapping: dict[StudentState, QRadioButton] = {
            "normal": self.radioButton,
            "early": self.radioButton_2,
            "late": self.radioButton_3,
            "late_more": self.radioButton_4,
            "absent": self.radioButton_5,
            "leave": self.radioButton_6,
            "leave_early": self.radioButton_7,
            "leave_late": self.radioButton_8
        }
        for k, v in mapping.items():
            if v.isChecked():
                return k
        raise NoSelectedStateError("没有选中任何状态？？这怎么可能？？？")

    def grid_buttons(self):
        """
        显示按钮（虽然不算真正意义上的grid）
        """
        self.grid_button_signal.emit()

    def _grid_buttons(self):
        "显示按钮的接口"
        for b in self.stu_buttons.values():
            b.destroy()
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
                    self.set_state(num, self.get_current_selected_state())
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
            except (KeyError, RuntimeError) as e:
                Base.log(
                    "W",
                    f"遇到了{e.__class__.__name__}，疑似刚刚添加/减少学生，正在重新加载",
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



__all__ = ["AttendanceInfoWidget"]
