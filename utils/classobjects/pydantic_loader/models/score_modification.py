"""
分数修改记录的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ...objects.scoremod import ScoreModification
from ...objects.scoremodtemplate import ScoreModificationTemplate
from ...objects.student import Student


class ScoreModificationModel(PydanticModelBase[ScoreModification]):
    "分数修改记录的Pydantic模型"

    chunk_type_name: ClassVar[str] = "ScoreModification"
    "类型名"

    template_ref: PydanticReference[ScoreModificationTemplate] | None = Field(default=None)
    "模板引用"

    target_ref: PydanticReference[Student] = Field()
    "目标学生引用"

    title: str = Field()
    "标题"

    description: str = Field(default="")
    "描述"

    modification: float = Field()
    "修改分数"

    executed: bool = Field(default=False)
    "是否已执行"

    execute_time: str | None = Field(default=None)
    "执行时间字符串"

    execute_time_key: int = Field(default=0)
    "执行时间键值"

    create_time: str = Field()
    "创建时间字符串"

    @classmethod
    def from_class_data(cls, data: ScoreModification) -> ScoreModificationModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            template_ref=PydanticReference.from_object(data.temp) if data.temp else None,
            target_ref=PydanticReference.from_object(data.target),
            title=data.title,
            description=data.desc,
            modification=data.mod,
            executed=data.executed,
            execute_time=data.execute_time,
            execute_time_key=data.execute_time_key,
            create_time=data.create_time,
        )

    def to_class_data(self) -> ScoreModification:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

        template: ScoreModificationTemplate | None = None
        if self.template_ref:
            template = self.template_ref.resolve()

        target: Student | None = None
        if self.target_ref:
            target = self.target_ref.resolve()

        obj = ScoreModification(
            template=template or ScoreModificationTemplate.new_dummy(),
            target=target or Student.new_dummy(),
            title=self.title,
            desc=self.description,
            mod=self.modification,
            execute_time=self.execute_time,
            create_time=self.create_time,
            executed=self.executed
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid
        obj.execute_time_key = self.execute_time_key

        return obj
