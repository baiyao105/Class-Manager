"""
成就实例的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ....objects.achievement import Achievement
from ....objects.achievementtemp import AchievementTemplate
from ....objects.student import Student


class AchievementModel(PydanticModelBase[Achievement]):
    "成就实例的Pydantic模型"

    chunk_type_name: ClassVar[str] = "Achievement"
    "类型名"

    template_ref: PydanticReference[AchievementTemplate] = Field()
    "模板引用"

    target_ref: PydanticReference[Student] = Field()
    "目标学生引用"

    time: str = Field()
    "达成时间"

    time_key: int = Field()
    "达成时间键值"

    sound: str | None = Field(default=None)
    "音效"

    @classmethod
    def from_class_data(cls, data: Achievement) -> AchievementModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            template_ref=PydanticReference.from_object(data.temp),
            target_ref=PydanticReference.from_object(data.target),
            time=data.time,
            time_key=data.time_key,
            sound=data.sound,
        )

    def to_class_data(self) -> Achievement:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """
        template = self.template_ref.resolve()

        target = self.target_ref.resolve()

        obj = Achievement(
            template=template,
            target=target,
            reach_time=self.time,
            reach_time_key=self.time_key
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid
        obj.sound = self.sound

        return obj
