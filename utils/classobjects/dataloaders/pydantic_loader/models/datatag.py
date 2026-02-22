"""
数据标签的Pydantic模型。
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field

from ..base import PydanticModelBase

from ....objects.datatag import DataTag


class DataTagModel(PydanticModelBase[DataTag]):
    "数据标签的Pydantic模型"

    chunk_type_name: ClassVar[str] = "DataTag"
    "类型名"

    key: str = Field()
    "标签key"

    data: Any = Field(default=None)
    "标签携带的数据"

    @classmethod
    def from_class_data(cls, data: DataTag) -> DataTagModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            key=data.key,
            data=data.data,
        )

    def to_class_data(self) -> DataTag:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """
        
        obj = DataTag(
            key=self.key,
            data=self.data
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid
        return obj
