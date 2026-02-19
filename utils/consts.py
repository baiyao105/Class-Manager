"""
常量文件
"""
from __future__ import annotations
import math
import os
import random
import sys
from typing import Any, Literal, TYPE_CHECKING, Optional


if TYPE_CHECKING:
    from .events import BroadcastDispatcher

debug: bool = True
"是否为调试模式"

enable_memory_tracing = False
"是否启用内存追踪"


default_user = "测试用户1"
"""默认用户名常量"""

app_style: Literal["windowsvista", "Windows", "Fusion", "windows11"] = "windowsvista"
"软件的样式"


qt_version: Literal["PySide6"] = "PySide6"
"使用的Qt版本"

qt_log_filter: str = "*.*=true\n*.debug=false\n*.info=false"
"Qt的日志过滤规则"

app_stylesheet: str = """
QMainWindow {
    color: black;
    font-family: 'Microsoft YaHei UI';
}

QWidget {
    color: black;
    font-family: 'Microsoft YaHei UI';
}
"""
"软件的样式表"


nl = "\n"
"换行符，3.8.10中的f-string有奇效"


log_style: Literal["new", "old"] = "old"
"日志的样式，new为新版，old为老版"


sound_file_path = "audio/sounds"
"声音文件路径"


inf = math.inf
"无穷大"

ninf = -math.inf
"无穷小"

nan = -math.nan
"非数"

cwd = os.getcwd()

LOG_PATH = "log"
"日志文件路径"


CONSOLE_TITLE = "班寄管理: 调试控制台     %s" % (
    random.choice([
        "也算是一种朝花夕拾?",
        "Make class great again!",
        "这个项目没救了罢（悲",
        "你会喜欢严格类型检查的, 信我",
        "是一种连AI都模仿不出来的神秘语录么, 有点意思",
        "Python还是太神秘了"
    ])
)
"调试控制台窗口标题"


runtime_flags: dict[Any, Any] = {}
"全局变量字典"

if getattr(sys, 'frozen', False):
    os.add_dll_directory(os.path.dirname(sys.executable))


def _should_alloc_console() -> bool:
    """
    检查命令行参数是否包含调试命令。
    """
    if getattr(sys, 'frozen', False):
        args = sys.argv[1:]
        return '--debug' in args or '-d' in args
    return False

def _alloc_console() -> bool:
    """
    在Windows上分配控制台窗口。
    """
    if sys.platform != 'win32':
        return False
    
    try:
        import ctypes
        from ctypes import wintypes
        
        kernel32 = ctypes.windll.kernel32
        AllocConsole = kernel32.AllocConsole
        AllocConsole.argtypes = []
        AllocConsole.restype = wintypes.BOOL
        SetStdHandle = kernel32.SetStdHandle
        SetStdHandle.argtypes = [wintypes.DWORD, wintypes.HANDLE]
        SetStdHandle.restype = wintypes.BOOL
        SetConsoleTitle = kernel32.SetConsoleTitleW
        SetConsoleTitle.argtypes = [wintypes.LPCWSTR]
        SetConsoleTitle.restype = wintypes.BOOL
        
        if not AllocConsole():
            return False
        
        SetConsoleTitle(CONSOLE_TITLE)
        
        sys.stdout = open('CONOUT$', 'w', encoding='utf-8')
        sys.stderr = open('CONOUT$', 'w', encoding='utf-8')
        sys.__stdout__ = sys.stdout
        sys.__stderr__ = sys.stderr
        
        return True
    except Exception:
        return False

if _should_alloc_console():
    _alloc_console()

# 为了防止发行包输出被覆盖掉，
# 如果检测到没有输出流，就打开一个文件作为输出流
if sys.stdout is None:
    if sys.__stdout__ is None:
        sys.stdout = open(os.path.join(os.getcwd(), "stdout"), "w", encoding="utf-8")
        sys.stderr = open(os.path.join(os.getcwd(), "stderr"), "w", encoding="utf-8")
        sys.__stdout__ = sys.stdout
        sys.__stderr__ = sys.stderr

    else:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__


stdout_orig = sys.stdout
"原始标准输出流"

stderr_orig = sys.stderr
"原始标准错误流"

stdout = sys.stdout
"当前标准输出流（可能被覆盖过）"

stderr = sys.stderr
"当前标准错误流（可能被覆盖过）"


dispatcher: Optional[BroadcastDispatcher] = None


def get_global_dispatcher() -> BroadcastDispatcher:
    global dispatcher
    from .events.broadcast import BroadcastDispatcher
    if not dispatcher:
        dispatcher = BroadcastDispatcher(name="GlobalDispatcher")
    return dispatcher
    
