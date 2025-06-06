"""
基本类型
"""

import os
import sys
import time
import random
import psutil
import threading
import ctypes
import copy

from .logger import Logger, logger



__all__ = [
    "ModifyingError",
    "DataObject",
    "Object",
    "Base",
    "stdout_orig",
    "stderr_orig"
]

def gen_uuid(length: int = 32) -> str:
    "生成一个长32位的uuid"
    return "".join([str(random.choice("0123456789abcdef")) for _ in range(length)])

os.makedirs(os.getcwd() + "/log", exist_ok=True)

if not os.path.isdir("log"):
    os.mkdir("log")


class ModifyingError(Exception):
    "修改出现错误。"


class DataObject(object):

    def copy(self):
        "给自己复制一次，两个对象不会互相影响"
        return copy.deepcopy(self)

    def __repr__(self):
        "返回这个对象的表达式"
        return (
            f"{self.__class__.__name__}"
            f"({', '.join([f'{k}={v!r}' for k, v in self.__dict__.items() if not k.startswith('_')])})"
        )
        # 我个人认为不要把下划线开头的变量输出出来（不过只以一个下划线开头的还得考虑考虑）


class Object(DataObject):
    "一个基础类"

    @property
    def uuid(self):
        "获取对象的UUID"
        if not hasattr(self, "_uuid") or not getattr(self, "_uuid"):
            self._uuid = gen_uuid()

        return self._uuid

    @uuid.setter
    def uuid(self, value):
        "设置对象的UUID"
        self._uuid = value

    @uuid.deleter
    def uuid(self):
        "删除对象的UUID"
        raise AttributeError("不能删除对象的UUID")

    def refresh_uuid(self):
        self._uuid = gen_uuid()


class Base(Logger, Object):
    "工具基层"

    thread_id = int(
        ctypes.CFUNCTYPE(ctypes.c_long)(ctypes.pythonapi.PyThread_get_thread_ident)()
    )
    # 一种很神奇的获取pid方法
    "当前进程的pid"
    thread_name = threading.current_thread().name
    "当前进程的名称"
    thread = threading.current_thread()
    "当前进程的线程对象"

    @staticmethod
    def utc(precision: int = 3):
        """
        返回当前时间戳

        :param precision: 精度，默认为3
        """
        return int(time.time() * pow(10, precision))

    @staticmethod
    def gettime():
        "获得当前时间"
        lt = time.localtime()
        return (
            f"{lt.tm_year}-{lt.tm_mon:02}-{lt.tm_mday:02} "
            + f"{lt.tm_hour:02}:{lt.tm_min:02}:{lt.tm_sec:02}"
            + f".{int((time.time()%1)*1000):03}"
        )
    
class SysMemTracer:
    "系统内存追踪器"

    def __init__(self, trace_interval: float = 0.1, record_data: bool = False):
        """
        构造一个新的追踪器。

        :param trace_interval: 追踪间隔
        :param record_data: 是否记录数据
        """

        self.trace_interval = trace_interval
        "追踪间隔"
        self.record_data = record_data
        "是否记录数据"
        self.data = {}
        "内存使用数据"
        self.current_usage = 0
        "当前内存使用量"
        self._running = False

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        "开始追踪"
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._trace, name=f"SysMemTracer_{id(self):x}")
        self._thread.start()
    
    def stop(self):
        "停止追踪"
        self._running = False


    def _trace(self):
        "追踪"
        while True:
            self.current_usage = self._get_memory_usage()
            if self.record_data:
                self.data[time.time()] = self.current_usage
            time.sleep(self.trace_interval)

    def _get_memory_usage(self):
        "获取内存使用量"
        return psutil.Process().memory_info().rss


stdout_orig = sys.stdout
stderr_orig = sys.stderr

sys.stdout = Base.captured_stdout
sys.stderr = Base.captured_stderr

if __name__ == "__main__":
    print("你闲的没事跑这玩意干啥")

# elif __name__ == "utils.basetypes":
#     print("基层已初步加载完成")
