from __future__ import annotations
import re
import threading
import inspect
import time
from typing import Any, Callable, Dict, List, Union
from ..logger import Logger
from ..algorithm.numeric import addrof
from ..profiler import profile
from .tasks import Task
from .event import Event

class BroadcastReceiver:
    """
    广播接收器。

    用于接收广播消息。
    """

    RECEIVED_KEY: str = "__received_tag"

    RECIEVE_ALL: str = "*"

    RE_PATTERN_PREFIX: str = "re:"

    def __init__(self, event_key: str, callback: Callable[..., Any] | Task, name: str | None = None):
        """
        构造函数。

        :param key: 接收器标签, *表示接收所有消息, re:pattern表示接收符合正则表达式的消息
        :param callback: 回调函数
        """
        self.event_key = event_key
        self.callback = callback
        self._signature_cache = None
        self.called_times = 0
        self.name = name or f"BroadcastReceiver(Unnamed_{addrof(self)})"

    def __call__(self, *args: Any, **kwargs: Any):
        "直接调用接收器。"
        args, kwargs = self._adapt_arguments(self.callback, *args, **kwargs)
        return self.callback(*args, **kwargs)

    def receive(self, tag: str, *args: Any, **kwargs: Any):
        """
        接收消息。获取到的实际标签名存储在kwargs[Boardcaster.RECEIVED_KEY]中。

        :param tag: 消息标签
        """
        kwargs.update({BroadcastReceiver.RECEIVED_KEY: tag})
        self.called_times += 1
        return self.run(self.callback, *args, **kwargs)
        
    def receive_async(self, tag: str, *args: Any, **kwargs: Any):
        """
        以异步模式接收消息。获取到的实际标签名存储在kwargs[Boardcaster.RECEIVED_KEY]中。

        :param tag: 消息标签
        """ 
        kwargs.update({BroadcastReceiver.RECEIVED_KEY: tag})
        self.called_times += 1
        return self.run_async(self.callback, *args, **kwargs)
    
    
    def _get_callable(self, callback: Union[Callable[..., Any], Task]) -> Callable[..., Any]:
        "获取实际可调用对象。"
        if isinstance(callback, Task):
            return callback.get_func()
        return callback
    
    def _get_signature(self, callback: Union[Callable[..., Any], Task]):
        "获取函数签名。"
        if self._signature_cache is None:
            callable_obj = self._get_callable(callback)
            self._signature_cache = inspect.signature(callable_obj)
        return self._signature_cache
    
    def _adapt_arguments(self, callback: Union[Callable[..., Any], Task], *args: Any, **kwargs: Any):
        """
        根据函数签名调整参数，只传入函数接受的参数。
        
        :return: 调整后的 (args, kwargs)
        """
        try:
            signature = self._get_signature(callback)
            parameters  = signature.parameters
            
            has_common_kwargs = any(
                param.kind == inspect.Parameter.VAR_KEYWORD 
                for param in parameters.values()
            )
            
            if not has_common_kwargs:
                kwarg_list = [
                    name for name, param in parameters.items()
                    if param.kind in (
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.KEYWORD_ONLY
                    )
                ]
                
                filtered_kwargs = {
                    key: value for key, value in kwargs.items()
                    if key in kwarg_list
                }
            else:
                # 有**kwargs
                filtered_kwargs = kwargs
            
            has_common_args = any(
                param.kind == inspect.Parameter.VAR_POSITIONAL 
                for param in parameters.values()
            )

            if not has_common_args:
                filtered_args = args[: len([param for param in parameters.values() if param.kind in (
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    inspect.Parameter.POSITIONAL_ONLY
                )])] # 瞎写的，鬼晓得会不会报错

            else:
                # 有*args
                filtered_args = args


            bound_args = signature.bind_partial(*filtered_args, **filtered_kwargs)
            bound_args.apply_defaults()
            
            return bound_args.args, bound_args.kwargs
        
        except Exception:
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != "__receiver_tag"}
            Logger.log_exc(f"为广播接收器{self!r}适配参数时出错, 将使用原始参数", "BroadcastReceiver._adapt_arguments", "W")
            return args, filtered_kwargs
    
    def run(self, callback: Callable[..., Any] | Task, *args: Any, **kwargs: Any):
        "运行回调函数（会自动适配参数）"
        func = self._get_callable(callback)
        args, kwargs = self._adapt_arguments(callback, *args, **kwargs)
        return func(*args, **kwargs)
    
    def run_async(self, callback: Callable[..., Any] | Task, *args: Any, **kwargs: Any):
        "异步运行回调函数（会自动适配参数）"
        args, kwargs = self._adapt_arguments(callback, *args, **kwargs)

        if isinstance(callback, Task):
            return callback.start(*args, **kwargs)
        else:
            thread = threading.Thread(
                target=self._safe_run, 
                args=(callback, *args), 
                kwargs=kwargs
            )
            thread.start()
            return thread
    
    def _safe_run(self, callback: Callable[..., Any], *args: Any, **kwargs: Any):
        "安全运行函数，捕获异常"
        try:
            args, kwargs = self._adapt_arguments(callback, *args, **kwargs)
            return callback(*args, **kwargs)
        except Exception:
            Logger.log_exc(f"广播接收器{self!r}运行时出错", "BroadcastReceiver._safe_run", "E")
            raise

    def __repr__(self):
        return f"<BroadcastReceiver key={self.event_key!r} callback={self.callback!r}>"
    




class BroadcastDispatcher:
    """
    广播分发器。
    用于在多个对象之间广播消息。
    """

    dispatchers: Dict[str, BroadcastDispatcher] = {}
    
    def __init__(self, listeners: list[BroadcastReceiver] | None = None, name: str | None = None, is_async: bool = True):
        """
        构造函数。
        
        :param listeners: 初始监听器列表
        :param name: 分发器的名称
        """
        if name in BroadcastDispatcher.dispatchers.keys():
            raise RuntimeError(f"名字为{name}的广播分发器已经存在了")
        listeners = listeners or []
        self.listeners: dict[str, List[BroadcastReceiver]] = {}
        self.is_async = is_async
        for listener in listeners:
            self.add_listener(listener)
        self._lock = threading.Lock()
        self.name = name or f"BroadcastDispatcher(Unnamed_{addrof(self)})"

    @staticmethod
    def as_listener_of(dispatcher: BroadcastDispatcher | str, event_key: str  = BroadcastReceiver.RECIEVE_ALL, name: str | None = None) \
            -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        将一个函数作为一个监听器注册到分发器上。

        :param dipatcher: 分发器
        :param key: 监听器的目标标签
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            nonlocal dispatcher, event_key, name
            if isinstance(dispatcher, str):
                try:
                    dispatcher = BroadcastDispatcher.dispatchers[dispatcher]
                except (IndexError, KeyError) as e:
                    raise RuntimeError(f"没有找到名字为{name}的广播分发器") from e
            dispatcher.add_listener(BroadcastReceiver(event_key, func, name))
            return func
        return decorator


    def listener_count(self, event_key: str | None = None) -> int:
        """
        获取监听器数量。

        :param key: 监听器标签
        """
        with self._lock:
            if event_key is None:
                return sum([len(self.listeners[key]) for key in self.listeners.keys()])
            else:
                return len(self.listeners[event_key]) if event_key in self.listeners else 0

    def add_listener(self, listener: BroadcastReceiver):
        """
        添加监听器。

        :param listener: 监听器
        """
        with self._lock:
            if listener.event_key not in self.listeners:
                self.listeners.setdefault(listener.event_key, [])
            
            if listener not in self.listeners[listener.event_key]:
                self.listeners[listener.event_key].append(listener)


    def remove_listener(self, listener: BroadcastReceiver):
        """
        移除监听器。
        
        :param listener: 监听器
        """
        with self._lock:
            if listener.event_key in self.listeners and listener in self.listeners[listener.event_key]:
                self.listeners[listener.event_key].remove(listener)
                if not self.listeners[listener.event_key]:
                    del self.listeners[listener.event_key]

    register = add_listener
    unregister = remove_listener

    @profile("BroadcastDispatcher.broadcast")
    def broadcast(self, tag: str | Event, *args: Any, **kwargs: Any) -> None:
        """
        广播消息。

        :param tag: 消息标签
        """
        start_time = time.perf_counter()
        
        if isinstance(tag, Event):
            args = tag.args + args
            kwargs = tag.kwargs | kwargs
            tag = tag.event_key

        listener_count = 0
        dispatch_count = 0
        
        with self._lock:
            lock_time = time.perf_counter()
            
            for key in list(self.listeners.keys()):
                if key.startswith(BroadcastReceiver.RE_PATTERN_PREFIX):
                    pattern = key[len(BroadcastReceiver.RE_PATTERN_PREFIX):]
                    match_start = time.perf_counter()
                    if re.match(pattern, tag):
                        match_time = time.perf_counter() - match_start
                        for listener in self.listeners[key]:
                            self._dispatch_to(listener, tag, *args, **kwargs)
                            dispatch_count += 1
                            listener_count += 1
                elif key == BroadcastReceiver.RECIEVE_ALL:
                    for listener in self.listeners[key]:
                        self._dispatch_to(listener, tag, *args, **kwargs)
                        dispatch_count += 1
                        listener_count += 1
                elif key == tag:
                    for listener in self.listeners[key]:
                        self._dispatch_to(listener, tag, *args, **kwargs)
                        dispatch_count += 1
                        listener_count += 1
        
        total_time = time.perf_counter() - start_time
        if total_time > 0.01:  # 超过10ms就记录
            Logger.log("D", f"Broadcast '{tag}' took {total_time*1000:.2f}ms, dispatched to {dispatch_count} listeners, {listener_count} total checks")

    def _dispatch_to(self, listener: BroadcastReceiver, tag: str, *args: Any, **kwargs: Any):
        "分发消息到指定监听器。"
        if self.is_async:
            listener.receive_async(tag, *args, **kwargs)
        else:
            listener.receive(tag, *args, **kwargs)
