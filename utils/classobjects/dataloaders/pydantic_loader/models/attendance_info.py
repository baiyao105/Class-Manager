"""
考勤信息的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ....objects.attendanceinfo import AttendanceInfo
from ....objects.student import Student

class AttendanceInfoModel(PydanticModelBase[AttendanceInfo]):
    "考勤信息的Pydantic模型"

    chunk_type_name: ClassVar[str] = "AttendanceInfo"
    "类型名"

    target_class: str = Field()
    "目标班级key"

    is_early_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "早到学生引用列表"

    is_late_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "迟到学生引用列表"

    is_late_more_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "严重迟到学生引用列表"

    is_absent_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "缺勤学生引用列表"

    is_leave_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "请假学生引用列表"

    is_leave_early_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "早退学生引用列表"

    is_leave_late_refs: list[PydanticReference[Student]] = Field(default_factory=list)
    "晚退学生引用列表"

    @classmethod
    def from_class_data(cls, data: AttendanceInfo) -> AttendanceInfoModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            target_class=data.target_class,
            is_early_refs=[PydanticReference.from_object(s) for s in data.is_early],
            is_late_refs=[PydanticReference.from_object(s) for s in data.is_late],
            is_late_more_refs=[PydanticReference.from_object(s) for s in data.is_late_more],
            is_absent_refs=[PydanticReference.from_object(s) for s in data.is_absent],
            is_leave_refs=[PydanticReference.from_object(s) for s in data.is_leave],
            is_leave_early_refs=[PydanticReference.from_object(s) for s in data.is_leave_early],
            is_leave_late_refs=[PydanticReference.from_object(s) for s in data.is_leave_late]
        )

    def to_class_data(self) -> AttendanceInfo:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

        def load_students(refs: list[PydanticReference[Student]]) -> list[Student]:
            result: list[Student] = []
            for ref in refs:
                result.append(ref.resolve())
            return result

        obj = AttendanceInfo(
            target_class=self.target_class,
            is_early=load_students(self.is_early_refs),
            is_late=load_students(self.is_late_refs),
            is_late_more=load_students(self.is_late_more_refs),
            is_absent=load_students(self.is_absent_refs),
            is_leave=load_students(self.is_leave_refs),
            is_leave_early=load_students(self.is_leave_early_refs),
            is_leave_late=load_students(self.is_leave_late_refs)
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid

        return obj
