"""
错误展示窗口所在模块
"""
from __future__ import annotations

import time
import traceback
from typing import TYPE_CHECKING, Any

from utils.basetypes import Base
from utils.qtconfig import QWidget, QIcon, QTimer, Qt, QCloseEvent

from widgets.basic import MyWidget
from widgets.templates import ExceptionHandler as ExceptionHandlerTemplate

if TYPE_CHECKING:
    from control.classwindow.models.basic_models.basic_ui import ExceptionHandlerModel

class ExceptionInfo:
    "记录异常信息"
    def __init__(self, tbstr: str, repeats: int, expire_time: float):
        self.tbstr = tbstr
        self.repeats = repeats
        self.expire_time = expire_time


class ExceptionHandlerWidget(ExceptionHandlerTemplate.Ui_Form, MyWidget):
    "错误窗口"

    handled_exception: dict[str, ExceptionInfo] = {}
    """
    记录已经处理过的异常（时间戳，异常Traceback，重复次数，过期时间）
    
    这里面的Tuple实际上是list
    """


    def __init__(
        self,
        model: ExceptionHandlerModel,
        exception: BaseException | None = None,
        master: QWidget | None = None
    ):
        """
        初始化

        :param master_widget: 这个窗口的父窗口
        :param main_window: 程序的主窗口，方便传参
        """
        super().__init__(master=master)
        self.model = model
        self.setup_time = time.time()
        self.exception = exception
        self.setupUi(self) # pyright: ignore[reportUnknownMemberType]
        self.setWindowTitle("出错啦！")
        self.setWindowIcon(QIcon("img/logo/favicon-error.ico"))
        self.checkBox.stateChanged.connect(self.on_checkbox_changed)
        self.spinBox.setDisabled(True)
        self.set_text_timer = QTimer(self)
        self.set_text_timer.timeout.connect(self.set_text)
        self.pushButton.clicked.connect(self.model.on_exit_with_exception)
        self.pushButton_2.clicked.connect(self.model.on_report_error)
        self.pushButton_3.clicked.connect(self.close)
        self.set_text()

    
    def on_checkbox_changed(self, *args: Any):
        state = self.checkBox.checkState()
        if state == Qt.CheckState.Checked:
            Base.log("I", "稍后提醒的选项被勾选了", "ExceptionHandler.on_checkbox_changed")
            self.spinBox.setEnabled(True)
        else:
            Base.log("I", "稍后提醒的选项被取消勾选了", "ExceptionHandler.on_checkbox_changed")
            self.spinBox.setDisabled(True)


    @property
    def tbstr(self) -> str:
        "异常的Traceback字符串"
        if self.exception:
            return "".join(traceback.format_exception(self.exception.__class__, self.exception, self.exception.__traceback__))
        raise ValueError("没有指定异常")


    def closeEvent(self, event: QCloseEvent):
        if self.checkBox.isChecked():
            self.handled_exception[self.tbstr].expire_time = time.time() + self.spinBox.value() * 60.0
        super().closeEvent(event)

    def set_text(self):
        if self.exception:
            self.label_7.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.setup_time)))
            self.label_3.setText(self.exception.__class__.__qualname__)
            excinfo_str = str(self.exception)
            repeats = 0
            if self.tbstr in self.handled_exception:
                repeats = self.handled_exception[self.tbstr].repeats - 1
            self.label_5.setText(excinfo_str + (f" [+{repeats}]" if repeats else ""))
            self.textBrowser.setText(self.tbstr)
        else:
            self.label_7.setText("不到啊")
            self.label_3.setText("怎么传了个None进来")
            self.label_5.setText("没有详细信息")
            self.textBrowser.setText("没有Traceback，别想了")

    def show(self):
        if (self.tbstr not in self.handled_exception):
            self.handled_exception[self.tbstr] = ExceptionInfo(self.tbstr, 1, 1145141919810114)
        elif (time.time() - self.handled_exception[self.tbstr].expire_time > 0):
            self.handled_exception[self.tbstr].repeats += 1
            self.handled_exception[self.tbstr].expire_time = 1145141919810114
        else:
            self.handled_exception[self.tbstr].repeats += 1
            return
        super().show()
        self.set_text()
        self.set_text_timer.start(1000)

__all__ = ["ExceptionHandlerWidget"]
