"""
数据类型
"""
from __future__ import annotations
import ctypes
import time
from collections.abc import Callable, Iterable, Mapping
from threading import Lock
from threading import Thread as OrigThread
from typing import Any, Generic, TypeVar


class NULLPTR:
    "虽然没用"

    def __eq__(self, value: object) -> bool:
        return isinstance(value, NULLPTR)

    def __ne__(self, value: object) -> bool:
        return not isinstance(value, NULLPTR)

    def __str__(self) -> str:
        return "nullptr"

    def __repr__(self) -> str:
        return "nullptr"

    def __hash__(self):
        return -1

    def __bool__(self):
        return False


null = NULLPTR()
"空指针"


class Node:
    "树节点"

    def __init__(self, value: object, left: object = null, right: object = null):
        self.value = value
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f"Node({self.value}, {self.left}, {self.right})"


DT = TypeVar("DT")


class Stack(Generic[DT]):
    "非常朴素的栈"

    def __init__(self, items: Iterable[DT] | None = None):
        "初始化栈"
        self.items = list(items) if items is not None else []

    def is_empty(self):
        "判断栈是否为空"
        return len(self.items) == 0

    def push(self, item: DT):
        "添加元素到栈顶"
        self.items.append(item)

    def pop(self) -> DT:
        "移除栈顶元素并返回该元素"
        return self.items.pop()

    def peek(self) -> DT:
        "返回栈顶元素"
        return self.items[len(self.items) - 1]

    def size(self):
        "返回栈的大小"
        return len(self.items)

    def clear(self):
        "清空栈"
        self.items = []


class Thread(OrigThread):
    "自己做的一个可以返回数据的Thread"

    def __init__(
        self,
        group: None = None,
        target: Callable | None = None,
        name: str | None = None,
        args: Iterable[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
        *,
        daemon: bool | None = None,
    ) -> None:
        """
        初始化线程

        :param group: 线程组，默认为None
        :param target: 线程函数，默认为None
        :param name: 线程名称，默认为None
        :param args: 线程函数的参数，默认为空元组
        :param kwargs: 线程函数的关键字参数，默认为None
        """
        args = () if args is None else args
        kwargs = {} if kwargs is None else kwargs
        super().__init__(
            group=group,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs,
            daemon=daemon,
        )
        self._return: Any = None
        self._finished = False
        self.thread_id: int | None = None

    @property
    def return_value(self) -> Any:
        "返回线程的返回值"
        if self._finished:
            return self._return
        raise RuntimeError("线程并未执行完成")

    def run(self):
        "运行线程"
        self.thread_id = ctypes.CFUNCTYPE(ctypes.c_long)(lambda: ctypes.pythonapi.PyThread_get_thread_ident())()  # pylint: disable=W0108
        if self._target is not None:  # type: ignore
            self._return = self._target(*self._args, **self._kwargs)  # type: ignore
        self._finished = True

    def join(self, timeout: float | None = None) -> Any:
        """
        等待线程完成并返回结果

        :param timeout: 超时时间，默认为None，表示无限等待
        """
        super().join(timeout=timeout)
        return self._return


class Mutex:
    "互斥锁"

    def __init__(self):
        self._lock = Lock()

    def acquire(self):
        "获取锁"
        self._lock.acquire()

    def release(self):
        "释放锁"
        self._lock.release()

    def __enter__(self):
        "进入上下文管理器"
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        "退出上下文管理器"
        self.release()
        return False

    def locked(self):
        "判断锁是否被占用"
        return self._lock.locked()

    def __bool__(self):
        "判断锁是否被占用"
        return self.locked()

    def __repr__(self):
        return f"Mutex(locked={self.locked()})"


class FrameCounter:
    "帧计数器"

    def __init__(self, maxcount: int | None = None, timeout: float | None = None):
        "初始化帧计数器"
        self.maxcount = maxcount
        self.timeout = timeout
        self.counted_frames = 0
        self.running = False
        self.start_time: Optional[float] = None

    @property
    def elapsed_time(self) -> float:
        "获取当前时间戳"
        return 0 if not self.running else time.time() - self.start_time # type: ignore

    @property
    def framerate(self):
        "获取帧率"
        if self.counted_frames == 0 or not self.running:
            return 0
        return self.counted_frames / self.elapsed_time


    def start(self):
        "启动计数器"
        if self.running:
            raise RuntimeError("这个计数器已经启动过了！")
        self.start_time = time.time()
        Thread(target=self.run).start()

    def stop(self):
        "停止计数器"
        self.running = False

    def run(self):
        "启动计数器"
        if self.running:
            raise RuntimeError("这个计数器已经启动过了！")
        self.counted_frames = 0
        self.running = True
        while (
                (self.maxcount is None or self.counted_frames < self.maxcount)
            and (self.timeout is None or time.time() - self.elapsed_time <= self.timeout)
            and self.running
        ):
            self.counted_frames += 1

