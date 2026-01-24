"""
错误展示窗口所在模块
"""

import time
import traceback
from typing import Optional, Tuple, List, Dict
from utils.classobjects import ClassObj
from widgets.custom.ListView import ListView
from widgets.basic import *
from widgets.ui.pyside6.ExceptionHandler import Ui_Form

__all__ = ["ExceptionHandler"]


class ExceptionInfo:
    "记录异常信息"
    def __init__(self, tbstr: str, repeats: int, expire_time: int):
        self.tbstr = tbstr
        self.repeats = repeats
        self.expire_time = expire_time


class ExceptionHandler(Ui_Form, MyWidget):
    "错误窗口"

    handled_exception: Dict[str, ExceptionInfo] = {}
    """
    记录已经处理过的异常（时间戳，异常Traceback，重复次数，过期时间）
    
    这里面的Tuple实际上是list
    """



    def __init__(
        self,
        master_widget: Optional[WidgetType] = None,
        main_window: Optional[ClassObj] = None,
        exception: Optional[Exception] = None,
    ):
        """
        初始化

        :param master_widget: 这个窗口的父窗口
        :param main_window: 程序的主窗口，方便传参
        """
        super().__init__(master=master_widget)
        self.master_widget = master_widget
        self.main_window = main_window
        "当前异常在列表中的索引"
        self.setup_time = time.time()
        self.exception = exception
        self.setupUi(self)
        self.setWindowTitle("出错啦！")
        self.setWindowIcon(QIcon("img/logo/favicon-error.ico"))
        self.checkBox.stateChanged.connect(self.on_checkbox_changed)
        self.spinBox.setDisabled(1)
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.set_text()

    @property
    def tbstr(self) -> str:
        "异常的Traceback字符串"
        if self.exception:
            return "".join(traceback.format_exception(self.exception.__class__, self.exception, self.exception.__traceback__))
        raise ValueError("没有指定异常")

    def on_checkbox_changed(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            self.spinBox.setDisabled(0)
        else:
            self.spinBox.setDisabled(1)

    def closeEvent(self, event):
        if self.checkBox.isChecked():
            self.handled_exception[self.tbstr].expire_time = time.time() + self.spinBox.value() * 60.0
        super().closeEvent(event)


    def run(self):
        self.set_text()
        if (self.tbstr not in self.handled_exception):
            self.handled_exception[self.tbstr] = ExceptionInfo(self.tbstr, 1, 1145141919810114)
        elif (time.time() - self.handled_exception[self.tbstr].expire_time > 0):
            self.handled_exception[self.tbstr].repeats += 1
        else: 
            return
        super().show()
        

    def set_text(self):
        if self.exception:
            self.label_7.setText(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.setup_time)))
            self.label_3.setText(self.exception.__class__.__qualname__)
            if self.tbstr in self.handled_exception:
                self.label_5.setText(f"[+{self.handled_exception[self.tbstr].repeats}]")
            else:
                self.label_5.setText("")
        else:
            self.label_7.setText("不到啊")
            self.label_3.setText("怎么传了个None进来")
            self.label_5.setText("")
            self.textBrowser.setText("没有Traceback，别想了")

    def update(self):
        self.set_text()
        super().update()

    def show(self):
        self.update_timer.start(1000)
        super().show()
