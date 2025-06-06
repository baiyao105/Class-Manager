"""
数据类型
"""

import time
import ctypes
from threading import Thread as OrigThread, Lock
from typing import Any, Callable, Generic, Iterable, Mapping, Optional, TypeVar



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

    def __init__(self, items: Iterable[DT] = None):
        "初始化栈"
        self.items = list(items) if items is not None else []

    def is_empty(self):
        "判断栈是否为空"
        return len(self.items) == 0

    def push(self, item):
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
        target: Optional[Callable] = None,
        name: Optional[str] = None,
        args: Iterable[Any] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        *,
        daemon: Optional[bool] = None,
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
        self._return = None
        self._finished = False
        self.thread_id: Optional[int] = None

    @property
    def return_value(self):
        "返回线程的返回值"
        if self._finished:
            return self._return
        else:
            raise RuntimeError("线程并未执行完成")

    def run(self):
        "运行线程"
        self.thread_id = ctypes.CFUNCTYPE(ctypes.c_long)(
            lambda: ctypes.pythonapi.PyThread_get_thread_ident()
        )()  # pylint: disable=W0108
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
        self._finished = True

    def join(self, timeout: Optional[float] = None) -> Any:
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

    def __init__(self, maxcount: Optional[int] = None, timeout: Optional[float] = None):
        "初始化帧计数器"
        self.maxcount = maxcount
        self.timeout = timeout
        self._c = 0
        self.running = False

    @property
    def _t(self):
        "获取当前时间戳"
        return time.time()

    @property
    def framerate(self):
        "获取帧率"
        if self._c == 0 or not self.running:
            return 0
        return self._c / self._t

    def start(self):
        "启动计数器"
        if self.running:
            raise RuntimeError("这个计数器已经启动过了！")
        self._c = 0
        self.running = True
        while (
            (self.maxcount is None or self._c < self.maxcount)
            and (self.timeout is None or time.time() - self._t <= self.timeout)
            and self.running
        ):
            self._c += 1

    def stop(self):
        "停止计数器"
        self.running = False
