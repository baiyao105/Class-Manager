"""
数据加载器模块。

提供数据存储和加载的统一接口。
"""

from typing import Literal, Optional

from .sqlite_loader import (
    LoaderError,
    UserCanceledError,
    ObjectDataNotFoundError,
    IdentifierDumplicatedError,
    DataObject,
    Chunk,
)
from .pydantic_loader import (
    PydanticModelBase,
    PydanticReference,
    DataChunk,
    PydanticLoader,
    PydanticLoaderError,
    ModelNotFoundError,
    DataNotFoundError,
    get_loader,
    clear_cache,
    DataTagModel,
    StudentModel,
    ScoreTemplateModel,
    ScoreModificationModel,
    GroupModel,
    ClassModel,
    AchievementTemplateModel,
    AchievementModel,
    AttendanceInfoModel,
    DayRecordModel,
    HistoryModel,
)
from .pydantic_sqlite import PydanticSQLiteLoader
from ..classdataloader import UserDataBase

LoaderType = Literal["legacy", "pydantic", "pydantic_sqlite"]
_current_loader_type: LoaderType = "legacy"


def set_loader_type(loader_type: LoaderType) -> None:
    """
    设置全局加载器类型。

    :param loader_type: 加载器类型，"legacy"、"pydantic" 或 "pydantic_sqlite"
    """
    global _current_loader_type
    _current_loader_type = loader_type


def get_loader_type() -> LoaderType:
    """
    获取当前加载器类型。

    :return: 当前加载器类型
    """
    return _current_loader_type


def create_chunk(path: str, database: Optional[UserDataBase] = None) -> DataChunk:
    """
    创建数据块对象。

    根据当前配置的加载器类型创建对应的DataChunk实例。

    :param path: 数据存储路径
    :param database: 绑定的数据库对象
    :return: DataChunk实例
    """
    if _current_loader_type == "pydantic_sqlite":
        return PydanticSQLiteLoader.get_chunk(path, database)  # type: ignore[arg-type]
    elif _current_loader_type == "pydantic":
        return PydanticLoader.get_chunk(path, database)  # type: ignore[arg-type]
    else:
        return Chunk.get_chunk(path, database)  # type: ignore[arg-type]


__all__ = [
    "LoaderType",
    "set_loader_type",
    "get_loader_type",
    "create_chunk",
    "LoaderError",
    "UserCanceledError",
    "ObjectDataNotFoundError",
    "IdentifierDumplicatedError",
    "DataObject",
    "Chunk",
    "PydanticModelBase",
    "PydanticReference",
    "DataChunk",
    "PydanticLoader",
    "PydanticSQLiteLoader",
    "PydanticLoaderError",
    "ModelNotFoundError",
    "DataNotFoundError",
    "get_loader",
    "clear_cache",
    "DataTagModel",
    "StudentModel",
    "ScoreTemplateModel",
    "ScoreModificationModel",
    "GroupModel",
    "ClassModel",
    "AchievementTemplateModel",
    "AchievementModel",
    "AttendanceInfoModel",
    "DayRecordModel",
    "HistoryModel",
]
