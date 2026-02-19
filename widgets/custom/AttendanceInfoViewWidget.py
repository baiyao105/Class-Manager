
"""
考勤信息窗口所在模块
"""

from __future__ import annotations

from utils.qtconfig import QWidget
from utils.classobjects import AttendanceInfo

from widgets.basic import MyWidget
from widgets.templates import AttendanceInfoView



class AttendanceInfoViewWidget(AttendanceInfoView.Ui_Form, MyWidget):
    """
    考勤信息查看器。

    （好敷衍。。。）
    """

    def __init__(
        self,
        attendanceinfo: AttendanceInfo,
        master: QWidget | None = None
    ):
        """
        构造新窗口。

        :param master: 父窗口
        :param attendanceinfo: 考勤信息
        """
        super().__init__(master)
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
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

__all__ = ["AttendanceInfoViewWidget"]
