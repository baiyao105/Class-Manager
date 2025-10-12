from __future__ import annotations

import json
from typing import (Literal, TYPE_CHECKING, Dict, Any)
from ..classdataobj import ClassDataObj
from ..basetype import ClassDataType
from utils.basetypes import Base


if TYPE_CHECKING:
    from .student import Student
    from .achievementtemp import AchievementTemplate


class Achievement(ClassDataType):
    "一个真实被达成的成就"

    chunk_type_name: Literal["Achievement"] = "Achievement"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    dummy: "Achievement" = None
    "空的成就实例"

    @staticmethod
    def new_dummy():
        "创建一个空的成就实例"
        from .achievementtemp import AchievementTemplate
        from .student import Student
        return Achievement(
            AchievementTemplate.new_dummy(),
            Student.new_dummy(),
            "1970-01-01 00:00:00.000",
            0,
        )

    def __init__(
        self,
        template: AchievementTemplate,
        target: Student,
        reach_time: str = None,
        reach_time_key: int = None,
    ):
        """一个成就的实例。

        :param template: 成就模板
        :param target: 成就的获得者
        :param reach_time: 达成时间
        :param reach_time_key: 达成时间键值
        """
        if reach_time is None:
            reach_time = Base.gettime()
        if reach_time_key is None:
            reach_time_key = Base.utc()
        self.time = reach_time
        self.time_key = reach_time_key
        self.temp = template
        self.target = target
        self.sound = self.temp.sound
        self.archive_uuid = ClassDataObj.get_archive_uuid()

    def give(self):
        "发放成就"
        Base.log(
            "I",
            f"发放成就：target={repr(self.target)}, "
            f"time={repr(self.time)}, key={self.time_key}",
        )
        self.target.achievements[self.time_key] = self

    def delete(self):
        "删除成就"
        Base.log(
            "I",
            f"删除成就：target={repr(self.target)}, "
            f"time={repr(self.time)}, key={self.time_key}",
        )
        del self

    def to_string(self):
        "将成就对象转换为字符串。"
        return json.dumps(
            {
                "type": self.chunk_type_name,
                "time": self.time,
                "time_key": self.time_key,
                "template": str(self.temp.uuid),
                "target": str(self.target.uuid),
                "sound": self.sound,
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        )

    @staticmethod
    def from_string(string: str):
        "从字符串加载成就对象。"
        from .achievementtemp import AchievementTemplate
        from .student import Student
        d: Dict[str, Any] = json.loads(string)
        if d["type"] != Achievement.chunk_type_name:
            raise ValueError(
                f"类型不匹配：{d['type']} != {Achievement.chunk_type_name}"
            )
        obj = Achievement(
            template=ClassDataObj.LoadUUID(d["template"], AchievementTemplate),
            target=ClassDataObj.LoadUUID(d["target"], Student),
            reach_time=d["time"],
            reach_time_key=d["time_key"],
        )
        obj.sound = d["sound"]
        obj.uuid = d["uuid"]
        obj.archive_uuid = d["archive_uuid"]
        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        self.__dict__.update(obj.__dict__)
        return self