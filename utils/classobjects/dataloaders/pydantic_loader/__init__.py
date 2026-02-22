"""
Pydantic数据模型加载器。

提供与ClassDataType兼容的Pydantic模型定义和转换机制。
"""

from .base import PydanticModelBase, PydanticReference
from ...datachunk import DataChunk
from .loader import (
    PydanticLoader,
    PydanticLoaderError,
    ModelNotFoundError,
    DataNotFoundError,
    get_loader,
    clear_cache,
)
from .models import (
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

__all__ = [
    "PydanticModelBase",
    "PydanticReference",
    "DataChunk",
    "PydanticLoader",
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
