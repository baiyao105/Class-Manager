from __future__ import annotations

import json
from typing import TYPE_CHECKING, Self, override
from uuid import UUID

from utils.algorithm import update_object_mapping

from ..basetype import ClassDataType, ClassDataTypeUUID, StringObjectDataKind
from ..classdataloader import ClassDataLoader

if TYPE_CHECKING:
    from .attendanceinfo import AttendanceInfo
    from .classtype import Class


class DayRecord(ClassDataType):
    "一天的记录"

    chunk_type_name: str = "DayRecord"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "返回一个空的每日记录对象"
        from .attendanceinfo import AttendanceInfo
        from .classtype import Class

        return cls(Class.new_dummy(), 0, 0, AttendanceInfo.new_dummy())

    def __init__(
        self,
        target_class: Class,
        weekday: int,
        create_utc: float,
        attendance_info: AttendanceInfo,
    ):
        """
        构造函数。

        :param target_class: 目标班级
        :param weekday: 星期几（1-7）
        :param create_utc: 时间戳
        :param attendance_info: 考勤信息
        """
        super().__init__()
        self.weekday = weekday
        self.utc = create_utc
        self.attendance_info = attendance_info
        self.target_class = target_class
        self.archive_uuid = ClassDataLoader.get_archive_uuid()

    def to_string(self) -> StringObjectDataKind[Self]:
        "将每日记录对象转为字符串。"
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "target_class": str(self.target_class.uuid),
                "weekday": self.weekday,
                "utc": self.utc,
                "attendance_info": str(self.attendance_info.uuid),
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @staticmethod
    def load_target_class(class_uuid: str) -> Class:
        "从UUID字符串加载目标班级对象。"
        from .classtype import Class
        result = ClassDataLoader.LoadUUID(
            ClassDataTypeUUID(Class, UUID(class_uuid)), Class
        )
        assert result is not None, f"目标班级{class_uuid}加载失败"
        return result

    @staticmethod
    def load_attendance_info(attendance_uuid: str) -> AttendanceInfo:
        "从UUID字符串加载考勤信息对象。"
        from .attendanceinfo import AttendanceInfo
        result = ClassDataLoader.LoadUUID(
            ClassDataTypeUUID(AttendanceInfo, UUID(attendance_uuid)), AttendanceInfo
        )
        assert result is not None, f"考勤信息{attendance_uuid}加载失败"
        return result

    @classmethod
    def from_string(cls, string: str) -> Self:
        "从字符串加载每日记录对象。"

        data = json.loads(string)
        if data["type"] != cls.chunk_type_name:
            raise ValueError(f"类型不匹配：{data['type']} != {cls.chunk_type_name}")
        obj = cls(
            target_class=cls.load_target_class(data["target_class"]),
            weekday=data["weekday"],
            create_utc=data["utc"],
            attendance_info=cls.load_attendance_info(data["attendance_info"]),
        )
        obj.uuid = data["uuid"]
        obj.archive_uuid = data["archive_uuid"]
        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        update_object_mapping(self, obj.__dict__)
        return self

    @override
    def to_pydantic(self):
        """
        转换为Pydantic模型。

        :return: Pydantic模型实例
        """
        from ..dataloaders.pydantic_loader.models.day_record import DayRecordModel
        return DayRecordModel.from_class_data(self)
