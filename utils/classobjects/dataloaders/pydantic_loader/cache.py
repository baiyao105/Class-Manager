"""
Pydantic模型缓存机制。

提供线程安全的缓存管理，被 PydanticLoader 使用。
"""

from __future__ import annotations

import threading
from typing import Any, TypeVar
from uuid import UUID

from ...basetype import ClassDataType


T = TypeVar("T")
DataType = TypeVar("DataType", bound=ClassDataType)


class PydanticCache:
    """
    Pydantic模型缓存管理器。

    提供简单的缓存功能，实际的加载逻辑在 PydanticLoader 中。
    """

    _instance: PydanticCache | None = None
    _lock = threading.Lock()

    def __new__(cls) -> PydanticCache:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self._cache: dict[UUID, ClassDataType] = {}
        self._cache_lock = threading.RLock()

    def has(self, uuid: UUID) -> bool:
        """
        检查对象是否在缓存中。

        :param uuid: 对象的UUID
        :return: 是否存在
        """
        with self._cache_lock:
            return uuid in self._cache

    def get(self, uuid: UUID, default: Any = None) -> Any:
        """
        从缓存获取对象。

        :param uuid: 对象的UUID
        :param default: 默认值
        :return: 缓存的对象或默认值
        """
        with self._cache_lock:
            return self._cache.get(uuid, default)

    def set(self, uuid: UUID, obj: ClassDataType) -> None:
        """
        将对象存入缓存。

        :param uuid: 对象的UUID
        :param obj: 要缓存的对象
        """
        with self._cache_lock:
            self._cache[uuid] = obj

    def remove(self, uuid: UUID) -> None:
        """
        从缓存移除对象。

        :param uuid: 对象的UUID
        """
        with self._cache_lock:
            self._cache.pop(uuid, None)

    def clear(self) -> None:
        "清空所有缓存。"
        with self._cache_lock:
            self._cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """
        获取缓存统计信息。

        :return: 统计信息字典
        """
        with self._cache_lock:
            return {
                "cache_count": len(self._cache)
            }


def get_cache() -> PydanticCache:
    """
    获取全局缓存实例。

    :return: PydanticCache实例
    """
    return PydanticCache()


def clear_cache() -> None:
    "清空全局缓存。"
    get_cache().clear()
