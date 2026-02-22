"""
所有Pydantic数据模型的包。
"""

from .datatag import DataTagModel
from .student import StudentModel
from .score_template import ScoreTemplateModel
from .score_modification import ScoreModificationModel
from .group import GroupModel
from .classtype import ClassModel
from .achievement_template import AchievementTemplateModel
from .achievement import AchievementModel
from .attendance_info import AttendanceInfoModel
from .day_record import DayRecordModel
from .history import HistoryModel
from .homework_rule import HomeworkRuleModel

DataTagModel.model_rebuild()
StudentModel.model_rebuild()
ScoreTemplateModel.model_rebuild()
ScoreModificationModel.model_rebuild()
GroupModel.model_rebuild()
ClassModel.model_rebuild()
AchievementTemplateModel.model_rebuild()
AchievementModel.model_rebuild()
AttendanceInfoModel.model_rebuild()
DayRecordModel.model_rebuild()
HistoryModel.model_rebuild()
HomeworkRuleModel.model_rebuild()

__all__ = [
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
    "HomeworkRuleModel"
]
