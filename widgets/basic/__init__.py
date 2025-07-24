"""
基础窗口类
"""
import sys
from .MyMainWindow import MyMainWindow
from .MyWidget import MyWidget
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
from .widgets import *
from utils.logger import Logger as Base


WidgetType = Union[
    QMainWindow, QWidget, QFrame, QStackedWidget, QScrollArea, MyMainWindow, MyWidget
]


def handle_fatal_qt_error(msg: str):
    """处理Qt致命错误并安全退出程序"""
    Base.log("F", "PySide6发生致命错误：", "MainThread")
    Base.log("F", msg, "MainThread")
    # widget.save_current_settings()
    # widget.save_data()
    # widget.critical("错误", f"PySide6发生致命错误\n错误信息：\n {msg}")
    # widget.closeEvent(QCloseEvent(), do_tip=False)
    # widget.destroy()
    Base.log("F", "程序退出", "MainThread")
    sys.exit(1)



def qt_messagehandler(
    mode: QtMsgType, context: QMessageLogContext, msg: str
):  # pylint: disable=unused-argument
    """自定义Qt消息处理函数，使用字典映射优化日志记录"""
    # 使用字典映射消息类型到日志级别
    msg_type_map = {
        QtMsgType.QtDebugMsg: "D",
        QtMsgType.QtInfoMsg: "I",
        QtMsgType.QtWarningMsg: "W",
        QtMsgType.QtCriticalMsg: "C",
        QtMsgType.QtFatalMsg: "F",
    }

    # 记录日志
    log_level = msg_type_map.get(mode, "I")  # 默认为Info级别
    Base.log(log_level, msg, "PySide6")

    # 处理致命错误
    if mode == QtMsgType.QtFatalMsg:
        handle_fatal_qt_error(msg)


qInstallMessageHandler(qt_messagehandler)
QLoggingCategory.setFilterRules("*.*=true\n*.debug=false\n*.info=false")
# 让Qt把除了debug和info以外的日志都输出到qtmessagehandler
