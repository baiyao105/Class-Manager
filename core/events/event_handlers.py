"""事件处理器注册表

提供事件处理器的注册、管理和执行功能
"""

import logging
from typing import Any, Callable, Optional

from .event_bus import event_bus
from .event_types import Event, EventType


class EventHandlerRegistry:
    """事件处理器注册表

    管理系统中的事件处理器，提供统一的注册和管理接口
    """

    def __init__(self):
        """初始化注册表"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._handlers: dict[str, Callable] = {}
        self._handler_metadata: dict[str, dict[str, Any]] = {}

        # 注册默认处理器
        self._register_default_handlers()

    def register_handler(
        self,
        name: str,
        handler: Callable,
        event_types: list[EventType],
        description: str = "",
        priority: int = 0,
        async_handler: bool = False,
    ) -> None:
        """注册事件处理器

        Args:
            name: 处理器名称
            handler: 处理器函数
            event_types: 处理的事件类型列表
            description: 处理器描述
            priority: 处理优先级
            async_handler: 是否为异步处理器
        """
        self._handlers[name] = handler
        self._handler_metadata[name] = {
            "description": description,
            "event_types": event_types,
            "priority": priority,
            "async_handler": async_handler,
            "registered_at": None,
        }

        # 订阅事件
        for event_type in event_types:
            event_bus.subscribe(event_type, handler, priority, async_handler)

        self.logger.info(f"注册事件处理器: {name} (处理 {len(event_types)} 种事件类型)")

    def unregister_handler(self, name: str) -> bool:
        """注销事件处理器

        Args:
            name: 处理器名称

        Returns:
            是否成功注销
        """
        if name not in self._handlers:
            return False

        # 取消事件订阅
        metadata = self._handler_metadata[name]
        handler = self._handlers[name]

        for _event_type in metadata["event_types"]:
            # 注意：这里需要EventBus支持通过处理器函数取消订阅
            # 当前实现中需要订阅者ID，这是一个设计改进点
            pass

        del self._handlers[name]
        del self._handler_metadata[name]

        self.logger.info(f"注销事件处理器: {name}")
        return True

    def get_handler(self, name: str) -> Optional[Callable]:
        """获取处理器

        Args:
            name: 处理器名称

        Returns:
            处理器函数或None
        """
        return self._handlers.get(name)

    def list_handlers(self) -> dict[str, dict[str, Any]]:
        """列出所有处理器

        Returns:
            处理器信息字典
        """
        return self._handler_metadata.copy()

    def _register_default_handlers(self) -> None:
        """注册默认事件处理器"""

        # 系统日志处理器
        def system_logger_handler(event: Event) -> None:
            """系统日志处理器"""
            if event.type in [EventType.SYSTEM_STARTED, EventType.SYSTEM_SHUTDOWN]:
                self.logger.info(f"系统事件: {event.type.value} - {event.data.get('message', '')}")
            elif event.type == EventType.ERROR_OCCURRED:
                self.logger.error(f"系统错误: {event.data.get('error_message', '')}")

        self.register_handler(
            "system_logger",
            system_logger_handler,
            [EventType.SYSTEM_STARTED, EventType.SYSTEM_SHUTDOWN, EventType.ERROR_OCCURRED],
            "系统事件日志记录器",
            priority=100,
        )

        # 数据统计处理器
        def statistics_handler(event: Event) -> None:
            """数据统计处理器"""
            # 这里可以实现统计逻辑
            # 例如：记录事件发生次数、更新仪表板数据等

        self.register_handler(
            "statistics",
            statistics_handler,
            [EventType.STUDENT_CREATED, EventType.CLASS_CREATED, EventType.ACHIEVEMENT_EARNED],
            "数据统计处理器",
            priority=50,
            async_handler=True,
        )

        # 通知处理器
        def notification_handler(event: Event) -> None:
            """通知处理器"""
            # 这里可以实现通知逻辑
            # 例如：发送邮件、推送消息等
            if event.type == EventType.ACHIEVEMENT_EARNED:
                student_id = event.data.get("student_id")
                achievement_data = event.data.get("achievement_data", {})
                self.logger.info(f"学生 {student_id} 获得成就: {achievement_data.get('title', '未知成就')}")

        self.register_handler(
            "notification",
            notification_handler,
            [EventType.ACHIEVEMENT_EARNED, EventType.STUDENT_GRADUATED],
            "通知处理器",
            priority=30,
            async_handler=True,
        )


# 全局事件处理器注册表
event_handler_registry = EventHandlerRegistry()


# 便捷的处理器注册装饰器
def register_event_handler(
    name: str, event_types: list[EventType], description: str = "", priority: int = 0, async_handler: bool = False
):
    """事件处理器注册装饰器

    Args:
        name: 处理器名称
        event_types: 处理的事件类型列表
        description: 处理器描述
        priority: 处理优先级
        async_handler: 是否为异步处理器
    """

    def decorator(func):
        event_handler_registry.register_handler(name, func, event_types, description, priority, async_handler)
        return func

    return decorator


# 预定义的事件处理器
class DefaultEventHandlers:
    """默认事件处理器集合"""

    @staticmethod
    @register_event_handler(
        "audit_logger",
        [
            EventType.STUDENT_CREATED,
            EventType.STUDENT_UPDATED,
            EventType.STUDENT_DELETED,
            EventType.CLASS_CREATED,
            EventType.CLASS_UPDATED,
            EventType.CLASS_DELETED,
        ],
        "审计日志记录器",
        priority=90,
    )
    def audit_logger(event: Event) -> None:
        """审计日志处理器"""
        logger = logging.getLogger("AuditLogger")

        action_map = {
            EventType.STUDENT_CREATED: "创建学生",
            EventType.STUDENT_UPDATED: "更新学生",
            EventType.STUDENT_DELETED: "删除学生",
            EventType.CLASS_CREATED: "创建班级",
            EventType.CLASS_UPDATED: "更新班级",
            EventType.CLASS_DELETED: "删除班级",
        }

        action = action_map.get(event.type, event.type.value)
        user_id = event.user_id or "系统"

        logger.info(f"[审计] {action} - 用户: {user_id}, 时间: {event.timestamp}, 事件ID: {event.event_id}")

    @staticmethod
    @register_event_handler(
        "cache_invalidator",
        [EventType.STUDENT_UPDATED, EventType.CLASS_UPDATED, EventType.ACHIEVEMENT_EARNED],
        "缓存失效处理器",
        priority=80,
        async_handler=True,
    )
    def cache_invalidator(event: Event) -> None:
        """缓存失效处理器"""
        # 这里可以实现缓存失效逻辑
        # 例如：清除相关的缓存键
        logger = logging.getLogger("CacheInvalidator")

        if event.type == EventType.STUDENT_UPDATED:
            student_id = event.data.get("student_id")
            logger.debug(f"失效学生缓存: {student_id}")
        elif event.type == EventType.CLASS_UPDATED:
            class_id = event.data.get("class_id")
            logger.debug(f"失效班级缓存: {class_id}")

    @staticmethod
    @register_event_handler(
        "data_sync",
        [EventType.STUDENT_CREATED, EventType.STUDENT_UPDATED, EventType.STUDENT_DELETED],
        "数据同步处理器",
        priority=70,
        async_handler=True,
    )
    def data_sync_handler(event: Event) -> None:
        """数据同步处理器"""
        # 这里可以实现数据同步逻辑
        # 例如：同步到外部系统、更新搜索索引等
        logger = logging.getLogger("DataSync")

        if event.type in [EventType.STUDENT_CREATED, EventType.STUDENT_UPDATED]:
            student_data = event.data.get("student_data", {})
            logger.debug(f"同步学生数据: {student_data.get('name', '未知')}")

    @staticmethod
    @register_event_handler("error_reporter", [EventType.ERROR_OCCURRED], "错误报告处理器", priority=100)
    def error_reporter(event: Event) -> None:
        """错误报告处理器"""
        logger = logging.getLogger("ErrorReporter")

        error_message = event.data.get("error_message", "")
        error_details = event.data.get("error_details", {})

        logger.error(f"系统错误报告: {error_message}")

        # 这里可以实现错误报告逻辑
        # 例如：发送错误报告邮件、记录到错误跟踪系统等
        if error_details.get("severity") == "critical":
            logger.critical(f"严重错误需要立即处理: {error_message}")
