"""数据模型包 - 混合架构数据模型"""

# 基础模型
# 成就系统（保持现有）
from .achievement import Achievement, AchievementLevel, AchievementTemplate, AchievementType
from .base import (
    ArchiveMixin,
    BaseModel,
    MasterDBModel,
    OrderMixin,
    SoftDeleteMixin,
    SubDBModel,
    TimestampMixin,
    UUIDMixin,
)

# 子库模型
from .class_ import (
    Classroom,
    ClassroomCreate,
    ClassroomRead,
    ClassroomUpdate,
    ClassType,
    Group,
    GroupCreate,
    GroupRead,
    GroupUpdate,
)

# 总库模型
from .master import DataRegistry, DataStatistics
from .score_record import RecordSource, RecordStatus, ScoreRecord
from .score_template import ScoreCategory, ScoreTemplate, ScoreType
from .student import Student, StudentCreate, StudentRead, StudentStatus, StudentUpdate
from .tag import StudentTagLink, Tag, TagColor, TagType

__all__ = [
    "Achievement",
    "AchievementLevel",
    "AchievementTemplate",
    # 成就系统
    "AchievementType",
    "ArchiveMixin",
    "BaseModel",
    # 子库模型
    "ClassType",
    "Classroom",
    "ClassroomCreate",
    "ClassroomRead",
    "ClassroomUpdate",
    # 总库模型
    "DataRegistry",
    "DataStatistics",
    "Group",
    "GroupCreate",
    "GroupRead",
    "GroupUpdate",
    "MasterDBModel",
    "OrderMixin",
    "RecordSource",
    "RecordStatus",
    "ScoreCategory",
    "ScoreRecord",
    "ScoreTemplate",
    "ScoreType",
    "SoftDeleteMixin",
    "Student",
    "StudentCreate",
    "StudentRead",
    "StudentStatus",
    "StudentTagLink",
    "StudentUpdate",
    "SubDBModel",
    "Tag",
    "TagColor",
    "TagType",
    # 基础模型
    "TimestampMixin",
    "UUIDMixin",
]
