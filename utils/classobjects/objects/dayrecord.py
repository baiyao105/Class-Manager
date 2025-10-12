from __future__ import annotations

import json
from typing import (Literal, TYPE_CHECKING)
from ..basetype import ClassDataType
from ..classdataobj import ClassDataObj

if TYPE_CHECKING:
    from .classtype import Class
    from .attendanceinfo import AttendanceInfo

class DayRecord(ClassDataType):
        "一天的记录"

        chunk_type_name: Literal["DayRecord"] = "DayRecord"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "DayRecord" = None
        "空的每日记录对象"

        @staticmethod
        def new_dummy():
            "返回一个空的每日记录对象"
            from .classtype import Class
            from .attendanceinfo import AttendanceInfo
            return DayRecord(Class.new_dummy(), 0, 0, AttendanceInfo.new_dummy())

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
            self.weekday = weekday
            self.utc = create_utc
            self.attendance_info = attendance_info
            self.target_class = target_class
            self.archive_uuid = ClassDataObj.get_archive_uuid()

        def to_string(self):
            "将每日记录对象转为字符串。"
            if isinstance(self.target_class, dict):
                self.target_class = self.target_class[self.target_class.keys()[0]]
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "target_class": str(self.target_class.uuid),
                    "weekday": self.weekday,
                    "utc": self.utc,
                    "attendance_info": str(self.attendance_info.uuid),
                    "uuid": str(self.uuid),
                    "archive_uuid": str(self.archive_uuid),
                }
            )

        @staticmethod
        def from_string(string: str) -> "DayRecord":
            "从字符串加载每日记录对象。"
            from .classtype import Class
            from .attendanceinfo import AttendanceInfo
            d = json.loads(string)
            if d["type"] != DayRecord.chunk_type_name:
                raise ValueError(
                    f"类型不匹配：{d['type']} != {DayRecord.chunk_type_name}"
                )
            obj = DayRecord(
                target_class=ClassDataObj.LoadUUID(d["target_class"], Class),
                weekday=d["weekday"],
                create_utc=d["utc"],
                attendance_info=ClassDataObj.LoadUUID(d["attendance_info"], AttendanceInfo),
            )
            obj.uuid = d["uuid"]
            obj.archive_uuid = d["archive_uuid"]
            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self
