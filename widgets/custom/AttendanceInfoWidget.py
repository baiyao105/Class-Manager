"""
考勤信息展示窗口所在模块
"""

from typing import Optional, Dict, Literal
from utils import AttendanceInfo, ClassObj
from widgets.custom.ListView import ListView
from widgets.custom.AttendanceInfoViewWidget import AttendanceInfoViewWidget
from widgets.basic import *
from widgets.ui.pyside6.AttendanceInfoEdit import Ui_Form

__all__ = ["AttendanceInfoWidget"]


class AttendanceInfoWidget(Ui_Form, MyWidget):
    "考勤信息窗口"

    grid_button_signal = Signal()
    "排列按钮的信号"

    def __init__(
        self,
        master: Optional[WidgetType] = None,
        main_window: ClassObj = None,
        attendanceinfo: AttendanceInfo = None,
    ):
        """
        构造新窗口

        :param parent: 父窗口
        :param main_window: 主窗口
        :param attendanceinfo: 考勤信息
        """
        super().__init__(master)
        self.setupUi(self)
        self.main_window = main_window
        self.attendanceinfo = attendanceinfo
        self.finished = False
        self.stu_buttons: Dict[int, ObjectButton] = {}
        self.stu_states: Dict[
            int,
            Literal[
                "normal",
                "early",
                "late",
                "late_more",
                "absent",
                "leave",
                "leave_early",
                "leave_late"
            ],
        ] = {}
        self.target_class = self.main_window.classes[attendanceinfo.target_class]
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
        ],
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
        try:
            attending_list = [
                (day.attendance_info, day.utc) for day in self.main_window.weekday_record[self.target_class.key].values()
            ]
        except:
            QMessageBox.information(self, "提示", f"当前班级（{self.target_class.name}）没有考勤记录")
            return
        self.listview = ListView(
            self.main_window,
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
            self.listview, self.main_window, attendanceinfo
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

        stu = self.main_window.target_class.students[num]

        if self.stu_states[num] == "early" and state != "early":
            for h in reversed(stu.history.values()):  # 从最近的开始遍历
                if (
                    h.temp.key == "go_to_school_early"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    # 防止今天把昨天的撤掉了
                    self.main_window.retract_modify(h, info="<考勤撤回早到>")
                    break  # 因为只要撤回一个就行了

        if self.stu_states[num] != "early" and state == "early":
            self.main_window.send_modify(
                "go_to_school_early",
                self.main_window.target_class.students[num],
                info="<考勤早到>",
            )

        if self.stu_states[num] == "late" and state != "late":
            for h in reversed(stu.history.values()):
                if (
                    h.temp.key == "go_to_school_late"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    self.main_window.retract_modify(h, info="<考勤撤回迟到>")
                    break

        if self.stu_states[num] != "late" and state == "late":
            self.main_window.send_modify(
                "go_to_school_late",
                self.main_window.target_class.students[num],
                info="<考勤迟到>",
            )

        if self.stu_states[num] == "late_more" and state != "late_more":
            for h in reversed(stu.history.values()):
                if (
                    h.temp.key == "go_to_school_late_more"
                    and time.time() - h.execute_time_key / 1000 <= 86400
                    and h.executed
                ):
                    self.main_window.retract_modify(h, info="<考勤撤回迟到过久>")
                    break

        if self.stu_states[num] != "late_more" and state == "late_more":
            self.main_window.send_modify(
                "go_to_school_late_more",
                self.main_window.target_class.students[num],
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


