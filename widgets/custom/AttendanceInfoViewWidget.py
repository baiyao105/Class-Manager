
"""
考勤信息窗口所在模块
"""

from typing import Optional
from utils import AttendanceInfo, ClassObj
from widgets.basic import *
from widgets.ui.pyside6.AttendanceInfoView import Ui_Form

__all__ = ["AttendanceInfoViewWidget"]


class AttendanceInfoViewWidget(Ui_Form, MyWidget):
    """考勤信息查看器"""

    def __init__(
        self,
        master: Optional[WidgetType] = None,
        main_window: Optional[ClassObj] = None,
        attendanceinfo: AttendanceInfo = None,
    ):
        """
        构造新窗口

        :param master: 父窗口
        :param main_window: 主窗口
        :param attendanceinfo: 考勤信息
        """
        super().__init__(master)
        self.setupUi(self)
        self.main_window = main_window
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
