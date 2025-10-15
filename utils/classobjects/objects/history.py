from __future__ import annotations

import json
import time
from typing import TYPE_CHECKING, Literal, Self
from uuid import UUID

from ..basetype import ClassDataType, ClassDataTypeUUID
from ..classdataobj import ClassDataObj

if TYPE_CHECKING:
    from .classtype import Class
    from .dayrecord import DayRecord


class History(ClassDataType):
    "每次重置保留的历史记录"

    chunk_type_name: Literal["History"] = "History"
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
        self._uuid: ClassDataTypeUUID[Self] | None = None
        self.classes = dict(classes)
        self.time = save_time or time.time()
        weekdays = weekdays.copy()

        self.weekdays: dict[str, dict[float, DayRecord]] = weekdays

        self.uuid = self.archive_uuid = ClassDataObj.get_archive_uuid()
        # IMPORTANT: 这里的对象uuid和归档uuid是一样的

    def __repr__(self):
        return f"<History object at time {self.time:.3f}>"

    @property
    def uuid(self) -> ClassDataTypeUUID[Self] | None:
        """
        该班级数据类型的唯一标识符。

        特别的是，History类型的uuid可以为None。
        """
        if not hasattr(self, "_uuid"):
            self._uuid = ClassDataTypeUUID(self.__class__)
        return self._uuid

    @uuid.setter
    def uuid(self, value: UUID | ClassDataTypeUUID[Self] | str | None):
        if isinstance(value, ClassDataTypeUUID):
            self._uuid = value

        elif isinstance(value, UUID):
            self._uuid = ClassDataTypeUUID(self.__class__, value)

        elif isinstance(value, str):
            self._uuid = ClassDataTypeUUID(self.__class__, UUID(value.replace("-", "")))

        elif value is None:
            self._uuid = None

        else:
            raise TypeError(f"uuid.setter需要提供UUID，ClassDataTypeUUID或者str， 但提供了{type(value)}")

    def to_string(self):
        "将历史记录转换为字符串。"

        return json.dumps(
            {
                "classes": {k: str(v.uuid) for k, v in self.classes.items()},
                "time": self.time,
                "weekdays": [
                    [(_class, time_key, str(day.uuid)) for time_key, day in item.items()]
                    for _class, item in self.weekdays.items()
                ],
                "uuid": str(self.uuid),
                "archive_uuid": self.archive_uuid,
            }
        )

    @staticmethod
    def from_string(s: str) -> History:
        "从字符串加载历史记录。"
        from .classtype import Class
        from .dayrecord import DayRecord

        d = json.loads(s)
        if d["type"] != History.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {History.chunk_type_name}")
        obj = History(
            classes={k: ClassDataObj.LoadUUID(v, Class) for k, v in d["classes"].items()},
            weekdays={},
            save_time=d["time"],
        )
        for _class, time_key, day_uuid in d["weekdays"]:
            if _class not in obj.weekdays:
                obj.weekdays[_class] = {}
            obj.weekdays[_class][time_key] = ClassDataObj.LoadUUID(day_uuid, DayRecord)
        obj.uuid = d["uuid"]
        obj.archive_uuid = d["archive_uuid"]
        assert obj.uuid == obj.archive_uuid, (
            f"对于一个历史记录, 它的对象uuid和归档uuid必须保持一致（当前一个是{obj.uuid}, 另一个是{obj.archive_uuid}）"
        )
        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        self.__dict__.update(obj.__dict__)
        return self

    @staticmethod
    def new_dummy():
        "创建一个空的历史记录。"
        return History({}, {})
