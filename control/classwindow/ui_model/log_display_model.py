"""
和日志显示有关的模型。
"""

from __future__ import annotations

import time

from utils.basetypes import Base
from utils.algorithm import Thread
from utils.qtconfig import Signal, Slot, QTextEdit

from .class_ui_model import MixinSuperType


class LogDisplayModel(MixinSuperType):
    """
    日志显示模型。
    """

    signal_log_update = Signal(str)
    """
    日志更新信号，用于更新日志窗口的内容。
    """

    signal_log_window_refresh = Signal()
    """
    日志窗口刷新信号，用于刷新日志窗口，让窗口的内容和最新日志保持同步。
    """

    def __init__(
        self, 
        current_user: str, 
        class_name: str, 
        class_key: str, 
        save_path: str | None = None
    ):
        Base.log("D", "初始化LogDisplayModel", "LogDisplayModel.__init__")

        self.textBrowser.setReadOnly(True)
        self.textBrowser.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.logwindow_content: list[str] = []
        "主窗口日志内容"
        self.refresh_log_window_thread = Thread(
            target=self.refresh_logwindow_while_alive,
            daemon=True,
            name="RefreshLogWindowThread",
        )
        self.refresh_log_window_thread.start()
        self.signal_log_update.connect(self.logwindow_add_newline)
        self.signal_log_window_refresh.connect(self._refresh_logwindow)
        self.signal_log_update.emit("这里是日志")

    def refresh_logwindow_while_alive(self):
        """
        更新日志窗口显示内容，每隔一段时间同步最新日志信息。
        """
        while self.is_running and not self.should_stop:
            self.signal_log_window_refresh.emit()
            time.sleep(self.log_update_interval)

    @Slot(str)
    def logwindow_add_newline(self, string: str):
        """
        向日志窗口添加新日志条目。

        :param string: 要添加的日志文本
        """
        if not hasattr(self, "logwindow_content"):
            self.logwindow_content = []
        self.logwindow_content.append(string.strip())
        if len(self.logwindow_content) > self.log_keep_linecount:
            self.logwindow_content.pop(0)

    @Slot()
    def _refresh_logwindow(self):
        "刷新日志窗口的接口，不要直接跨线程调用，会爆炸"
        if self.logged_count != self.displayed_on_the_log_window:
            self.textBrowser.setText("\n".join(self.short_log_info))
            self.textBrowser.verticalScrollBar().setValue(
                self.textBrowser.verticalScrollBar().maximum()
            )
            self.displayed_on_the_log_window = self.logged_count