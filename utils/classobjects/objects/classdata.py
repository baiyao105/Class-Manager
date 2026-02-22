from __future__ import annotations

from typing import TYPE_CHECKING

from ...basetypes import Object

if TYPE_CHECKING:
    from ..observers.achievementstatobs import AchievementStatusObserver
    from ..observers.classstatobs import ClassStatusObserver
    from .classtype import Class
    from .student import Student


class ClassData(Object):
    "班级数据，用于判断成就"

    def __init__(
        self,
        student: Student,
        classes: dict[str, Class],
        class_obs: ClassStatusObserver,
        achievement_obs: AchievementStatusObserver
    ):
        """
        班级数据构造函数。

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
            self.student_class.groups[self.student.belongs_to_group] if self.student.belongs_to_group else None
        )
        "学生所在的组"
        self.groups = self.student_class.groups
        "班级中的所有组"
