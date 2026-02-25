from __future__ import annotations

import json
from typing import Any, Self, override

from ...algorithm import SupportsKeyOrdering, update_object_mapping

from ..basetype import ClassDataType, DataProperty, StringObjectDataKind
from ..classdataloader import ClassDataLoader


class ScoreModificationTemplate(ClassDataType, SupportsKeyOrdering):
    "分数加减操作的模板。"

    chunk_type_name: str = "ScoreModificationTemplate"
    "类型名"

    is_unrelated_data_type = True
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "返回一个空的分数加减操作模板"
        return cls("dummy", 0, "dummy")

    def __init__(
        self,
        key: str,
        modification: float,
        title: str,
        description: str = "该加减分模板没有详细信息。",
        cant_replace: bool = False,
        is_visible: bool = True,
    ):
        """
        分数操作模板的构造函数。

        :param key: 模板标识符
        :param modification: 模板修改分数
        :param title: 模板标题
        :param description: 模板描述
        :param cant_replace: 是否禁止替换
        :param is_visible: 是否可见
        """
        super().__init__()
        self.key = key
        self._mod = modification
        self._title = title
        self.desc = description
        self.cant_replace = cant_replace
        self._is_visible = is_visible
        self.archive_uuid = ClassDataLoader.get_archive_uuid()

    @DataProperty
    def mod(self):
        "模板修改分数"
        return self._mod

    @mod.setter
    def mod(self, value: float):
        self._mod = value

    @DataProperty
    def title(self):
        "模板标题"
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    @DataProperty
    def is_visible(self):
        "是否可见"
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value: bool):
        self._is_visible = value

    def __repr__(self):
        return (
            f"ScoreModificationTemplate("
            f"key={self.key.__repr__()}, "
            f"modification={self.mod.__repr__()}, "
            f"title={self.title.__repr__()}, "
            f"description={self.desc.__repr__()}, "
            f"cant_replace={self.cant_replace.__repr__()}, "
            f"is_visible={self.is_visible.__repr__()})"
        )

    def to_string(self) -> StringObjectDataKind[Self]:
        "将分数修改记录对象转为字符串。"
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "key": self.key,
                "modification": self.mod,
                "title": self.title,
                "description": self.desc,
                "cant_replace": self.cant_replace,
                "is_visible": self.is_visible,
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "将字符串转化为分数加减模板对象。"
        data: dict[str, Any] = json.loads(string)
        if data["type"] != cls.chunk_type_name:
            raise TypeError(f"类型不匹配：{data['type']} != {cls.chunk_type_name}")
        obj = cls(
            key=data["key"],
            modification=data["modification"],
            title=data["title"],
            description=data["description"],
            cant_replace=data["cant_replace"],
            is_visible=data["is_visible"],
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
        from ..dataloaders.pydantic_loader.models.score_template import ScoreTemplateModel
        return ScoreTemplateModel.from_class_data(self)
