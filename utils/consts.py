"""
常量文件
"""

import os
import sys
import math
import time
import datetime
from typing import Literal, Any, Dict


debug: bool = True
"是否为调试模式"

enable_memory_tracing = False
"是否启用内存追踪"


default_user = "测试用户1"
"""默认用户名常量"""

app_style: Literal["windowsvista", "Windows", "Fusion", "windows11"] = "windowsvista"
"软件的样式"

qt_version: Literal["PyQt5", "PyQt6", "PySide2", "PySide6"] = "PySide6"
"使用的Qt版本"


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

LOG_FILE_PATH = (
    f'log/ClassManager_log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    + f"_{str(int((time.time() % 1) * 1000000)).zfill(6)}.log"
)
"日志文件路径"


runtime_flags: Dict[Any, Any] = {}
"全局变量字典"


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
