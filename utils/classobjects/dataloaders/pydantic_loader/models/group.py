"""
小组的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ....objects.datatag import DataTag
from ....objects.group import Group
from ....objects.student import Student


class GroupModel(PydanticModelBase[Group]):
    "小组的Pydantic模型"

    chunk_type_name: ClassVar[str] = "Group"
    "类型名"

    key: str = Field()
    "小组key"

    name: str = Field()
    "小组名称"

    leader_ref: PydanticReference[Student] = Field()
    "组长引用"

    member_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "成员引用列表"

    belongs_to: str = Field()
    "所属班级key"

    description: str = Field(default="")
    "详细描述"

    tag_refs: list[PydanticReference[DataTag]] = Field(default_factory=list)
    "标签引用列表"

    @classmethod
    def from_class_data(cls, data: Group) -> GroupModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            key=data.key,
            name=data.name,
            leader_ref=PydanticReference.from_object(data.leader),
            member_refs=[PydanticReference.from_object(m) for m in data.members],
            belongs_to=data.belongs_to,
            description=data.further_desc,
            tag_refs=[PydanticReference.from_object(t) for t in data.tags],
        )

    def to_class_data(self) -> Group:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """


        leader = self.leader_ref.resolve()

        members: list[Student] = []
        for ref in self.member_refs:
            members.append(ref.resolve())

        obj = Group(
            key=self.key,
            name=self.name,
            leader=leader,
            members=members,
            belongs_to=self.belongs_to,
            further_desc=self.description
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid

        for ref in self.tag_refs:
            obj.tags.append(ref.resolve())

        return obj
