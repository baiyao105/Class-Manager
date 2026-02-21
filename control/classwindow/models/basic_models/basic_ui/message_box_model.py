"""
和展示信息框有关的模型。
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable

from utils.basetypes import Base
from utils.functions import question_yes_no
from utils.qtconfig import QWidget, QMessageBox, Signal, QPixmap, Slot

if TYPE_CHECKING:
    _BaseClass = QWidget
else:
    _BaseClass = object


class MessageBoxModel(_BaseClass):
    """
    和展示信息框有关的模型。
    
    是一个Mixin类。
    """

    signal_info = Signal(tuple)
    """
    显示信息的信号。
    """

    @Slot(tuple)
    def slot_information(self, data: tuple[str, str, QPixmap | None]):
        self.impl_information(*data)

    signal_warning = Signal(tuple)
    """
    显示警告的信号。
    """
    @Slot(tuple)
    def slot_show_warning(self, data: tuple[str, str, QPixmap | None]):
        self.impl_warning(*data)

    signal_error = Signal(tuple)
    """
    显示错误的信号。
    """

    @Slot(tuple)
    def slot_show_critical(self, data: tuple[str, str, QPixmap | None]):
        self.impl_critical(*data)

    signal_question_if_exec = Signal(tuple)
    """
    显示询问的信号。
    """
    @Slot(tuple)
    def slot_question_if_exec(self, data: tuple[str, str, Callable[[], Any], QPixmap | None]):
        self.impl_question_if_exec(*data)


    def __init__(self, master: QWidget | None = None):
        Base.log("D", "初始化MessageBoxModel", "MessageBoxModel.__init__")
        # 不调用super().__init__()
        self.master = master
        if hasattr(self, "setParent") and master:
            self.setParent(master)
        self.signal_info.connect(self.slot_information)
        self.signal_warning.connect(self.slot_show_warning)
        self.signal_error.connect(self.slot_show_critical)
        self.signal_question_if_exec.connect(self.slot_question_if_exec)

    def information(self, title: str, text: str, pixmap: QPixmap | None = None):
        """
        显示信息对话框

        :param title: 对话框标题
        :param text: 对话框内容
        :param pixmap: 自定义图标
        """
        self.signal_info.emit((title, text, pixmap))

    def impl_information(self, title: str, text: str, pixmap: QPixmap | None):
        "显示信息框的接口"
        Base.log(
            "I",
            f"信息框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.information",
        )
        msgbox = QMessageBox(
            QMessageBox.Icon.Information,
            title,
            text,
            QMessageBox.StandardButton.Ok,
            parent=self
        )
        msgbox.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-main.png"))
        msgbox.exec()

    def warning(self, title: str, text: str, pixmap: QPixmap | None = None):
        """
        显示警告对话框

        :param title: 对话框标题
        :param text: 对话框内容
        :param pixmap: 自定义图标"""
        self.signal_warning.emit((title, text, pixmap))

    def impl_warning(self, title: str, text: str, pixmap: QPixmap | None):
        "显示警告框的接口"
        Base.log(
            "W",
            f"警告框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.warning",
        )
        msgbox = QMessageBox(
            QMessageBox.Icon.Warning,
            title,
            text,
            QMessageBox.StandardButton.Ok,
            parent=self
        )
        msgbox.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-warn.png"))
        msgbox.exec()

    def critical(self, title: str, text: str, pixmap: QPixmap | None = None):
        """
        显示错误对话框

        :param title: 对话框标题
        :param text: 对话框内容
        :param pixmap: 自定义图标
        """
        self.signal_error.emit((title, text, pixmap))

    def impl_critical(self, title: str, text: str, pixmap: QPixmap | None):
        "显示错误框的接口"
        Base.log(
            "C",
            f"错误框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.critical",
        )
        msgbox = QMessageBox(
            QMessageBox.Icon.Critical,
            title,
            text,
            QMessageBox.StandardButton.Ok,
            parent=self
        )
        msgbox.setWindowIcon(pixmap or QPixmap("./img/logo/favicon-error.png"))
        msgbox.exec()

    def question_if_exec(
        self, title: str, text: str, 
        command: Callable[[], Any], pixmap: QPixmap | None = None
    ):
        """
        显示确认对话框并在用户确认时执行指定函数

        :param title: 对话框标题
        :param text: 对话框内容
        :param command: 用户确认时执行的回调函数
        :param pixmap: 自定义图标
        """
        self.signal_question_if_exec.emit((title, text, command, pixmap))

    def impl_question_if_exec(self, title: str, text: str, 
                            command: Callable[[], Any], pixmap: QPixmap | None):
        "询问框的接口"
        Base.log("I", f"询问框：{repr(title)} - {repr(text)}，pixmap={repr(pixmap)}",
            "MainWindow.question_if_exec"
        )
        if question_yes_no(
            self,
            title,
            text,
            False,
            "question",
            pixmap or QPixmap("./img/logo/favicon-help.png")
        ):
            command()
            return True
        return False
    
