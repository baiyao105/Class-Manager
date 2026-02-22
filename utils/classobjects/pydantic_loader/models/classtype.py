"""
班级的Pydantic模型。
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ...objects.classtype import Class
from ...objects.student import Student
from ...objects.group import Group


class ClassModel(PydanticModelBase[Class]):
    "班级的Pydantic模型"

    chunk_type_name: ClassVar[str] = "Class"
    "类型名"

    name: str = Field()
    "班级名称"

    owner: str = Field()
    "班主任"

    key: str = Field()
    "班级key"

    student_refs: list[tuple[int, PydanticReference[Student]]] = Field(default_factory=list)
    "学生引用列表(学号,引用)"

    group_refs: list[tuple[str, PydanticReference[Group]]] = Field(default_factory=list)
    "小组引用列表(key,引用)"

    cleaning_mapping: dict[int, dict[Literal["leader", "member"], list[PydanticReference[Student]]]] | None = Field(default=None)
    "打扫卫生映射"

    homework_rules: dict[str, Any] | None = Field(default=None)
    "作业规则"

    @classmethod
    def from_class_data(cls, data: Class) -> ClassModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        cleaning_mapping: dict[int, dict[Literal["leader", "member"], list[PydanticReference[Student]]]] | None = None
        if data.cleaning_mapping:
            cleaning_mapping = {}
            for k, v in data.cleaning_mapping.items():
                cleaning_mapping[k] = {}
                for t, students in v.items():
                    cleaning_mapping[k][t] = [PydanticReference.from_object(s) for s in students]

        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            name=data.name,
            owner=data.owner,
            key=data.key,
            student_refs=[
                (num, PydanticReference.from_object(s))
                for num, s in data.students.items()
            ],
            group_refs=[
                (key, PydanticReference.from_object(g))
                for key, g in data.groups.items()
            ],
            cleaning_mapping=cleaning_mapping,
        )

    def to_class_data(self) -> Class:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

        students: dict[int, Student] = {}
        for num, ref in self.student_refs:
            students[num] = ref.resolve() or Student.new_dummy()

        groups: dict[str, Group] = {}
        for key, ref in self.group_refs:
            groups[key] = ref.resolve() or Group.new_dummy()

        cleaning_mapping: dict[int, dict[Literal["leader", "member"], list[Student]]] | None = None
        if self.cleaning_mapping:
            cleaning_mapping = {}
            for k, v in self.cleaning_mapping.items():
                cleaning_mapping[k] = {}
                for t, refs in v.items():
                    cleaning_mapping[k][t] = []
                    for ref in refs:
                        cleaning_mapping[k][t].append(ref.resolve() or Student.new_dummy())

        obj = Class(
            name=self.name,
            owner=self.owner,
            students=students,
            key=self.key,
            groups=groups,
            cleaning_mapping=cleaning_mapping
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid

        return obj
