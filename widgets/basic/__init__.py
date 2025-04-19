"""
基础窗口类
"""
import sys
from .MyMainWindow import MyMainWindow
from .MyWidget import MyWidget
from .Qt import *
from .widgets import *
from utils import Base


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
    sys.exit(0)


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

last_process_time = 0
"上次处理QCoreApplication.processEvents的时间"

max_process_rate = 120
"最大处理QCoreApplication.processEvents的频率"

def do_nothing():
    "啥也不干，让程序摸鱼一会"
    # global last_process_time
    # if time.time() - last_process_time > 1 / max_process_rate:
        # last_process_time = time.time()
    try:
        QCoreApplication.processEvents()
    except (RuntimeError, ValueError) as unused:
        pass