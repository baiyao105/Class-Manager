"""
日志记录器
"""

import os
import sys
import time
import inspect
import traceback
from queue import Queue
from threading import Thread, Lock
from typing import Optional, TextIO, Literal, final, List

import colorama
from loguru import logger

import utils.consts as consts

from utils.consts import LOG_FILE_PATH, stdout_orig, stderr_orig, log_style, cwd
from utils.system import SystemLogger
from utils.functions.excinfo import format_exc_like_java
def get_time():
    "获得当前时间"
    lt = time.localtime()
    return (
        f"{lt.tm_year}-{lt.tm_mon:02}-{lt.tm_mday:02} "
        + f"{lt.tm_hour:02}:{lt.tm_min:02}:{lt.tm_sec:02}"
        + f".{int((time.time()%1)*1000):03}"
    )



__all__ = ["LoggerSettings", "log_settings", "Logger", "Color"]


class LoggerSettings:
    "日志配置"

    def __init__(
        self,
        log_file_path: Optional[str] = LOG_FILE_PATH,
        fast_log_file_path: Optional[str] = None,
        console_wrapper: Optional[TextIO] = stdout_orig,
        log_mode: Literal["write_instantly", "write_buffered"] = "write_instantly",
        log_level: Literal["I", "W", "E", "F", "D", "C"] = "D",
        draw_color: bool = True,
        use_mutex: bool = True,
        encoding: Optional[str] = "utf-8",
    ):
        """
        初始化日志配置

        :param log_file_path: 日志文件路径
        :param fast_log_file_path: 快速日志文件路径
        :param console_wrapper: 控制台的输出
        :param log_mode: 日志模式
        :param log_level: 日志等级
        :param draw_color: 是否绘制颜色
        :param use_mutex: 是否使用互斥锁
        """
        self.log_file_path = log_file_path
        "日志文件路径"
        self.fast_log_file_path = fast_log_file_path
        "快速日志文件路径"
        self.console_wrapper = console_wrapper
        "控制台的输出"
        self.log_mode: Literal["write_instantly", "write_buffered"] = log_mode
        "日志模式"
        self.log_level = log_level
        "日志等级"
        self.draw_color = draw_color
        "是否着色"
        self.use_mutex = use_mutex
        "是否使用互斥锁"
        self.encoding = encoding
        "编码"


log_settings = LoggerSettings()


LIGHT_CYAN = "<light-cyan>" if log_settings.draw_color else ""
LIGHT_GREEN = "<light-green>" if log_settings.draw_color else ""
BLUE = "<blue>" if log_settings.draw_color else ""
LEVEL = "<level>" if log_settings.draw_color else ""

LIGHT_CYAN_CLOSE = "</light-cyan>" if log_settings.draw_color else ""
LIGHT_GREEN_CLOSE = "</light-green>" if log_settings.draw_color else ""
BLUE_CLOSE = "</blue>" if log_settings.draw_color else ""
LEVEL_CLOSE = "</level>" if log_settings.draw_color else ""

# 初始化日志配置
logger.remove()
logger.add(
    stdout_orig,  # 这样就不会重复读写了
    format=f"{LIGHT_CYAN}{{time:YYYY-MM-DD HH:mm:ss.SSS}}"
    f"{LIGHT_CYAN_CLOSE} | {LEVEL}{{level: <8}}{LEVEL_CLOSE} | "
    f"{BLUE}{{extra[file]: <15}}{BLUE_CLOSE} | "
    f"{LIGHT_GREEN}{{extra[source]}}:{{extra[lineno]}}"
    f"{LIGHT_GREEN_CLOSE} - {LEVEL}{{message}}{LEVEL_CLOSE}",
    backtrace=True,
    diagnose=True,
)


logger.add(
    LOG_FILE_PATH,
    rotation=None,
    retention="7 days",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | "
    "{level: <8} | {extra[full_file]: <23} | "
    "{extra[source_with_lineno]: <35} | {message}",
    backtrace=True,
    diagnose=True,
)


colorama.init(autoreset=True)


class Color:
    """颜色类（给终端文字上色的）

    :example:

    >>> print(Color.RED + "Hello, " + Color.End + "World!")
    Hello, World!       (红色Hello，默认颜色的World)

    """

    RED = colorama.Fore.RED if log_settings.draw_color else ""
    "红色"
    GREEN = colorama.Fore.GREEN if log_settings.draw_color else ""
    "绿色"
    YELLOW = colorama.Fore.YELLOW if log_settings.draw_color else ""
    "黄色"
    BLUE = colorama.Fore.BLUE if log_settings.draw_color else ""
    "蓝色"
    MAGENTA = colorama.Fore.MAGENTA if log_settings.draw_color else ""
    "品红色"
    CYAN = colorama.Fore.CYAN if log_settings.draw_color else ""
    "青色"
    WHITE = colorama.Fore.WHITE if log_settings.draw_color else ""
    "白色"
    BLACK = colorama.Fore.BLACK if log_settings.draw_color else ""
    "黑色"
    END = colorama.Fore.RESET if log_settings.draw_color else ""
    "着色结束"
    BOLD = colorama.Style.BRIGHT if log_settings.draw_color else ""
    "加粗"
    UNDERLINE = colorama.Style.DIM if log_settings.draw_color else ""
    "下划线"
    NORMAL = colorama.Style.NORMAL if log_settings.draw_color else ""
    "正常"

    @staticmethod
    @final
    def from_rgb(r: int, g: int, b: int) -> str:
        "从RGB数值中生成颜色"
        return f"\033[38;2;{r};{g};{b}m" if log_settings.draw_color else ""


class                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Logger:
    "日志记录器"

    log_file: Optional[TextIO] = (
        open(
            log_settings.log_file_path,
            "a",
            encoding=log_settings.encoding,
            errors="ignore",
            buffering=1,
        )
        if log_settings.log_file_path
        else None
    )
    "日志文件"

    fast_log_file: Optional[TextIO] = (
        open(
            log_settings.fast_log_file_path,
            "a",
            encoding=log_settings.encoding,
            errors="ignore",
            buffering=1,
        )
        if log_settings.fast_log_file_path
        else None
    )
    "快速日志文件"

    log_settings = log_settings
    "日志配置"

    stdout_orig = stdout_orig
    "原始的输出"

    stderr_orig = stderr_orig
    "原始的错误输出"

    captured_stdout = SystemLogger(
        stdout_orig,
        logger_name="sys.stdout",
        function=lambda m: Logger.log("I", m, "sys.stdout"),
    )
    "经过处理的输出"

    captured_stderr = SystemLogger(
        stderr_orig,
        logger_name="sys.stderr",
        function=lambda m: Logger.log("E", m, "sys.stderr"),
    )
    "经过处理的错误输出"

    log_mutex = Lock()
    "日志互斥锁"

    @staticmethod
    def reopen_log_file():
        "重新打开日志文件"
        if log_settings.log_file_path:
            Logger.log_file.close()
            Logger.log_file = open(
                log_settings.log_file_path,
                "a",
                encoding=log_settings.encoding,
                errors="ignore",
                buffering=1,
            )

    console_log_queue = Queue()
    "控制台日志队列"
    logfile_log_queue = Queue()
    "日志文件日志队列"
    log_file_keepcount = 20
    "日志文件保留数量"
    logger_running = True
    "日志记录器是否在运行（我自己都不知道有没有用，忘了）"
    short_log_info: List[str] = []
    "给主界面用的简短日志信息列表"
    short_log_keep_length: int = 150
    "日志信息保留的条数"
    logged_count: int = 0
    "自启动以来记录过的日志条数"

    if log_style == "new":

        @staticmethod
        def log(
            msg_type: Literal["I", "W", "E", "F", "D", "C"],
            msg: str,
            source: str = "MainThread",
        ):
            """
            向控制台和日志输出信息

            :param level: 日志级别 (I=INFO, W=WARNING,
            E=ERROR, F=CRITICAL, D=DEBUG, C=CRITICAL)
            :param msg: 日志消息
            :param source: 日志来源
            """
            # 如果日志等级太低就不记录
            if (
                (msg_type == "D" and Logger.log_settings.log_level not in ("D"))
                or (msg_type == "I" and Logger.log_settings.log_level not in ("D", "I"))
                or (
                    msg_type == "W"
                    and Logger.log_settings.log_level not in ("D", "I", "W")
                )
                or (
                    msg_type == "E"
                    and Logger.log_settings.log_level not in ("D", "I", "W", "E")
                )
                or (
                    msg_type == "F"
                    or msg_type == "C"
                    and Logger.log_settings.log_level
                    not in ("D", "I", "W", "E", "F", "C")
                )
            ):
                return

            if not isinstance(msg, str):
                msg = repr(msg)
            for m in msg.splitlines():
                if not m.strip():
                    continue
                frame = inspect.currentframe()
                file = frame.f_back.f_code.co_filename.replace(cwd, "")
                if file == "<string>":
                    lineno = 0
                if file.startswith(("/", "\\")):
                    file = file[1:]
                frame = inspect.currentframe()
                caller_frame = frame.f_back
                log_level = {
                    "I": "INFO",
                    "W": "WARNING",
                    "E": "ERROR",
                    "F": "CRITICAL",
                    "C": "CRITICAL",
                    "D": "DEBUG",
                }.get(msg_type, "INFO")

                filename = caller_frame.f_code.co_filename
                file_basename = os.path.basename(filename)
                lineno = caller_frame.f_lineno
                logger.bind(
                    file=file_basename,
                    source=source,
                    lineno=lineno,
                    full_file=file,
                    source_with_lineno=f"{source}:{lineno}",
                ).log(log_level, m)
                short_info = (
                    f"{time.strftime('%H:%M:%S', time.localtime())} {msg_type} {m}"
                )
                Logger.short_log_info.append(short_info)
                short_info = short_info[-Logger.short_log_keep_length :]
                Logger.logged_count += 1

    else:

        @staticmethod
        def log(
            msg_type: Literal["I", "W", "E", "F", "D", "C"],
            msg: str,
            source: str = "MainThread",
        ):
            """
            向控制台和日志输出信息

            :param type: 类型
            :param msg: 信息
            :param send: 发送者
            :return: None
            """
            if Logger.log_settings.use_mutex:
                Logger.log_mutex.acquire()

            if not isinstance(msg, str):
                msg = repr(msg)
            for m in msg.splitlines():
                if msg_type == "I":
                    color = Color.GREEN
                elif msg_type == "W":
                    color = Color.YELLOW
                elif msg_type == "E":
                    color = Color.RED
                elif msg_type == "F" or msg_type == "C":
                    color = Color.MAGENTA
                elif msg_type == "D":
                    color = Color.CYAN
                else:
                    color = Color.WHITE

                if not m.strip():
                    continue
                frame = inspect.currentframe()
                lineno = frame.f_back.f_lineno
                file = frame.f_back.f_code.co_filename.replace(cwd, "")
                if file == "<string>":
                    lineno = 0
                if file.startswith(("/", "\\")):
                    file = file[1:]
                cm = (
                    f"{Color.BLUE}{get_time()}{Color.END} {color}{msg_type}{Color.END} "
                    f"{Color.from_rgb(50, 50, 50)}{source.ljust(35)}{color} {m}{Color.END}"
                )
                lfm = f"{get_time()} {msg_type} {(source + f' -> {file}:{lineno}').ljust(60)} {m}"

                if Logger.fast_log_file:
                    Logger.fast_log_file.write(lfm + "\n")
                    Logger.fast_log_file.flush()

                if log_settings.log_mode == "write_instantly":
                    print(cm, file=Logger.stdout_orig)
                    if Logger.log_file:
                        Logger.log_file.write(lfm + "\n")
                        Logger.log_file.flush()

                elif log_settings.log_mode == "write_buffered":
                    Logger.console_log_queue.put(cm)
                    Logger.logfile_log_queue.put(lfm)

                short_info = (
                    f"{time.strftime('%H:%M:%S', time.localtime())} {msg_type} {m}"
                )
                Logger.short_log_info.append(short_info)
                Logger.short_log_info = Logger.short_log_info[
                    -Logger.short_log_keep_length :
                ]
                Logger.logged_count += 1
            if Logger.log_settings.use_mutex:
                Logger.log_mutex.release()

    @staticmethod
    def log_thread_logfile():
        "把日志写进日志文件的线程的运行函数"
        while Logger.logger_running:
            s = Logger.logfile_log_queue.get()
            Logger.log_file.write(s + "\n")
            Logger.log_file.flush()

    @staticmethod
    def log_thread_console():
        "把日志写在终端的线程的运行函数"
        while Logger.logger_running:
            s = Logger.console_log_queue.get()
            Logger.stdout_orig.write(s + "\n")
            Logger.stdout_orig.flush()

    @staticmethod
    def stop_loggers():
        "停止所有日志记录器"
        Logger.logger_running = False

    console_log_thread = Thread(
        target=lambda: Logger.log_thread_console(),  # pylint: disable=unnecessary-lambda
        daemon=True,
        name="ConsoleLogger",
    )
    "把日志写在终端的线程的线程对象"

    logfile_log_thread = Thread(
        target=lambda: Logger.log_thread_logfile(),  # pylint: disable=unnecessary-lambda
        daemon=True,
        name="FileLogger",
    )
    "把日志写进日志文件的线程的线程对象"

    @staticmethod
    def clear_oldfile(keep_amount: int = 10):
        "清理日志文件"
        if not os.path.exists("log/"):
            return
        log_files = sorted(
            [
                f
                for f in os.listdir(os.path.dirname(LOG_FILE_PATH))
                if f.startswith("ClassManager_") and f.endswith(".log")
            ],
            reverse=True,
        )
        for f in log_files[keep_amount:]:
            os.remove(os.path.join(os.path.dirname(LOG_FILE_PATH), f))

    @staticmethod
    def log_exc(
        info: str = "未知错误：",
        sender="MainThread -> Unknown",
        level: Literal["I", "W", "E", "F", "D", "C"] = "E",
        exc: Exception = None,
    ):
        """向控制台和日志报错。

        :param info: 信息
        :param sender: 发送者
        :param level: 级别
        :param exc: 指定的Exception，可以不传（就默认是最近发生的一次）
        :return: None
        """
        if exc is None:
            exc = sys.exc_info()[1]
            if exc is None:
                return
        Logger.log(level, info, sender)
        Logger.log(
            level,
            ("").join(
                traceback.format_exception(exc.__class__, exc, exc.__traceback__)
            ),
            sender,
        )
        Logger.log(level, "\n".join(format_exc_like_java(exc)), sender)

    @staticmethod
    def log_exc_short(
        info: str = "未知错误：",
        sender="MainThread -> Unknown",
        level: Literal["I", "W", "E", "F", "D", "C"] = "W",
        exc: Exception = None,
    ):
        """
        向控制台和日志报错，但是相对精简，格式为[ERROR_TYPE] INFO

        :param info: 信息
        :param sender: 发送者
        :param level: 级别
        :param exc: 指定的Exception，可以不传（就默认是最近发生的一次）
        :return: None
        """
        if exc is None:
            exc = sys.exc_info()[1]
            if exc is None:
                return
        Logger.log(level, f"{info} [{exc.__class__.__qualname__}] {exc}", sender)


if log_style == "old" and log_settings.log_mode == "write_buffered":
    # 性能能省一点是一点
    Logger.console_log_thread.start()
    Logger.logfile_log_thread.start()

try:
    Logger.clear_oldfile()
except OSError as e:
    Logger.log_exc_short("清理日志文件失败：", exc=e)


if log_style == "new":
    # 启用loguru的异常捕获
    logger.catch(onerror=lambda exc: Logger.log_exc("logger捕获到异常", exc=exc))

consts.stdout = Logger.captured_stdout
consts.stderr = Logger.captured_stderr
