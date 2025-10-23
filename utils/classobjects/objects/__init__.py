"""
所有基础班级数据类型的包。

目前只是用annotation和动态import简单处理了依赖关系...

（以后应该还是会接着改）
"""

from .achievement import Achievement
from .achievementtemp import AchievementTemplate
from .attendanceinfo import AttendanceInfo
from .classdata import ClassData
from .classtype import Class
from .dayrecord import DayRecord
from .group import Group
from .history import History
from .homeworkrule import HomeworkRule
from .scoremod import ScoreModification
from .scoremodtemplate import ScoreModificationTemplate
from .student import Student

__all__ = [
    "Achievement",
    "AchievementTemplate",
    "AttendanceInfo",
    "Class",
    "ClassData",
    "DayRecord",
    "Group",
    "History",
    "HomeworkRule",
    "ScoreModification",
    "ScoreModificationTemplate",
    "Student",
]
