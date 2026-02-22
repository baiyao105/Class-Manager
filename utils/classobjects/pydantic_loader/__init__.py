"""
Pydantic数据模型加载器。

提供与ClassDataType兼容的Pydantic模型定义和转换机制。
"""

from .base import PydanticModelBase, PydanticReference
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
