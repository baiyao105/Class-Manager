"""
日志记录器
"""
from __future__ import annotations
import inspect
import os
import re
import sys
import time
import datetime
import traceback
from queue import Queue
from threading import Lock, Thread
from typing import Any, Dict, Literal, NamedTuple, TextIO, final, Optional, List, Callable

import colorama
from loguru import logger

from . import consts
from .consts import LOG_PATH, cwd, log_style, stderr_orig, stdout_orig
from .system import SystemLogger



def get_function_namespace(func: object) -> str:
    """
    获取函数的命名空间

    :param func: 函数对象
    :return: 函数的命名空间字符串
    """
    module = inspect.getmodule(func)
    if not hasattr(func, "__module__"):
        try:
            return func.__qualname__    # type: ignore
        except (AttributeError, TypeError, ValueError, NameError):
            try:
                return func.__name__ # type: ignore
            except (AttributeError, TypeError, ValueError, NameError):
                if isinstance(func, property):
                    return str(func.fget.__qualname__)
                elif isinstance(func, classmethod):
                    return str(func.__func__.__qualname__) # type: ignore
                try:
                    return func.__class__.__qualname__ # type: ignore
                except (AttributeError, TypeError, ValueError, NameError):
                    return func.__class__.__name__ # type: ignore
    if module is None:
        module_name = ( # type: ignore
            func.__self__.__module__ if hasattr(func, "__self__") else func.__module__ # type: ignore
        ) 
    else:
        module_name = module.__name__

    return f"{module_name}.{func.__qualname__}" # type: ignore


def format_exc_like_java(exc: BaseException) -> List[str]:
    "不是我做这东西有啥用啊"
    result = [
        f"{get_function_namespace(exc.__class__)}: " + (str(exc) if str(exc).strip() else "no further information"),
        "Stacktrace:",
    ]
    tb = exc.__traceback__
    while tb is not None:
        frame = tb.tb_frame
        filename = frame.f_code.co_filename
        filename_strip = filename
        lineno = tb.tb_lineno
        funcname = frame.f_code.co_name
        _locals = frame.f_locals.copy()
        instance = None
        method_obj = None
        for i in _locals.values():
            if isinstance(i, object) and hasattr(i, "__class__"):
                instance = i
                class_obj = instance.__class__
                method_obj = getattr(class_obj, funcname, None)
                if method_obj:
                    break
        if instance and method_obj:
            full_path = get_function_namespace(method_obj)
            result.append(f"  at {full_path}({filename_strip}:{lineno})")
        else:
            func_obj = frame.f_globals.get(funcname) or frame.f_locals.get(funcname)
            if func_obj:
                qualname = get_function_namespace(func_obj)
                result.append(f"  at {qualname}({filename_strip}:{lineno})")
        tb = tb.tb_next
    return result


def get_function_module(func: object | Callable[..., Any]) -> str:
    "获取函数的模块"
    module = inspect.getmodule(func)
    if module is None:
        module_name = ( # type: ignore
            func.__self__.__module__ if hasattr(func, "__self__") else func.__module__ # type: ignore
        )
    else:
        module_name = module.__name__
    return module_name # type: ignore


def get_time():
    "获得当前时间"
    lt = time.localtime()
    return (
        f"{lt.tm_year}-{lt.tm_mon:02}-{lt.tm_mday:02} "
        + f"{lt.tm_hour:02}:{lt.tm_min:02}:{lt.tm_sec:02}"
        + f".{int((time.time() % 1) * 1000):03}"
    )


LOG_FILE_PATH = os.path.join(
    LOG_PATH,
    f"ClassManager_log_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        + f"_{str(int((time.time() % 1) * 1000000)).zfill(6)}.log"
)    

LOG_FILE_PATTERN = r"^ClassManager_log_.+.log$"


class LoggerSettings:
    "日志配置"

    def __init__(
        self,
        log_file_path: str | None = LOG_FILE_PATH,
        fast_log_file_path: str | None = None,
        console_wrapper: TextIO | None = stdout_orig,
        log_mode: Literal["write_instantly", "write_buffered"] = "write_buffered",
        log_level: Literal["T", "I", "W", "E", "F", "D", "C", "OFF"] = "D",
        draw_color: bool = True,
        use_mutex: bool = False,
        encoding: str | None = "utf-8",
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
default_encoding = "utf-8"
"get_log_file没有指定encoding参数时使用的编码"

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



def get_log_file(path: Optional[str], encoding: Optional[str] = None) -> Optional[TextIO]:
    if not path: return None
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    return open(path, "a", encoding=encoding or default_encoding, errors="ignore", buffering=1)

    

class Logger:
    "日志记录器"

    log_file: TextIO | None = get_log_file(log_settings.log_file_path, log_settings.encoding)
    "日志文件"

    fast_log_file: TextIO | None = get_log_file(log_settings.fast_log_file_path, log_settings.encoding)
    "快速日志文件"

    config = log_settings
    "日志配置"

    stdout_orig = stdout_orig
    "原始的输出"

    stderr_orig = stderr_orig
    "原始的错误输出"

    stdout_redirector = SystemLogger(
        stdout_orig,
        logger_name="sys.stdout",
        function=lambda m: Logger.log("I", m, "sys.stdout"),
    )
    "经过处理的输出"

    stderr_redirector = SystemLogger(
        stderr_orig,
        logger_name="sys.stderr",
        function=lambda m: Logger.log("E", m, "sys.stderr"),
    )
    "经过处理的错误输出"

    log_mutex = Lock()
    "日志互斥锁"


    TRACE: str = "TRACE"
    DEBUG: str = "DEBUG"
    INFO: str = "INFO"
    WARN: str = "WARNING"
    ERROR: str = "ERROR"
    CRITICAL: str = "CRITICAL"
    FATAL: str = CRITICAL

    console_log_queue: Queue[str] = Queue()
    "控制台日志队列"
    logfile_log_queue: Queue[str] = Queue()
    "日志文件日志队列"
    log_file_keepcount = 20
    "日志文件保留数量"
    logger_running = True
    "日志记录器是否在运行（我自己都不知道有没有用，忘了）"
    short_log_info: list[str] = []
    "给主界面用的简短日志信息列表"
    short_log_keep_length: int = 150
    "日志信息保留的条数"
    logged_count: int = 0
    "自启动以来记录过的日志条数"

    @staticmethod
    def set_capture_stdstream(stdout: bool = True, stderr: bool = True):
        "设置是否捕获标准输出和错误输出"
        if stdout:
            sys.stdout = Logger.stdout_redirector
            consts.stdout = Logger.stdout_redirector
        else:
            sys.stdout = Logger.stdout_orig
            consts.stdout = Logger.stdout_orig

        if stderr:
            sys.stderr = Logger.stdout_redirector
            consts.stderr = Logger.stdout_redirector
        else:
            sys.stderr = Logger.stderr_orig
            consts.stderr = Logger.stderr_orig

    @staticmethod
    def reopen_log_file():
        "重新打开日志文件"
        if log_settings.log_file_path:
            if Logger.log_file:
                Logger.log_file.close()
            Logger.log_file = get_log_file(log_settings.log_file_path, log_settings.encoding)

    @staticmethod
    def close_log_file():
        if Logger.log_file:
            Logger.log_file.close()
    
    @staticmethod
    def close_fast_log_file():
        if Logger.fast_log_file:
            Logger.fast_log_file.close()



    @staticmethod
    def get_fullname(level: str):
        "获取日志等级的完整名称"
        return {
            "T": Logger.TRACE,
            "D": Logger.DEBUG,
            "I": Logger.INFO,
            "W": Logger.WARN,
            "E": Logger.ERROR,
            "F": Logger.FATAL,
            "C": Logger.CRITICAL
        }.get(level, level)
    
    @staticmethod
    def get_shortname(level: str):
        "获取日志等级的短名"
        return {
            Logger.TRACE: "T",
            Logger.DEBUG: "D",
            Logger.INFO: "I",
            Logger.WARN: "W",
            Logger.ERROR: "E",
            Logger.FATAL: "C",
            Logger.CRITICAL: "F"
        }.get(level, level)
    
    @staticmethod
    def get_level_index(level: str):
        "获取日志等级的索引"
        return {
            Logger.TRACE: -1,
            Logger.DEBUG: 0,
            Logger.INFO: 1,
            Logger.WARN: 2,
            Logger.ERROR: 3,
            Logger.CRITICAL: 4,
            Logger.FATAL: 4
        }.get(Logger.get_fullname(level), 1145)

    @staticmethod
    def get_level_color(level: str):
        return {
            Logger.TRACE: Color.BLUE,
            Logger.DEBUG: Color.CYAN,
            Logger.INFO: Color.GREEN,
            Logger.WARN: Color.YELLOW,
            Logger.ERROR: Color.RED,
            Logger.CRITICAL: Color.MAGENTA,
            Logger.FATAL: Color.MAGENTA
        }.get(Logger.get_fullname(level), Color.WHITE)
    
    class LogInfo(NamedTuple):
        "一个日志的信息。"
        level: str
        source: str
        file: str
        file_basename: str
        lineno: int
        message: str

    @staticmethod
    def _new_logger(context: LogInfo) -> None:
        logger.bind(
            file=context.file_basename,
            source=context.source,
            lineno=context.lineno,
            full_file=context.file,
            source_with_lineno=f"{context.source}:{context.lineno}",
        ).log(context.level, context.message)

    @staticmethod
    def _old_logger(context: LogInfo) -> None:
        color = Logger.get_level_color(context.level)
        msg_type = Logger.get_shortname(context.level)
        cm = (
            f"{Color.BLUE}{get_time()}{Color.END} {color}{msg_type}{Color.END} "
            f"{Color.from_rgb(50, 50, 50)}{context.source.ljust(35)}{color} {context.message}{Color.END}"
        )
        lfm = f"{get_time()} {msg_type} {(context.source + f' -> {context.file}:{context.lineno}').ljust(60)} {context.message}"

        if Logger.fast_log_file:
            Logger.fast_log_file.write(lfm + "\n")
            Logger.fast_log_file.flush()

        if log_settings.log_mode == "write_instantly":
            Logger.stdout_orig.writelines([cm])
            if Logger.log_file:
                Logger.log_file.write(lfm + "\n")
                Logger.log_file.flush()

        elif log_settings.log_mode == "write_buffered":
            Logger.console_log_queue.put(cm)
            Logger.logfile_log_queue.put(lfm)

    LogHandler = Callable[[LogInfo], Any]

    log_handlers: Dict[str, LogHandler] = {
        "new": _new_logger,
        "old": _old_logger
    }

    @staticmethod
    def _handle_log(context: LogInfo):
        handler = Logger.log_handlers.get(log_style)
        if handler:
            handler(context)

    @staticmethod
    def log(
        msg_type: Literal["T", "I", "W", "E", "F", "D", "C"],
        msg: Any,
        source: str = "MainThread",
    ):
        """
        向控制台和日志输出信息

        :param level: 日志级别 (T=TRACE, I=INFO, W=WARNING,
        E=ERROR, F=CRITICAL, D=DEBUG, C=CRITICAL)
        :param msg: 日志消息
        :param source: 日志来源
        """
        # 如果日志等级太低就不记录
        if Logger.get_level_index(msg_type) < Logger.get_level_index(log_settings.log_level):
            return
        
        log_level = Logger.get_fullname(msg_type)
        
        if log_settings.use_mutex:
            Logger.log_mutex.acquire()
        
        if not isinstance(msg, str):
            msg = repr(msg)
            
        for m in msg.splitlines():
            if not m.strip():
                continue
            frame = inspect.currentframe()
            caller_frame = frame.f_back if frame else None
            if frame and frame.f_back and caller_frame:
                file = frame.f_back.f_code.co_filename.replace(cwd, "")
                if file == "<string>":
                    lineno = 0
                while file.startswith(("/", "\\")):
                    file = file[1:]
                frame = inspect.currentframe()
                
                filename = caller_frame.f_code.co_filename
                file_basename = os.path.basename(filename)
                lineno = caller_frame.f_lineno
            else:
                file_basename = "unknown"
                source = "unknown"
                lineno = -1
                file = "unknown"

            context = Logger.LogInfo(
                level=log_level,
                source=source,
                file=file,
                file_basename=file_basename,
                lineno=lineno,
                message=m
            )

            Logger._handle_log(context)
                
            short_info = (
                f"{time.strftime('%H:%M:%S', time.localtime())} {msg_type} {m}"
            )
            Logger.short_log_info.append(short_info)
            Logger.short_log_info = Logger.short_log_info[-Logger.short_log_keep_length :]
            Logger.logged_count += 1
        if Logger.config.use_mutex:
            Logger.log_mutex.release()

    @staticmethod
    def log_thread_logfile():
        "把日志写进日志文件的线程的运行函数"
        while Logger.logger_running:
            s = Logger.logfile_log_queue.get()
            if Logger.log_file:
                Logger.log_file.write(s + "\n")
                Logger.log_file.flush()

    @staticmethod
    def log_thread_console():
        "把日志写在终端的线程的运行函数"
        while Logger.logger_running:
            s = Logger.console_log_queue.get()
            if Logger.stdout_orig:
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
        if not os.path.isdir(LOG_PATH):
            return
        log_files = sorted(
            [f for f in os.listdir(LOG_PATH) if re.match(LOG_FILE_PATTERN, f)],
            reverse=True
        )
        for f in log_files[keep_amount:]:
            os.remove(os.path.join(LOG_PATH, f))

    @staticmethod
    def log_exc(
        info: str = "未知错误：",
        sender: str ="MainThread -> Unknown",
        level: Literal["I", "W", "E", "F", "D", "C"] = "E",
        exc: Optional[BaseException] = None,
    ):
        """
        向控制台和日志报错。

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
            ("").join(traceback.format_exception(exc.__class__, exc, exc.__traceback__)),
            sender,
        )
        Logger.log(level, "\n".join(format_exc_like_java(exc)), sender)

    @staticmethod
    def log_exc_short(
        info: str = "未知错误：",
        sender: str ="MainThread -> Unknown",
        level: Literal["I", "W", "E", "F", "D", "C"] = "W",
        exc: Optional[BaseException] = None,
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

# Logger.set_capture_stdstream()

__all__ = ["Color", "Logger", "LoggerSettings", "log_settings"]
