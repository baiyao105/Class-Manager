from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

from ..basetype import ClassDataType
from ..classdataobj import ClassDataObj

if TYPE_CHECKING:
    from .classtype import Class
    from .student import Student


class AttendanceInfo(ClassDataType):
    "考勤信息"

    chunk_type_name: Literal["AttendanceInfo"] = "AttendanceInfo"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @staticmethod
    def new_dummy():
        "返回一个空考勤信息"
        return AttendanceInfo()

    def __init__(
        self,
        target_class: str = "CLASS_TEST",
        is_early: list[Student] | None = None,
        is_late: list[Student] | None = None,
        is_late_more: list[Student] | None = None,
        is_absent: list[Student] | None = None,
        is_leave: list[Student] | None = None,
        is_leave_early: list[Student] | None = None,
        is_leave_late: list[Student] | None = None,
    ):
        """
        考勤信息

        :param target_class: 目标班级
        :param is_early: 早到的学生
        :param is_late: 晚到的学生
        :param is_late_more: 晚到得相当抽象的学生
        :param is_absent: 缺勤的学生
        :param is_leave: 临时请假的学生
        :param is_leave_early: 早退的学生
        :param is_leave_late: 晚退的学生，特指某些"热爱学校"的人（直接点我名算了）
        """

        if is_early is None:
            is_early = []
        if is_late is None:
            is_late = []
        if is_late_more is None:
            is_late_more = []
        if is_absent is None:
            is_absent = []
        if is_leave is None:
            is_leave = []
        if is_leave_early is None:
            is_leave_early = []
        if is_leave_late is None:
            is_leave_late = []

        self.target_class = target_class
        "目标班级"
        self.is_early = is_early
        "早到的学生"
        self.is_late = is_late
        "晚到（7:25-7:30）的学生"
        self.is_late_more = is_late_more
        "7:30以后到的"
        self.is_absent = is_absent
        "缺勤的学生"
        self.is_leave = is_leave
        "请假的学生"
        self.is_leave_early = is_leave_early
        "早退的学生"
        self.is_leave_late = is_leave_late
        "晚退的学生"
        self.archive_uuid = ClassDataObj.get_archive_uuid()
        "存档UUID"

    def to_string(self) -> str:
        "将考勤记录对象转为字符串。"
        return json.dumps(
            {
                "type": self.chunk_type_name,
                "target_class": self.target_class,
                "is_early": [str(s.uuid) for s in self.is_early],
                "is_late": [str(s.uuid) for s in self.is_late],
                "is_late_more": [str(s.uuid) for s in self.is_late_more],
                "is_absent": [str(s.uuid) for s in self.is_absent],
                "is_leave": [str(s.uuid) for s in self.is_leave],
                "is_leave_early": [str(s.uuid) for s in self.is_leave_early],
                "is_leave_late": [str(s.uuid) for s in self.is_leave_late],
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        )

    @staticmethod
    def from_string(string: str) -> AttendanceInfo:
        "从字符串加载出勤信息对象。"
        from .student import Student

        d = json.loads(string)
        if d["type"] != AttendanceInfo.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {AttendanceInfo.chunk_type_name}")
        obj = AttendanceInfo(
            target_class=d["target_class"],
            is_early=[ClassDataObj.LoadUUID(s, Student) for s in d["is_early"]],
            is_late=[ClassDataObj.LoadUUID(s, Student) for s in d["is_late"]],
            is_late_more=[ClassDataObj.LoadUUID(s, Student) for s in d["is_late_more"]],
            is_absent=[ClassDataObj.LoadUUID(s, Student) for s in d["is_absent"]],
            is_leave=[ClassDataObj.LoadUUID(s, Student) for s in d["is_leave"]],
            is_leave_early=[ClassDataObj.LoadUUID(s, Student) for s in d["is_leave_early"]],
            is_leave_late=[ClassDataObj.LoadUUID(s, Student) for s in d["is_leave_late"]],
        )
        obj.uuid = d["uuid"]
        obj.archive_uuid = d["archive_uuid"]
        return obj

    def is_normal(self, target_class: Class) -> list[Student]:
        "正常出勤的学生，没有缺席"
        return [
            s
            for s in target_class.students.values()
            if s.num not in [abnormal_s.num for abnormal_s in (self.is_absent)]
        ]

    @property
    def all_attended(self) -> bool:
        "今天咱班全部都出勤了（不过基本不可能）"
        return len(self.is_absent) == 0

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        self.__dict__.update(obj.__dict__)
        return self
