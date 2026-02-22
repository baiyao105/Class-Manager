"""
HomeworkRule的Pydantic模型。
"""

from __future__ import annotations
from typing import ClassVar


from pydantic import Field

from ..base import PydanticModelBase, PydanticReference
from ...objects.homeworkrule import HomeworkRule
from ...objects.scoremodtemplate import ScoreModificationTemplate


class HomeworkRuleModel(PydanticModelBase[HomeworkRule]):
    """
    作业规则的Pydantic模型。
    """

    chunk_type_name: ClassVar[str] = "HomeworkRule"
    "类型名"

    key: str
    "在homework_rules中对应的key"

    subject_name: str
    "科目名称"

    ruler: str
    "规则制定者"

    rule_mapping: dict[str, PydanticReference[ScoreModificationTemplate]] = Field(default_factory=dict)
    "规则映射"

    @classmethod
    def from_class_data(cls, data: HomeworkRule) -> HomeworkRuleModel:
        """
        从HomeworkRule对象创建Pydantic模型。

        :param data: HomeworkRule对象
        :return: HomeworkRuleModel实例
        """
        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            key=data.key,
            subject_name=data.subject_name,
            ruler=data.ruler,
            rule_mapping={
                k: PydanticReference.from_object(v)
                for k, v in data.rule_mapping.items()
            }
        )

    def to_class_data(self) -> HomeworkRule:
        """
        转换为HomeworkRule对象。

        :return: HomeworkRule对象实例
        """
        obj = HomeworkRule(
            key=self.key,
            subject_name=self.subject_name,
            ruler=self.ruler,
            rule_mapping={k: v.resolve() for k, v in self.rule_mapping.items()}
        )
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid
        return obj
