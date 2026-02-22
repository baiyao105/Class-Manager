from __future__ import annotations

import json
from typing import Any, Self, override

from ...algorithm import SupportsKeyOrdering, update_object_mapping

from ..basetype import ClassDataType, StringObjectDataKind
from ..classdataloader import ClassDataLoader
from .scoremodtemplate import ScoreModificationTemplate


class HomeworkRule(ClassDataType, SupportsKeyOrdering):
    "作业规则"

    chunk_type_name: str = "HomeworkRule"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "返回一个空作业规则"
        return cls("dummy", "dummy", "dummy", {})

    def __init__(
        self,
        key: str,
        subject_name: str,
        ruler: str,
        rule_mapping: dict[str, ScoreModificationTemplate],
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
        self.archive_uuid = ClassDataLoader.get_archive_uuid()
    
    def dump_rules(self) -> dict[str, str]:
        "将规则映射转换为字符串映射。"
        return {n: str(t.uuid) for n, t in self.rule_mapping.items()}
    
    @staticmethod
    def load_rules(d: dict[str, Any]) -> dict[str, ScoreModificationTemplate]:
        "从字符串映射加载规则映射。"
        from .scoremodtemplate import ScoreModificationTemplate
        result: dict[str, ScoreModificationTemplate] = {}
        for n, t in d.items():
            item = ClassDataLoader.LoadUUID(t, ScoreModificationTemplate)
            assert item is not None, f"作业规则的规则{n}加载失败"
            result[n] = item
        return result

    def to_string(self) -> StringObjectDataKind[Self]:
        "将作业规则对象转为字符串。"
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "key": self.key,
                "subject_name": self.subject_name,
                "ruler": self.ruler,
                "rule_mapping": self.dump_rules(),
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "从字符串加载作业规则对象。"
        d = json.loads(string)
        if d["type"] != cls.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {cls.chunk_type_name}")
        obj = cls(
            key=d["key"],
            subject_name=d["subject_name"],
            ruler=d["ruler"],
            rule_mapping=cls.load_rules(d["rule_mapping"]),
        )
        obj.uuid = d["uuid"]
        obj.archive_uuid = d["archive_uuid"]
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
        from ..dataloaders.pydantic_loader.models.homework_rule import HomeworkRuleModel
        return HomeworkRuleModel.from_class_data(self)


