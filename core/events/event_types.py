"""事件类型定义

定义系统中使用的各种事件类型和事件数据结构
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class EventType(str, Enum):
    """事件类型枚举

    定义系统中所有可能的事件类型
    """

    # 学生相关事件
    STUDENT_CREATED = "student_created"
    STUDENT_UPDATED = "student_updated"
    STUDENT_DELETED = "student_deleted"
    STUDENT_ACTIVATED = "student_activated"
    STUDENT_DEACTIVATED = "student_deactivated"
    STUDENT_GRADUATED = "student_graduated"
    STUDENT_SCORE_UPDATED = "student_score_updated"
    STUDENT_SCORE_RESET = "student_score_reset"

    # 班级相关事件
    CLASS_CREATED = "class_created"
    CLASS_UPDATED = "class_updated"
    CLASS_DELETED = "class_deleted"
    CLASS_ACTIVATED = "class_activated"
    CLASS_DEACTIVATED = "class_deactivated"
    CLASS_STATISTICS_UPDATED = "class_statistics_updated"

    # 成就相关事件
    ACHIEVEMENT_EARNED = "achievement_earned"
    ACHIEVEMENT_UPDATED = "achievement_updated"
    ACHIEVEMENT_DELETED = "achievement_deleted"
    ACHIEVEMENT_BATCH_CREATED = "achievement_batch_created"

    # 数据相关事件
    DATA_IMPORTED = "data_imported"
    DATA_EXPORTED = "data_exported"
    DATA_BACKUP_CREATED = "data_backup_created"
    DATA_RESTORED = "data_restored"
    DATA_MIGRATED = "data_migrated"

    # 系统相关事件
    SYSTEM_STARTED = "system_started"
    SYSTEM_SHUTDOWN = "system_shutdown"
    DATABASE_CONNECTED = "database_connected"
    DATABASE_DISCONNECTED = "database_disconnected"

    # 用户相关事件
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_ACTION = "user_action"

    # 错误相关事件
    ERROR_OCCURRED = "error_occurred"
    WARNING_ISSUED = "warning_issued"

    # 通知相关事件
    NOTIFICATION_SENT = "notification_sent"
    EMAIL_SENT = "email_sent"

    # 配置相关事件
    CONFIG_UPDATED = "config_updated"
    SETTINGS_CHANGED = "settings_changed"


class EventPriority(str, Enum):
    """事件优先级"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Event:
    """事件数据结构

    表示系统中的一个事件实例
    """

    # 基本信息
    type: EventType
    data: dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"

    # 元数据
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: EventPriority = EventPriority.NORMAL

    # 可选信息
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None

    # 处理信息
    processed: bool = False
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式

        Returns:
            事件信息字典
        """
        return {
            "event_id": self.event_id,
            "type": self.type.value,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.value,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "correlation_id": self.correlation_id,
            "processed": self.processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """从字典创建事件对象

        Args:
            data: 事件数据字典

        Returns:
            事件对象
        """
        event = cls(
            type=EventType(data["type"]),
            data=data.get("data", {}),
            source=data.get("source", "unknown"),
            event_id=data.get("event_id", str(uuid.uuid4())),
            priority=EventPriority(data.get("priority", EventPriority.NORMAL.value)),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            correlation_id=data.get("correlation_id"),
            processed=data.get("processed", False),
            error_message=data.get("error_message"),
            retry_count=data.get("retry_count", 0),
        )

        # 处理时间戳
        if "timestamp" in data:
            if isinstance(data["timestamp"], str):
                event.timestamp = datetime.fromisoformat(data["timestamp"])
            else:
                event.timestamp = data["timestamp"]

        if data.get("processed_at"):
            if isinstance(data["processed_at"], str):
                event.processed_at = datetime.fromisoformat(data["processed_at"])
            else:
                event.processed_at = data["processed_at"]

        return event

    def mark_processed(self, error_message: Optional[str] = None) -> None:
        """标记事件为已处理

        Args:
            error_message: 错误消息（如果处理失败）
        """
        self.processed = True
        self.processed_at = datetime.utcnow()
        if error_message:
            self.error_message = error_message
            self.retry_count += 1

    def should_retry(self, max_retries: int = 3) -> bool:
        """判断是否应该重试

        Args:
            max_retries: 最大重试次数

        Returns:
            是否应该重试
        """
        return self.error_message is not None and self.retry_count < max_retries


# 事件工厂类
class EventFactory:
    """事件工厂

    提供便捷的事件创建方法
    """

    @staticmethod
    def create_student_event(
        event_type: EventType, student_id: str, student_data: dict[str, Any], source: str = "StudentService"
    ) -> Event:
        """创建学生相关事件

        Args:
            event_type: 事件类型
            student_id: 学生ID
            student_data: 学生数据
            source: 事件源

        Returns:
            学生事件对象
        """
        return Event(
            type=event_type,
            data={"student_id": student_id, "student_data": student_data},
            source=source,
            priority=EventPriority.NORMAL,
        )

    @staticmethod
    def create_class_event(
        event_type: EventType, class_id: str, class_data: dict[str, Any], source: str = "ClassService"
    ) -> Event:
        """创建班级相关事件

        Args:
            event_type: 事件类型
            class_id: 班级ID
            class_data: 班级数据
            source: 事件源

        Returns:
            班级事件对象
        """
        return Event(
            type=event_type,
            data={"class_id": class_id, "class_data": class_data},
            source=source,
            priority=EventPriority.NORMAL,
        )

    @staticmethod
    def create_achievement_event(
        event_type: EventType, achievement_id: str, achievement_data: dict[str, Any], source: str = "AchievementService"
    ) -> Event:
        """创建成就相关事件

        Args:
            event_type: 事件类型
            achievement_id: 成就ID
            achievement_data: 成就数据
            source: 事件源

        Returns:
            成就事件对象
        """
        return Event(
            type=event_type,
            data={"achievement_id": achievement_id, "achievement_data": achievement_data},
            source=source,
            priority=EventPriority.NORMAL,
        )

    @staticmethod
    def create_system_event(
        event_type: EventType,
        message: str,
        details: Optional[dict[str, Any]] = None,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> Event:
        """创建系统相关事件

        Args:
            event_type: 事件类型
            message: 事件消息
            details: 事件详情
            priority: 事件优先级

        Returns:
            系统事件对象
        """
        return Event(
            type=event_type, data={"message": message, "details": details or {}}, source="System", priority=priority
        )

    @staticmethod
    def create_error_event(error_message: str, error_details: dict[str, Any], source: str = "System") -> Event:
        """创建错误事件

        Args:
            error_message: 错误消息
            error_details: 错误详情
            source: 事件源

        Returns:
            错误事件对象
        """
        return Event(
            type=EventType.ERROR_OCCURRED,
            data={"error_message": error_message, "error_details": error_details},
            source=source,
            priority=EventPriority.HIGH,
        )
