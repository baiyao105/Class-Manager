from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Self, override

from ...algorithm.types import update_object_mapping

from ...basetypes import Base

from ..basetype import ClassDataType, DataProperty, StringObjectDataKind
from ..classdataloader import ClassDataLoader

if TYPE_CHECKING:
    from .achievementtemp import AchievementTemplate
    from .student import Student
    from ..dataloaders.pydantic_loader.models.achievement import AchievementModel


class Achievement(ClassDataType):
    "一个真实被达成的成就"

    chunk_type_name: str = "Achievement"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "创建一个空的成就实例"
        from .achievementtemp import AchievementTemplate
        from .student import Student

        return cls(
            AchievementTemplate.new_dummy(),
            Student.new_dummy(),
            "1970-01-01 00:00:00.000",
            0
        )

    def __init__(
        self,
        template: AchievementTemplate,
        target: Student,
        reach_time: str | None = None,
        reach_time_key: int | None = None,
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
        self._time = reach_time
        self._time_key = reach_time_key
        self.temp = template
        self.target = target
        self.sound = self.temp.sound
        self.archive_uuid = ClassDataLoader.get_archive_uuid()

    @DataProperty
    def time(self):
        "达成时间"
        return self._time

    @time.setter
    def time(self, value: str):
        self._time = value

    @DataProperty
    def time_key(self):
        "达成时间键值"
        return self._time_key

    @time_key.setter
    def time_key(self, value: int):
        self._time_key = value

    def give(self):
        "发放成就"
        Base.log(
            "I",
            f"发放成就：target={self.target!r}, time={self.time!r}, key={self.time_key}",
        )
        self.target.achievements[self.time_key] = self

    def delete(self):
        "删除成就"
        Base.log(
            "I",
            f"删除成就：target={self.target!r}, time={self.time!r}, key={self.time_key}",
        )
        del self

    def to_string(self) -> StringObjectDataKind[Self]:
        "将成就对象转换为字符串。"
        return StringObjectDataKind(json.dumps(
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
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "从字符串加载成就对象。"
        from .achievementtemp import AchievementTemplate
        from .student import Student

        d: dict[str, Any] = json.loads(string)
        
        if d["type"] != cls.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {cls.chunk_type_name}")
        template = ClassDataLoader.LoadUUID(d["template"], AchievementTemplate)
        assert template is not None, f"成就{d['uuid']}的成就模板{template}加载失败"
        target = ClassDataLoader.LoadUUID(d["target"], Student)
        assert target is not None, f"成就{d['uuid']}的目标学生对象{target}加载失败"
        obj = cls(
            template=template,
            target=target,
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
        update_object_mapping(self, obj.__dict__)
        return self

    @override
    def to_pydantic(self) -> AchievementModel:
        """
        转换为Pydantic模型。

        :return: Pydantic模型实例
        """
        from ..dataloaders.pydantic_loader.models.achievement import AchievementModel
        return AchievementModel.from_class_data(self)
        