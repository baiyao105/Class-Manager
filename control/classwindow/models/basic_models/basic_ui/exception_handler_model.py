"""
捕获错误并显示错误窗口的模型。
"""
from __future__ import annotations

import os
import sys
import threading
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Optional, Tuple, Type, TypeAlias

from utils.consts import log_style
from utils.logger import logger
from utils.basetypes import Base
from utils.qtconfig import Signal, QWidget, Slot

from widgets.custom.ExceptionHandler import ExceptionHandlerWidget


# 为了防止神秘Qt在重复继承的时候会爆炸
if TYPE_CHECKING:
    _BaseClass = QWidget
else:
    _BaseClass = object


OptExcInfo: TypeAlias = Tuple[
    Optional[Type[BaseException]], 
    Optional[BaseException],
    Optional[TracebackType]
]
"异常信息类型别名。"

ThreadingExcInfo: TypeAlias = Tuple[
    Optional[Type[BaseException]], 
    Optional[BaseException], 
    Optional[TracebackType], 
    Optional[threading.Thread]
]
"线程异常信息类型别名。"


class ExceptionHandlerModel(_BaseClass):
    """
    捕获错误并显示错误窗口的模型。
    
    是一个Mixin类。
    """

    signal_show_exc_window = Signal(tuple)
    """
    显示异常窗口的信号。
    """

    show_exc_window_callback: Optional[Callable[[OptExcInfo], Any]] = None
    "显示异常窗口的回调函数"

    def __init__(self, master: QWidget | None = None) -> None:
        """
        初始化异常处理模型。

        :param exception: 异常对象。
        :param traceback: 异常的回溯信息。
        """
        Base.log("D", "初始化ExceptionHandlerModel", "ExceptionHandlerModel.__init__")
        # 这里不调用super().__init__()
        self.master = master
        if hasattr(self, 'setParent') and master:
            self.setParent(master)
        self.setup_hooks(self.handle_exception)
        self.show_exc_window_callback = self.show_exc_window
        self.exception_window: ExceptionHandlerWidget | None = None
        "异常信息窗口"
        self.signal_show_exc_window.connect(self.slot_show_exc_window)

    def show_exc_window(self, excinfo: OptExcInfo) -> None:
        """
        显示异常窗口。

        :param excinfo: 异常信息。
        """
        self.signal_show_exc_window.emit(excinfo)

    @Slot(tuple)
    def slot_show_exc_window(self, e: OptExcInfo):
        "展示异常信息的接口"
        Base.log("I", f"展示异常信息窗口：{e!r}", "MainWindow._show_exception")
        self.exception_window = ExceptionHandlerWidget(model=self, exception=e[1], master=self)
        self.exception_window.show()

    @Slot()
    def on_exit_with_exception(self):
        """
        当遇到错误并且用户想要退出的时候执行的操作。
        """
        self.close()
        sys.exit(0)

    @Slot()
    def on_report_error(self):
        """
        当用户想要报告错误的时候执行的操作。
        """
        os.startfile("https://www.bilibili.com/video/BV1GJ411x7h7/")
        self.close()

    @Slot()
    def on_close(self):
        """
        当用户想要关闭窗口的时候执行的操作。
        """
        self.close()
    

    def setup_hooks(self, hook: Callable[[*OptExcInfo], Any]) -> None:
        sys.excepthook = hook
        threading.excepthook = hook

        
    def handle_exception(self, 
            exc_type: Type[BaseException] | None, 
            exc_val: BaseException | None, 
            exc_tb: TracebackType | None,
            thread: threading.Thread | None = None
        ) -> None:
        """
        捕获未处理的异常并显示错误对话框，
        用作sys.excepthook和threading.excepthook的处理函数。

        :param excinfo: 异常信息。
        """
        file_basename = os.path.basename(__file__)
        file_path = __file__.replace(os.getcwd(), "").lstrip("\\/")
        # 绑定上下文信息
        if log_style == "new":
            binding = logger.bind(
                file=file_basename,
                full_file=file_path,
                source="handle_exception",
                lineno=-1,
                source_with_lineno="handle_exception:-1",
            )
            if thread:
                binding = binding.bind(thread=thread)
            binding.exception("Uncaught exception occurred", exc_info=exc_val)
        else:
            Base.log_exc("捕获到异常", "exception_handler", exc=exc_val)
        
        if self.show_exc_window_callback is not None:
            self.show_exc_window_callback((exc_type, exc_val, exc_tb))

       
    def stop(self):
        if self.exception_window:
            self.exception_window.close()
