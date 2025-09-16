"""事件总线实现

提供事件的发布、订阅和异步处理功能
"""

import logging
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from typing import Any, Callable, Optional

from .event_types import Event, EventType


class EventSubscriber:
    """事件订阅者

    封装事件处理器的相关信息
    """

    def __init__(
        self, handler: Callable, priority: int = 0, async_handler: bool = False, filter_func: Optional[Callable] = None
    ):
        """初始化订阅者

        Args:
            handler: 事件处理函数
            priority: 处理优先级（数字越大优先级越高）
            async_handler: 是否为异步处理器
            filter_func: 事件过滤函数
        """
        self.handler = handler
        self.priority = priority
        self.async_handler = async_handler
        self.filter_func = filter_func
        self.subscriber_id = id(handler)
        self.call_count = 0
        self.error_count = 0
        self.last_called = None

    def can_handle(self, event: Event) -> bool:
        """判断是否可以处理该事件

        Args:
            event: 事件对象

        Returns:
            是否可以处理
        """
        if self.filter_func:
            return self.filter_func(event)
        return True

    def __call__(self, event: Event) -> Any:
        """调用处理器

        Args:
            event: 事件对象

        Returns:
            处理结果
        """
        self.call_count += 1
        self.last_called = time.time()

        try:
            return self.handler(event)
        except Exception as e:
            self.error_count += 1
            raise


class EventBus:
    """事件总线

    提供事件的发布、订阅和处理功能，支持同步和异步处理
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化事件总线"""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.logger = logging.getLogger(self.__class__.__name__)

        # 订阅者管理
        self._subscribers: dict[EventType, list[EventSubscriber]] = defaultdict(list)
        self._global_subscribers: list[EventSubscriber] = []

        # 事件队列和处理
        self._event_queue: Queue = Queue()
        self._processing = False
        self._thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="EventBus")

        # 统计信息
        self._stats = {"events_published": 0, "events_processed": 0, "events_failed": 0, "subscribers_count": 0}

        # 配置
        self._max_queue_size = 1000
        self._enable_async = True
        self._retry_failed_events = True
        self._max_retries = 3

        # 启动事件处理线程
        self._start_processing()

    def subscribe(
        self,
        event_type: EventType,
        handler: Callable,
        priority: int = 0,
        async_handler: bool = False,
        filter_func: Optional[Callable] = None,
    ) -> str:
        """订阅事件

        Args:
            event_type: 事件类型
            handler: 事件处理函数
            priority: 处理优先级
            async_handler: 是否为异步处理器
            filter_func: 事件过滤函数

        Returns:
            订阅者ID
        """
        subscriber = EventSubscriber(handler, priority, async_handler, filter_func)

        # 按优先级插入
        subscribers = self._subscribers[event_type]
        inserted = False
        for i, existing_subscriber in enumerate(subscribers):
            if subscriber.priority > existing_subscriber.priority:
                subscribers.insert(i, subscriber)
                inserted = True
                break

        if not inserted:
            subscribers.append(subscriber)

        self._stats["subscribers_count"] += 1

        self.logger.debug(f"订阅事件 {event_type.value}，处理器: {handler.__name__}")
        return str(subscriber.subscriber_id)

    def subscribe_all(
        self, handler: Callable, priority: int = 0, async_handler: bool = False, filter_func: Optional[Callable] = None
    ) -> str:
        """订阅所有事件

        Args:
            handler: 事件处理函数
            priority: 处理优先级
            async_handler: 是否为异步处理器
            filter_func: 事件过滤函数

        Returns:
            订阅者ID
        """
        subscriber = EventSubscriber(handler, priority, async_handler, filter_func)

        # 按优先级插入
        inserted = False
        for i, existing_subscriber in enumerate(self._global_subscribers):
            if subscriber.priority > existing_subscriber.priority:
                self._global_subscribers.insert(i, subscriber)
                inserted = True
                break

        if not inserted:
            self._global_subscribers.append(subscriber)

        self._stats["subscribers_count"] += 1

        self.logger.debug(f"订阅所有事件，处理器: {handler.__name__}")
        return str(subscriber.subscriber_id)

    def unsubscribe(self, event_type: EventType, subscriber_id: str) -> bool:
        """取消订阅

        Args:
            event_type: 事件类型
            subscriber_id: 订阅者ID

        Returns:
            是否成功取消订阅
        """
        subscribers = self._subscribers.get(event_type, [])
        for i, subscriber in enumerate(subscribers):
            if str(subscriber.subscriber_id) == subscriber_id:
                subscribers.pop(i)
                self._stats["subscribers_count"] -= 1
                self.logger.debug(f"取消订阅事件 {event_type.value}")
                return True
        return False

    def unsubscribe_all(self, subscriber_id: str) -> bool:
        """取消全局订阅

        Args:
            subscriber_id: 订阅者ID

        Returns:
            是否成功取消订阅
        """
        for i, subscriber in enumerate(self._global_subscribers):
            if str(subscriber.subscriber_id) == subscriber_id:
                self._global_subscribers.pop(i)
                self._stats["subscribers_count"] -= 1
                self.logger.debug("取消全局事件订阅")
                return True
        return False

    def publish(self, event: Event, sync: bool = False) -> bool:
        """发布事件

        Args:
            event: 事件对象
            sync: 是否同步处理

        Returns:
            是否成功发布
        """
        try:
            self._stats["events_published"] += 1

            if sync or not self._enable_async:
                # 同步处理
                self._process_event(event)
            else:
                # 异步处理
                if self._event_queue.qsize() >= self._max_queue_size:
                    self.logger.warning(f"事件队列已满 ({self._max_queue_size})，丢弃事件: {event.type.value}")
                    return False

                self._event_queue.put(event)

            self.logger.debug(f"发布事件: {event.type.value} (ID: {event.event_id})")
            return True

        except Exception as e:
            self.logger.error(f"发布事件失败: {e}", exc_info=True)
            return False

    def publish_sync(self, event: Event) -> bool:
        """同步发布事件

        Args:
            event: 事件对象

        Returns:
            是否成功处理
        """
        return self.publish(event, sync=True)

    def _process_event(self, event: Event) -> None:
        """处理单个事件

        Args:
            event: 事件对象
        """
        try:
            # 获取订阅者
            subscribers = self._subscribers.get(event.type, []) + self._global_subscribers

            if not subscribers:
                self.logger.debug(f"没有订阅者处理事件: {event.type.value}")
                return

            # 处理事件
            processed_count = 0
            for subscriber in subscribers:
                if not subscriber.can_handle(event):
                    continue

                try:
                    if subscriber.async_handler and self._enable_async:
                        # 异步处理
                        self._thread_pool.submit(self._handle_event_async, subscriber, event)
                    else:
                        # 同步处理
                        subscriber(event)

                    processed_count += 1

                except Exception as e:
                    self.logger.error(f"事件处理器执行失败: {e}", exc_info=True)
                    self._stats["events_failed"] += 1

                    # 标记事件处理失败
                    event.mark_processed(str(e))

            if processed_count > 0:
                self._stats["events_processed"] += 1
                if not event.processed:
                    event.mark_processed()

        except Exception as e:
            self.logger.error(f"处理事件失败: {e}", exc_info=True)
            self._stats["events_failed"] += 1

    def _handle_event_async(self, subscriber: EventSubscriber, event: Event) -> None:
        """异步处理事件

        Args:
            subscriber: 订阅者
            event: 事件对象
        """
        try:
            subscriber(event)
        except Exception as e:
            self.logger.error(f"异步事件处理器执行失败: {e}", exc_info=True)

    def _start_processing(self) -> None:
        """启动事件处理线程"""
        if self._processing:
            return

        self._processing = True

        def process_events():
            """事件处理循环"""
            while self._processing:
                try:
                    # 从队列获取事件
                    event = self._event_queue.get(timeout=1.0)
                    self._process_event(event)

                    # 处理重试事件
                    if self._retry_failed_events and event.should_retry(self._max_retries):
                        self.logger.info(f"重试处理事件: {event.type.value} (第{event.retry_count}次)")
                        time.sleep(0.1 * event.retry_count)  # 指数退避
                        self._event_queue.put(event)

                except Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"事件处理循环异常: {e}", exc_info=True)

        # 启动处理线程
        processing_thread = threading.Thread(target=process_events, name="EventBus-Processor", daemon=True)
        processing_thread.start()

        self.logger.info("事件总线处理线程已启动")

    def stop_processing(self) -> None:
        """停止事件处理"""
        self._processing = False
        self._thread_pool.shutdown(wait=True)
        self.logger.info("事件总线处理已停止")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息

        Returns:
            统计信息字典
        """
        return {
            **self._stats,
            "queue_size": self._event_queue.qsize(),
            "subscribers_by_type": {
                event_type.value: len(subscribers) for event_type, subscribers in self._subscribers.items()
            },
            "global_subscribers": len(self._global_subscribers),
        }

    def clear_subscribers(self) -> None:
        """清除所有订阅者"""
        self._subscribers.clear()
        self._global_subscribers.clear()
        self._stats["subscribers_count"] = 0
        self.logger.info("已清除所有事件订阅者")

    def set_config(self, **config) -> None:
        """设置配置

        Args:
            **config: 配置参数
        """
        if "max_queue_size" in config:
            self._max_queue_size = config["max_queue_size"]
        if "enable_async" in config:
            self._enable_async = config["enable_async"]
        if "retry_failed_events" in config:
            self._retry_failed_events = config["retry_failed_events"]
        if "max_retries" in config:
            self._max_retries = config["max_retries"]


# 全局事件总线实例
event_bus = EventBus()


# 装饰器函数
def event_handler(
    event_type: EventType, priority: int = 0, async_handler: bool = False, filter_func: Optional[Callable] = None
):
    """事件处理器装饰器

    Args:
        event_type: 事件类型
        priority: 处理优先级
        async_handler: 是否为异步处理器
        filter_func: 事件过滤函数
    """

    def decorator(func):
        event_bus.subscribe(event_type, func, priority, async_handler, filter_func)
        return func

    return decorator


def global_event_handler(priority: int = 0, async_handler: bool = False, filter_func: Optional[Callable] = None):
    """全局事件处理器装饰器

    Args:
        priority: 处理优先级
        async_handler: 是否为异步处理器
        filter_func: 事件过滤函数
    """

    def decorator(func):
        event_bus.subscribe_all(func, priority, async_handler, filter_func)
        return func

    return decorator


def publish_event(event_type: EventType, data: dict[str, Any], source: str = "Unknown", sync: bool = False) -> bool:
    """便捷的事件发布函数

    Args:
        event_type: 事件类型
        data: 事件数据
        source: 事件源
        sync: 是否同步处理

    Returns:
        是否成功发布
    """
    event = Event(type=event_type, data=data, source=source)
    return event_bus.publish(event, sync)
