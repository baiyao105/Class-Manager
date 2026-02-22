"""
历史记录的Pydantic模型。
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..base import PydanticModelBase, PydanticReference

from ...objects.classtype import Class
from ...objects.dayrecord import DayRecord
from ...objects.history import History
from ...basetype import ClassDataTypeUUID

class HistoryModel(PydanticModelBase[History]):
    "历史记录的Pydantic模型"

    chunk_type_name: ClassVar[str] = "History"
    "类型名"

    time: float = Field()
    "保存时间"

    class_refs: dict[str, PydanticReference[Class]] = Field(default_factory=dict)
    "班级引用字典"

    weekday_refs: list[tuple[str, float, PydanticReference[DayRecord]]] = Field(default_factory=list)
    "每日记录引用列表(class_key, time_key, ref)"

    is_current: bool = Field(default=False)
    "是否为当前未归档存档"

    @classmethod
    def from_class_data(cls, data: History) -> HistoryModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        class_refs: dict[str, PydanticReference[Class]] = {
            k: PydanticReference.from_object(v)
            for k, v in data.classes.items()
        }

        weekday_refs: list[tuple[str, float, PydanticReference[DayRecord]]] = []
        for class_key, day_dict in data.weekdays.items():
            for time_key, day in day_dict.items():
                weekday_refs.append((class_key, time_key, PydanticReference.from_object(day)))

        is_current = data.uuid is None


        return cls(
            uuid=data.uuid or ClassDataTypeUUID(History),
            archive_uuid=data.archive_uuid,
            time=data.time,
            class_refs=class_refs,
            weekday_refs=weekday_refs,
            is_current=is_current,
        )

    def to_class_data(self) -> History:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """
        classes: dict[str, Class] = {}
        for key, ref in self.class_refs.items():
            classes[key] = ref.resolve()

        weekdays: dict[str, dict[float, DayRecord]] = {}
        for class_key, time_key, ref in self.weekday_refs:
            if class_key not in weekdays:
                weekdays[class_key] = {}
            weekdays[class_key][time_key] = ref.resolve()

        obj = History(
            classes=classes,
            weekdays=weekdays,
            save_time=self.time
        )
        if self.is_current:
            obj.uuid = None
        else:
            obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid

        return obj
