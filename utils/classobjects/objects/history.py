from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Any, Self, override
from uuid import UUID

from ...algorithm.types import update_object_mapping

from ..basetype import ClassDataType, ClassDataTypeUUID, StringObjectDataKind
from ..classdataloader import ClassDataLoader

if TYPE_CHECKING:
    from .classtype import Class
    from .dayrecord import DayRecord


class History(ClassDataType):
    "每次重置保留的历史记录"

    chunk_type_name: str = "History"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    def __init__(
        self,
        classes: dict[str, Class],
        weekdays: dict[str, dict[float, DayRecord]],
        save_time: float | None = None,
    ):
        super().__init__()
        self._uuid_priv: ClassDataTypeUUID[Self] | None = None
        self.classes = dict(classes)
        self.time = save_time or time.time()
        weekdays = weekdays.copy()

        self.weekdays: dict[str, dict[float, DayRecord]] = weekdays

        self.uuid = self.archive_uuid = ClassDataLoader.get_archive_uuid()
        # IMPORTANT: 这里的对象uuid和归档uuid是一样的

    def __repr__(self):
        return f"<History object at time {self.time:.3f}>"

    @property
    def uuid(self) -> ClassDataTypeUUID[Self] | None: # pyright: ignore[reportIncompatibleMethodOverride]
        """
        该班级数据类型的唯一标识符。

        特别的是，History类型的uuid可以为None。
        """
        if not hasattr(self, "_uuid_priv"):
            self._uuid_priv = ClassDataTypeUUID(self.__class__)
        return self._uuid_priv

    @uuid.setter
    def uuid(self, value: UUID | ClassDataTypeUUID[Self] | str | None):
        if isinstance(value, ClassDataTypeUUID):
            self._uuid_priv = value

        elif isinstance(value, UUID):
            self._uuid_priv = ClassDataTypeUUID(self.__class__, value)

        elif isinstance(value, str):
            self._uuid_priv = ClassDataTypeUUID(self.__class__, UUID(value.replace("-", "")))

        elif value is None:
            self._uuid_priv = None

        else:
            raise TypeError(f"uuid.setter需要提供UUID，ClassDataTypeUUID或者str， 但提供了{type(value)}")
    
    def dump_classes(self) -> dict[str, str]:
        "将班级字典转换为字符串字典。"
        return {k: str(v.uuid) for k, v in self.classes.items()}

    @staticmethod
    def load_classes(d: dict[str, Any]) -> dict[str, Class]:
        "从字符串字典加载班级对象。"
        from .classtype import Class
        result: dict[str, Class] = {}
        for k, v in d["classes"].items():
            cls = ClassDataLoader.LoadUUID(v, Class)
            assert cls is not None, f"历史记录的班级{k}加载失败"
            result[k] = cls
        return result

    def dump_weekdays(self) -> list[list[tuple[str, float, str]]]:
        "将周记录字典转换为字符串列表。"
        return [
            [(_class, time_key, str(day.uuid)) for time_key, day in item.items()]
            for _class, item in self.weekdays.items()
        ]
    
    @staticmethod
    def load_weekdays(d: dict[str, Any]) -> dict[str, dict[float, DayRecord]]:
        "从字符串列表加载周记录对象。"
        from .dayrecord import DayRecord
        result: dict[str, dict[float, DayRecord]] = {}
        for _class, time_key, day_uuid in d["weekdays"]:
            if _class not in result:
                result[_class] = {}
            item = ClassDataLoader.LoadUUID(day_uuid, DayRecord)
            assert item is not None, f"历史记录的班级{_class}的时间{time_key}的记录加载失败"
            result[_class][time_key] = item
        return result

    def to_string(self) -> StringObjectDataKind[Self]:
        "将历史记录转换为字符串。"
        return StringObjectDataKind(json.dumps(
            {
                "classes": self.dump_classes(),
                "time": self.time,
                "weekdays": self.dump_weekdays(),
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "从字符串加载历史记录。"
        d = json.loads(string)
        if d["type"] != cls.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {cls.chunk_type_name}")
        obj = cls(
            classes=cls.load_classes(d),
            weekdays=cls.load_weekdays(d),
            save_time=d["time"],
        )
        obj.uuid = d["uuid"]
        obj.archive_uuid = d["archive_uuid"]
        assert obj.uuid == obj.archive_uuid, (
            f"对于一个历史记录, 它的对象uuid和归档uuid必须保持一致（当前uuid是{obj.uuid}, archive_uuid是{obj.archive_uuid}）"
        )
        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        update_object_mapping(self, obj.__dict__)
        return self

    @classmethod
    def new_dummy(cls) -> Self:
        "创建一个空的历史记录。"
        return cls({}, {})

    @override
    def to_pydantic(self):
        """
        转换为Pydantic模型。

        :return: Pydantic模型实例
        """
        from ..dataloaders.pydantic_loader.models.history import HistoryModel
        return HistoryModel.from_class_data(self)
