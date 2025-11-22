"""
任务类。
"""

from __future__ import annotations
import time
import threading
from typing import Callable, Any
from ..basetypes import Object


class Task(Object):

    
    """
    一个任务类。
    """

    def __init__(self, 
                    func: Callable[..., Any], 
                    args: tuple[Any, ...] | None = None, 
                    kwargs: dict[str, Any] | None = None,
                    *,
                    daemon: bool = False,
                    delay: float |  None = None,
                    raise_errors_if_no_handler: bool = True,
                    on_error: Callable[[BaseException], Any] | None = None,
                    repeat: int | None = None,
                    repeat_interval: float | None = None,
                    repeat_interrputs_on_error: bool = False,
                    multi_threaded: bool = True,
                    multi_threading_blocks: bool = False,
                    name: str | None = None
                    ) -> None:
        """
        构造函数。构造一个新的任务。

        :param func: 任务函数
        :param args: 任务函数的参数
        :param kwargs: 任务函数的关键字参数

        :param delay: 延迟执行的时间，单位为秒，None则立即执行
        :param raise_errors_if_no_handler: 如果没有设置错误处理函数，是否抛出错误
        :param on_error: 任务执行发生错误时的回调函数，None则不处理错误
        
        :param repeat: 重复执行的次数，None则不重复
        :param repeat_interval: 重复执行的时间间隔，单位为秒 (如果启用重复执行)
        :param repeat_interrputs_on_error: 如果重复执行时发生错误，是否中断重复执行 (如果启用重复执行)

        :param multi_threaded: 是否允许多线程执行
        :param multi_threading_blocks: 多线程是否阻塞 (如果启用多线程)

        :param name: 任务名称
        """
        self._func = func
        self._args = args or ()
        self._kwargs = kwargs or {}
        self._delay = delay
        self._repeat = repeat
        self._repeat_interval = repeat_interval
        self._multi_threaded = multi_threaded
        self._raise_errors_if_no_handler = raise_errors_if_no_handler
        self._multi_threading_use_lock = multi_threading_blocks
        self._daemon = daemon
        self._repeat_interrputs_on_error = repeat_interrputs_on_error
        self._on_error = on_error
        self._name = name
        self._multi_threading_lock = threading.Lock()
        self._total_running_tasks = 0


        
    def set_pargs(self, args: tuple[Any, ...] | None) -> None:
        "设置任务函数的位置参数。"
        self._args = args or ()

    def set_kwargs(self, kwargs: dict[str, Any] | None) -> None:
        "设置任务函数的关键字参数。"
        self._kwargs = kwargs or {}

    def set_args(self, args: tuple[Any, ...] | None, kwargs: dict[str, Any] | None) -> None:
        "设置任务函数的参数。"
        self.set_pargs(args)
        self.set_kwargs(kwargs)

    def enable_multi_threading(self, blocks: bool = False):
        """
        启用多线程执行。
        
        :param use_lock: 是否使用锁来保证多线程安全
        """
        self._multi_threaded = True
        self._multi_threading_use_lock = blocks

    def disable_multi_threading(self):
        """
        关闭多线程执行。

        如果任务正在运行中，再次启动了任务，则会报错。
        """
        self._multi_threaded = False

    def enable_repeat(self, repeat: int, repeat_interval: float, interrputs_on_error: bool = False):
        """
        启用重复执行。

        :param repeat: 重复执行的次数
        :param repeat_interval: 重复执行的时间间隔，单位为秒
        :param interrputs_on_error: 如果重复执行时发生错误，是否中断重复执行
        """
        if (repeat <= 0):
            raise ValueError("重复次数不能小于0")
        self._repeat = repeat
        self._repeat_interval = repeat_interval
        self._repeat_interrputs_on_error = interrputs_on_error

    def disable_repeat(self):
        "关闭重复执行。"
        self._repeat = None
        self._repeat_interval = None

    def enable_delay(self, delay: float):
        """
        启用延迟执行。

        :param delay: 延迟执行的时间，单位为秒
        """
        if (delay < 0):
            raise ValueError("延迟时间不能小于0")
        self._delay = delay

    def disable_delay(self):
        "关闭延迟执行。"
        self._delay = None

    def force_unlock(self):
        "强制解锁多线程锁。"
        self._multi_threading_lock.release()

    def set_error_handler(self, handler: Callable[[BaseException], Any]):
        "设置任务执行发生错误时的回调函数。"
        self._on_error = handler

    def set_raise_errors_if_no_handler(self, value: bool):
        "设置如果没有设置错误处理函数，是否抛出错误。"
        self._raise_errors_if_no_handler = value

    def set_daemon(self, value: bool):
        "设置任务是否为守护线程。"
        self._daemon = value

    def set_name(self, name: str):
        "设置任务名称。"
        self._name = name

    def running_tasks(self) -> int:
        "获取当前正在运行的任务数量。"
        return self._total_running_tasks
    
    def is_running(self) -> bool:
        "判断任务有任务正在运行。"
        return self._total_running_tasks > 0

    def run(self, *args: Any, **kwargs: Any) -> None:
        "执行任务。"
        args = args or self._args
        kwargs = kwargs or self._kwargs
        multi_threaded = self._multi_threaded
        multi_threading_use_lock = self._multi_threading_use_lock
        delay = self._delay
        repeat = self._repeat
        repeat_interval = self._repeat_interval
        self._total_running_tasks += 1
        if multi_threaded and multi_threading_use_lock:
            self._multi_threading_lock.acquire()
        if (not multi_threaded) and self.is_running():
            raise RuntimeError("任务正在运行中")
        if delay:
            time.sleep(delay)
        for _ in range(repeat or 1):
            try:
                self._func(*args, **kwargs)
            except BaseException as e:
                if self._on_error:
                    self._on_error(e)
                else:
                    if self._raise_errors_if_no_handler:
                        self._total_running_tasks -= 1
                        raise
            if repeat_interval:
                time.sleep(repeat_interval)
        if multi_threaded and multi_threading_use_lock:
            self._multi_threading_lock.release()
        self._total_running_tasks -= 1

    def start(self, *args: Any, **kwargs: Any) -> None:
        "启动任务。"
        if (not self._multi_threaded) and self.is_running():
            raise RuntimeError("任务正在运行中")
        threading.Thread(target=self.run, args=args, kwargs=kwargs, name="Task(" + (self._name or "Unnamed") + ")").start()

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        "等效于Task.start。"
        self.start(*args, **kwargs)


    def join(self, timeout: float = -1, recheck_interval: float = 0.001) -> None:
        """
        等待所有任务完成。

        :param timeout: 超时时间，单位为秒，-1表示不超时
        :param recheck_interval: 检查任务是否完成的间隔时间，单位为秒
        """

        st = time.time()
        while self.is_running():
            if timeout >= 0 and time.time() - st >= timeout:
                raise RuntimeError("任务超时")
            time.sleep(recheck_interval)


__all__ = ["Task"]