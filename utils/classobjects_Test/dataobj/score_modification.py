"""
分数修改历史记录
"""

import json
from typing import Literal

from utils.basetypes import Base, Object
from utils.algorithm import SupportsKeyOrdering


class ScoreModificationTemplate(Object, SupportsKeyOrdering):
    "分数加减操作的模板。"

    chunk_type_name: Literal["ScoreModificationTemplate"] = "ScoreModificationTemplate"
    "类型名"

    is_unrelated_data_type = True
    "是否是与其他班级数据类型无关联的数据类型"

    dummy: "ScoreModificationTemplate" = None
    "空的分数加减操作模板"

    @staticmethod
    def new_dummy():
        "返回一个空的分数加减操作模板"
        return ScoreModificationTemplate("dummy", 0, "dummy")

    def __init__(self,
                key:             str,
                modification:    float,
                title:           str,
                description:     str      = "该加减分模板没有详细信息。",
                cant_replace:    bool     = False,
                is_visible:      bool     = True):
        """
        分数操作模板的构造函数。

        :param key: 模板标识符
        :param modification: 模板修改分数
        :param title: 模板标题
        :param description: 模板描述
        :param cant_replace: 是否禁止替换
        :param is_visible: 是否可见
        """
        self.key = key
        self.mod = modification
        self.title = title
        self.desc = description
        self.cant_replace = cant_replace
        self.is_visible = is_visible
        self.archive_uuid = ClassObj.archive_uuid

    def __repr__(self):
        return (f"ScoreModificationTemplate("
            f"key={self.key.__repr__()}, "
            f"modification={self.mod.__repr__()}, "
            f"title={self.title.__repr__()}, "
            f"description={self.desc.__repr__()}, "
            f"cant_replace={self.cant_replace.__repr__()}, "
            f"is_visible={self.is_visible.__repr__()})")

    def to_string(self):
        "将分数修改记录对象转为字符串。"
        return json.dumps(
            {
                "type": self.chunk_type_name,
                "key": self.key,
                "modification": self.mod,
                "title": self.title,
                "description": self.desc,
                "cant_replace": self.cant_replace,
                "is_visible": self.is_visible,
                "uuid": self.uuid,
                "archive_uuid": self.archive_uuid
            }
        )



    @staticmethod
    def from_string(string: str):
        "将字符串转化为分数加减模板对象。"
        string = json.loads(string)
        if string["type"] != ScoreModificationTemplate.chunk_type_name:
            raise TypeError(f"类型不匹配：{string['type']} != "
                            f"{ScoreModificationTemplate.chunk_type_name}")
        obj = ScoreModificationTemplate(
            key=string["key"],
            modification=string["modification"],
            title=string["title"],
            description=string["description"],
            cant_replace=string["cant_replace"],
            is_visible=string["is_visible"]
        )
        obj.uuid = string["uuid"]
        obj.archive_uuid = string["archive_uuid"]

        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        self.__dict__.update(obj.__dict__)
        return self