
import time
from abc import ABC


from typing import Callable, Any, final
from typing_extensions import override

from ..algorithm.datatypes import Thread
from ..algorithm.numeric import addrof
from .event import Event

class EventBuffer(ABC):

    def __init__(self, callback: Callable[..., Any], name: str | None = None):
        self.callback = callback
        self.buffer: list[Event] = []
        self.listener: Thread | None = None
        self.name = name or f"EventBuffer({addrof(self)})"
        self._listening: bool = False
        self._should_stop: bool = False
        "当检测到这个值为true时，停止监听。"

    def listen(self):
        """
        监听事件的具体实现。这个函数将会在开始监听时在一个单独的线程中运行。

        （记得注意should_stop的处理）
        """
        ...


    def submit(self, event: Event):
        "向缓冲区提交一个事件。"
        self.buffer.append(event)

    def process(self):
        "处理缓冲区中的事件。"
        while self.buffer:
            event = self.buffer.pop(0)
            self.execute(event=event)

    @final
    def start_listening(self):
        "开始监听事件。"
        if self._listening:
            raise RuntimeError("事件缓冲区已经在监听中")
        self._should_stop = False
        self.listener = Thread(target=self.listen, name=f"ListenerThread({self.name})", daemon=True)
        self.listener.start()

    @final
    def is_listening(self) -> bool:
        "返回当前是否正在监听事件。"
        return self._listening

    @final
    def stop_listening(self):
        "停止监听事件。"
        if not self._listening:
            raise RuntimeError("事件缓冲区没有在监听中")
        self._should_stop = True
        if self.listener:
            self.listener.join()
            self.listener = None
        self.listener = None
        self._listening = False

    @final
    def execute(self, *args: Any, **kwargs: Any):
        "执行回调函数。"
        self.callback(*args, **kwargs)

    @final
    def get_callback(self) -> Callable[..., Any]:
        "获取回调函数。"
        return self.callback
    
    @final
    def set_callback(self, callback: Callable[..., Any]):
        "设置回调函数。"
        self.callback = callback

    @final
    def get_buffer(self) -> list[Event]:
        "获取当前缓冲区内容。"
        return self.buffer
    
    @final
    def clear_buffer(self):
        "清空缓冲区。"
        self.buffer.clear()


    def __repr__(self):
        return f"{self.__class__.__name__}(callback={self.callback}, name={self.name}, listening={self._listening}, buffer={self.buffer})"



class FilteredEventBuffer(EventBuffer, ABC):
    """
    过滤事件缓冲区。

    这个缓冲区会过滤掉一些不符合条件的事件。
    """

    def __init__(self, callback: Callable[..., Any], filter: Callable[[Event], bool], name: str | None = None):
        """
        构造函数。
        
        :param callback: 对事件进行处理的回调函数
        :type callback: Callable[..., Any]
        :param filter: 过滤函数，返回True则接受该事件，False则丢弃
        :type filter: Callable[[str], bool]
        :param name: 缓冲区名称
        :type name: str | None
        """
        super().__init__(callback, name)
        self._filter = filter

    def submit(self, event: Event):
        if self._filter(event):
            super().submit(event)

    def get_filter(self) -> Callable[[Event], bool]:
        "获取过滤函数。"
        return self._filter
    
    def set_filter(self, filter: Callable[[Event], bool]):
        "设置过滤函数。"
        self._filter = filter


class TimedEventBuffer(EventBuffer):
    """
    定时事件缓冲区。

    只有当事件在缓冲区中达到一定时间不增加或者达到数量上限时，才会触发处理函数。
    """

    def __init__(self, callback: Callable[..., Any], 
                    interval: float = 1.0, 
                    recheck_time: float = 0.01,
                    max_events: int = 65535,
                    name: str | None = None):
        """
        构造函数。

        :param callback: 对事件进行处理的回调函数
        :type callback: Callable[..., Any]
        :param interval: 事件缓冲区中事件的最大未更新间隔
        :type interval: float
        :param recheck_time: 监听线程检查缓冲区是否过期的时间间隔
        :type recheck_time: float
        :param max_events: 事件缓冲区中事件的最大数量
        :type max_events: int
        :param name: 缓冲区名称
        :type name: str | None
        """ 
        super().__init__(callback, name)
        self._interval = interval
        self._last_event_time: float | None = None
        self._recheck_time = recheck_time
        self._max_events = max_events

    def __del__(self):
        """
        析构函数。会停止监听来释放资源。
        """
        self.stop_listening()

    @override
    def submit(self, event: Event):
        """
        提交事件到缓冲区。

        :param event: 要提交的事件
        :type event: Event
        """
        super().submit(event)
        self._last_event_time = time.time()

    def listen(self):
        "监听事件。用来检测缓冲区是否过期。"
        self._listening = True
        while not self._should_stop:
            # Logger.log("T", f"监听事件缓冲区 {self.name}，当前事件数量：{len(self.buffer)}", "TimedEventBuffer.listen")
            if len(self.buffer) >= self._max_events:
                self.deal_with_buffer()
            if self._last_event_time and time.time() - self._last_event_time >= self._interval:
                self.deal_with_buffer()
            time.sleep(self._recheck_time)
        self._listening = False

    def deal_with_buffer(self):
        "处理缓冲区中的事件。"
        self.process()
        self.clear_buffer()
        self._last_event_time = None

    def get_interval(self) -> float:
        """
        获取事件缓冲区中事件的最大未更新处理间隔。
        
        （也就是说，如果超过这个时间没有任何新事件进入缓冲区，就会触发process函数）
        """
        return self._interval
    
    def set_interval(self, interval: float):    
        """
        设置事件缓冲区中事件的最大未更新处理间隔。

        :param interval: 时间间隔，单位为秒
        :type interval: float
        """
        self._interval = interval

    def get_recheck_time(self) -> float:
        "获取事件缓冲区中事件的最大未更新处理间隔。"
        return self._recheck_time
    
    def set_recheck_time(self, recheck_time: float):
        "设置事件缓冲区中事件的最大未更新处理间隔。"
        self._recheck_time = recheck_time

    def process(self):
        """处理缓冲区中的事件。子类可以重写此方法来自定义处理逻辑。"""
        while self.buffer:
            event = self.buffer.pop(0)
            self.execute(event=event)
    

class CountedEventBuffer(EventBuffer):
    """
    计数事件缓冲区。

    只有当事件在缓冲区中达到一定数量时，才会触发处理函数。
    """

    def __init__(self, callback: Callable[..., Any], 
                    max_buffer_size: int = 114514,
                    name: str | None = None):
        """
        构造函数。

        :param callback: 对事件进行处理的回调函数
        :type callback: Callable[..., Any]
        :param max_buffer_size: 事件缓冲区中事件的最大数量
        :type max_buffer_size: int
        :param name: 缓冲区名称
        :type name: str | None
        """
        super().__init__(callback, name=name)
        self._buffer_size = 0
        self._max_buffer_size = max_buffer_size

    def deal_with_buffer(self):
        "处理缓冲区中的事件。"
        self.process()
        self.clear_buffer()
        self._buffer_size = 0
    
    def submit(self, event: Event):
        self._buffer_size += 1
        if self._buffer_size > self._max_buffer_size:
            self.deal_with_buffer()
        super().submit(event)


    def get_max_buffer_size(self) -> int:
        "获取事件缓冲区中事件的最大数量。"
        return self._max_buffer_size
    
    def set_max_buffer_size(self, max_buffer_size: int):
        "设置事件缓冲区中事件的最大数量。"
        self._max_buffer_size = max_buffer_size

    def process(self):
        """处理缓冲区中的事件，子类可以重写此方法来自定义处理逻辑。"""
        while self.buffer:
            event = self.buffer.pop(0)
            self.execute(event=event)


