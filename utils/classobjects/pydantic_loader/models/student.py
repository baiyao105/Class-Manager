"""
学生的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ...objects.achievement import Achievement
from ...objects.datatag import DataTag
from ...objects.scoremod import ScoreModification
from ...objects.student import Student


class StudentModel(PydanticModelBase[Student]):
    "学生的Pydantic模型"

    chunk_type_name: ClassVar[str] = "Student"
    "类型名"

    name: str = Field()
    "学生姓名"

    num: int = Field()
    "学号"

    score: float = Field(default=0.0)
    "当前分数"

    total_score: float = Field(default=0.0)
    "总分数"

    highest_score: float = Field(default=0.0)
    "历史最高分"

    lowest_score: float = Field(default=0.0)
    "历史最低分"

    highest_score_cause_time: float | None = Field(default=None)
    "最高分产生时间"

    lowest_score_cause_time: float | None = Field(default=None)
    "最低分产生时间"

    belongs_to: str = Field()
    "所属班级key"

    belongs_to_group: str | None = Field(default=None)
    "所属小组key"

    history_refs: list[PydanticReference[ScoreModification]] = Field(default_factory=list)
    "历史记录引用列表"

    achievement_refs: list[PydanticReference[Achievement]] = Field(default_factory=list)
    "成就引用列表"

    tag_refs: list[PydanticReference[DataTag]] = Field(default_factory=list)
    "标签引用列表"

    last_reset: float | None = Field(default=None)
    "上次重置时间"

    last_reset_info_ref: PydanticReference[Student] | None = Field(default=None)
    "上次重置信息引用"

    @classmethod
    def from_class_data(cls, data: Student) -> StudentModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        model = cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            name=data.name,
            num=data.num,
            score=float(data.score),
            total_score=data.total_score,
            highest_score=data.highest_score,
            lowest_score=data.lowest_score,
            highest_score_cause_time=data.highest_score_cause_time,
            lowest_score_cause_time=data.lowest_score_cause_time,
            belongs_to=data.belongs_to,
            belongs_to_group=data.belongs_to_group,
            history_refs=[
                PydanticReference.from_object(sm)
                for sm in data.history.values() if sm.executed
            ],
            achievement_refs=[
                PydanticReference.from_object(a)
                for a in data.achievements.values()
            ],
            tag_refs=[
                PydanticReference.from_object(t)
                for t in data.tags
            ],
            last_reset=data.last_reset,
            last_reset_info_ref=(
                PydanticReference.from_object(data.last_reset_info)
                if data.last_reset_info else None
            ),
        )

        return model

    def to_class_data(self) -> Student:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

        stu = Student(
            name=self.name,
            num=self.num,
            score=self.score,
            belongs_to=self.belongs_to,
            total_score=self.total_score,
            highest_score=self.highest_score,
            lowest_score=self.lowest_score,
            highest_score_cause_time=self.highest_score_cause_time,
            lowest_score_cause_time=self.lowest_score_cause_time,
            belongs_to_group=self.belongs_to_group,
            last_reset=self.last_reset,
        )

        stu.uuid = self.uuid
        stu.archive_uuid = self.archive_uuid

        stu.history = {}
        for ref in self.history_refs:
            sm = ref.resolve()
            stu.history[sm.execute_time_key] = sm

        stu.achievements = {}
        for ref in self.achievement_refs:
            a = ref.resolve()
            stu.achievements[a.time_key] = a

        stu.tags = []
        for ref in self.tag_refs:
            stu.tags.append(ref.resolve())

        if self.last_reset_info_ref:
            stu.last_reset_info = self.last_reset_info_ref.resolve()

        return stu
