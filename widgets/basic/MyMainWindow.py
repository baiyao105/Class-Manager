"""
我的主窗口
"""
from typing import Optional
from utils.logger import Logger
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from utils.functions.prompts import question_yes_no

__all__ = ["MyMainWindow"]

class MyMainWindow(QMainWindow):
    """主应用程序窗口类"""

    main_instance: Optional["MyMainWindow"] = None
    "主实例"



    def __init__(self):
        super().__init__()
        self.is_running = True
        self.setTopmost(True)
        self.move(200, 110)
        self.setWindowFlags(
            (
                Qt.WindowType.WindowCloseButtonHint
                | Qt.WindowType.MSWindowsFixedSizeDialogHint
                | Qt.WindowType.WindowTitleHint
                | Qt.WindowType.WindowSystemMenuHint
                | Qt.WindowType.Window
            )
        )
        self.close_count = 0
        self.clear_time_timer = QTimer(self)
        self.clear_time_timer.timeout.connect(self.clear_close_count)
        self.clear_time_timer.start(30000)


    @Slot()
    def clear_close_count(self):
        self.close_count = 0

    def setTopmost(self, topmost: bool = True):
        "设置窗口置顶状态"
        if topmost:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
            )
        self.show()

    def closeEvent(self, event: QCloseEvent, tip=True) -> bool:
        "处理窗口关闭事件"
        Logger.log("I", "主窗口尝试退出", "MyMainWindow")
        self.close_count += 1
        if tip:
            if self.isEnabled():
                reply = question_yes_no(
                    self,
                    "提示",
                    "确定退出？" if self.close_count <= 5 else "确认退出程序？",
                )
                # 判断返回结果处理相应事项w
                if reply:
                    Logger.log("I", "确认退出", "MyMainWindow")
                    event.accept()
                    self.is_running = False
                    return True

                else:
                    Logger.log("I", "取消退出", "MyMainWindow")
                    event.ignore()
                    return False
            else:
                Logger.log("I", "子窗口未关闭，无法退出", "MyMainWindow")
                event.ignore()
                return False
        else:
            Logger.log("I", "退出", "MyMainWindow")
            event.accept()
            self.is_running = False
            return True