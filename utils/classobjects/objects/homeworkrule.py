from __future__ import annotations

import json
from typing import (Literal, Dict)
from ..classdataobj import ClassDataObj
from ..basetype import ClassDataType
from utils.algorithm import SupportsKeyOrdering
from .scoremodtemplate import ScoreModificationTemplate


class HomeworkRule(ClassDataType, SupportsKeyOrdering):
    "作业规则"

    chunk_type_name: Literal["HomeworkRule"] = "HomeworkRule"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    dummy: "HomeworkRule" = None
    "空作业规则"

    @staticmethod
    def new_dummy():
        "返回一个空作业规则"
        return HomeworkRule("dummy", "dummy", "dummy", {})

    def __init__(
        self,
        key: str,
        subject_name: str,
        ruler: str,
        rule_mapping: Dict[str, "ScoreModificationTemplate"],
    ):
        """
        作业规则构造函数。

        :param key: 在homework_rules中对应的key
        :param subject_name: 科目名称
        :param ruler: 规则制定者
        :param rule_mapping: 规则映射
        """
        self.key = key
        self.subject_name = subject_name
        self.ruler = ruler
        self.rule_mapping = rule_mapping
        self.archive_uuid = ClassDataObj.get_archive_uuid()

    def to_string(self):
        "将作业规则对象转为字符串。"
        return json.dumps(
            {
                "type": self.chunk_type_name,
                "key": self.key,
                "subject_name": self.subject_name,
                "ruler": self.ruler,
                "rule_mapping": dict(
                    [(n, str(t.uuid)) for n, t in self.rule_mapping.items()]
                ),
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        )

    @staticmethod
    def from_string(s: str):
        "从字符串加载作业规则对象。"
        d = json.loads(s)
        if d["type"] != HomeworkRule.chunk_type_name:
            raise ValueError(
                f"类型不匹配：{d['type']} != "
                f"{HomeworkRule.chunk_type_name}"
            )
        obj = HomeworkRule(
            key=d["key"],
            subject_name=d["subject_name"],
            ruler=d["ruler"],
            rule_mapping={
                n: ClassDataObj.LoadUUID(t, ScoreModificationTemplate)
                for n, t in d["rule_mapping"].items()
            },
        )
        obj.uuid = d["uuid"]
        obj.archive_uuid = d["archive_uuid"]
        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        self.__dict__.update(obj.__dict__)
        return self