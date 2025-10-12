from __future__ import annotations

from typing import (TYPE_CHECKING, Dict)
from utils.basetypes import Object

if TYPE_CHECKING:
    from .student import Student
    from .classtype import Class
    from ..observers.achievementstatobs import AchievementStatusObserver
    from ..observers.classstatobs import ClassStatusObserver



class ClassData(Object):
    "班级数据，用于判断成就"

    def __init__(
        self,
        student: Student,
        classes: Dict[str, Class] = None,
        class_obs: ClassStatusObserver = None,
        achievement_obs: AchievementStatusObserver = None,
    ):
        """班级数据构造函数。

        :param student: 学生
        :param classes: 班级字典
        :param class_obs: 班级侦测器
        :param achievement_obs: 成就侦测器
        """
        self.classes = classes
        "班级的dict"
        self.class_obs = class_obs
        "班级侦测器"
        self.achievement_obs = achievement_obs
        "成就侦测器"
        self.student = student
        "学生"
        self.student_class = self.classes[self.student.belongs_to]
        "学生所在的班级"
        self.student_group = (
            self.student_class.groups[self.student.belongs_to_group]
            if self.student.belongs_to_group
            else None
        )
        "学生所在的组"
        self.groups = self.student_class.groups
        "班级中的所有组"