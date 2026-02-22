"""
分数修改模板的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase

from ....objects.scoremodtemplate import ScoreModificationTemplate


class ScoreTemplateModel(PydanticModelBase[ScoreModificationTemplate]):
    "分数修改模板的Pydantic模型"

    chunk_type_name: ClassVar[str] = "ScoreModificationTemplate"
    "类型名"

    key: str = Field()
    "模板标识符"

    title: str = Field()
    "模板标题"

    description: str = Field(default="")
    "模板描述"

    modification: float = Field()
    "修改分数"

    is_visible: bool = Field(default=True)
    "是否可见"

    cant_replace: bool = Field(default=False)
    "是否禁止替换"

    @classmethod
    def from_class_data(cls, data: ScoreModificationTemplate) -> ScoreTemplateModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            key=data.key,
            title=data.title,
            description=data.desc,
            modification=data.mod,
            is_visible=data.is_visible,
            cant_replace=data.cant_replace,
        )

    def to_class_data(self) -> ScoreModificationTemplate:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

        obj = ScoreModificationTemplate(
            key=self.key,
            modification=self.modification,
            title=self.title,
            description=self.description,
            cant_replace=self.cant_replace,
            is_visible=self.is_visible
        )

        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid
        return obj
