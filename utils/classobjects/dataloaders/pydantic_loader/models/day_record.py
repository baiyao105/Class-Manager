"""
每日记录的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ....objects.attendanceinfo import AttendanceInfo
from ....objects.classtype import Class
from ....objects.dayrecord import DayRecord


class DayRecordModel(PydanticModelBase[DayRecord]):
    "每日记录的Pydantic模型"

    chunk_type_name: ClassVar[str] = "DayRecord"
    "类型名"

    target_class_ref: PydanticReference[Class] = Field()
    "目标班级引用"

    weekday: int = Field()
    "星期几(1-7)"

    utc: float = Field()
    "时间戳"

    attendance_info_ref: PydanticReference[AttendanceInfo] = Field()
    "考勤信息引用"

    @classmethod
    def from_class_data(cls, data: DayRecord) -> DayRecordModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            target_class_ref=PydanticReference.from_object(data.target_class),
            weekday=data.weekday,
            utc=data.utc,
            attendance_info_ref=PydanticReference.from_object(data.attendance_info)
        )

    def to_class_data(self) -> DayRecord:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

        target_class = self.target_class_ref.resolve()

        attendance_info = self.attendance_info_ref.resolve()

        obj = DayRecord(
            target_class=target_class,
            weekday=self.weekday,
            create_utc=self.utc,
            attendance_info=attendance_info
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid
        
        return obj