from __future__ import annotations

import json

from abc import ABC, abstractmethod
from typing import Any, Literal, Callable
from ...basetypes import Base
from ..basetype import ClassDataType



BasicDataTypes = int | float | str | bool | None
JsonLoadableBasicTypes = BasicDataTypes | list[BasicDataTypes] | dict[str, BasicDataTypes]
JsonLoadableTypes = JsonLoadableBasicTypes | list[JsonLoadableBasicTypes] | dict[str, JsonLoadableBasicTypes]


class DataTag(ClassDataType):
    "一个标签。"

    chunk_type_name: Literal["DataTag"] = "DataTag"

    is_unrelated_data_type = True

    registered_tags: dict[str, tuple[str, Callable[[JsonLoadableTypes, dict[str, Any] | None], bool] | None, dict[str, Any] | None]] = {}
    "已注册的标签类别"

    @staticmethod
    def register(key: str, desc: str | None = None, 
                    validator: Callable[[JsonLoadableTypes, dict[str, Any] | None], bool] | None = None, 
                    data: dict[str, Any] | None = None):
        "注册一个标签类别。"
        DataTag.registered_tags[key] = (desc or "这个标签没有提供具体的描述。", validator, data)

    @staticmethod
    def unregister(key: str):
        "注销一个标签类别。"
        try:
            del DataTag.registered_tags[key]
        except KeyError:
            raise KeyError(f"标签类别{key!r}未注册")
        
    @staticmethod
    def registered(key: str) -> bool:
        "判断一个标签类别是否已注册。"
        try:
            DataTag.registered_tags[key]    # 省点性能
            return True
        except KeyError:
            return False

    @staticmethod
    def get_registered_tag(key: str) -> tuple[str, Callable[[JsonLoadableTypes, dict[str, Any] | None], bool] | None, dict[str, Any] | None]:
        "获取已注册的标签类别。"
        try:
            return DataTag.registered_tags[key]
        except KeyError:
            raise KeyError(f"标签类别{key!r}未注册")


    def __init__(self, key: str, data: JsonLoadableTypes | None = None) -> None:
        """
        构造函数。

        :param key: 标签的键
        :param data: 标签携带的数据，可选
        """
        self.key = key
        self.data = data
        DataTag.validate(self.key, self.data)


    def to_string(self) -> str:
        return json.dumps({
            "key": self.key,
            "data": json.dumps(self.data)
        })
    
    @staticmethod
    def validate(key: str, src: JsonLoadableTypes | None = None):
        """
        验证标签。
        
        :param key: 标签的键
        :param src: 标签携带的数据，可选
        :raises ValueError: 如果标签验证失败
        """
        if not DataTag.registered(key):
            Base.log("W", f"标签类别{key!r}未注册，已自动注册", "DataTag.inst_from_string")
            DataTag.register(key)
        validator, data = DataTag.get_registered_tag(key)[1:]
        if validator is not None:
            try:
                if not validator(src, data):
                    Base.log("W", f"标签类别{key!r}的数据验证失败", "DataTag.inst_from_string")
                    raise ValueError(f"标签类别{key!r}的数据验证失败")
            except:
                raise ValueError(f"标签类别{key!r}的数据验证失败/校验器出错")
    
    def inst_from_string(self, string: str):
        d = json.loads(string)
        self.key = d["key"]
        self.data = json.loads(d["data"])
        DataTag.validate(self.key, self.data)
        return self
    
    @staticmethod
    def new_dummy():
        return DataTag("dummy")

    @staticmethod
    def from_string(string: str) -> DataTag:
        "从字符串中读取标签。"
        d = json.loads(string)
        key = d["key"]
        if not DataTag.registered(key):
            Base.log
        data = json.loads(d["data"])
        return DataTag(key, data)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, DataTag):
            return False
        return self.key == other.key and self.data == other.data
    
    def is_same_type(self, other: DataTag) -> bool:
        "判断两个标签是否属于同一类型。"
        return self.key == other.key
    


class TagSigned(ABC):
    "一个带有标签的类。"

    def __init__(self) -> None:
        super().__init__()
        self.tags: list[DataTag] = []
        "标签列表"

    def get_tag(self, key: str) -> DataTag | None:
        "获取标签。"
        for tag in self.tags:
            if tag.key == key:
                return tag
        return None

    def add_tag(self, tag: DataTag):
        "添加标签。"
        self.tags.append(tag)

    def remove_tag(self, tag: DataTag | str):
        "移除标签。"
        if isinstance(tag, str):
            for t in self.tags:
                if t.key == tag:
                    self.tags.remove(t)
                    return
        else:
            self.tags.remove(tag)

    def has_tag(self, tag: DataTag | str) -> bool:
        "判断是否有标签。"
        if isinstance(tag, str):
            for t in self.tags:
                if t.key == tag:
                    return True
            return False
        else:
            return tag in self.tags