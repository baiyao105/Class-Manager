"""
成就模板的Pydantic模型。
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import Field

from ..base import PydanticModelBase

from ...objects.achievementtemp import AchievementTemplate


class AchievementTemplateModel(PydanticModelBase[AchievementTemplate]):
    "成就模板的Pydantic模型"

    chunk_type_name: ClassVar[str] = "AchievementTemplate"
    "类型名"

    key: str = Field()
    "成就key"

    name: str = Field()
    "成就名称"

    description: str = Field()
    "成就描述"

    active: bool = Field(default=True)
    "是否激活"

    when_triggered: list[str] = Field(default_factory=lambda: ["any"])
    "触发时机"

    sound: str | None = Field(default=None)
    "音效"

    icon: str | None = Field(default=None)
    "图标"

    condition_info: str = Field(default="具体就是这样，我也不清楚，没写")
    "条件描述"

    further_info: str = Field(default="貌似是那几个开发者懒得进行文学创作了，所以没有进一步描述")
    "进一步描述"

    name_equals: list[str] | None = Field(default=None)
    "名称等于列表"

    name_not_equals: list[str] | None = Field(default=None)
    "名称不等于列表"

    num_equals: list[int] | None = Field(default=None)
    "学号等于列表"

    num_not_equals: list[int] | None = Field(default=None)
    "学号不等于列表"

    score_range: list[list[float]] | None = Field(default=None)
    "分数范围列表"

    score_rank_range: tuple[int, int] | None = Field(default=None)
    "名次范围"

    highest_score_range: tuple[float, float] | None = Field(default=None)
    "最高分数范围"

    lowest_score_range: tuple[float, float] | None = Field(default=None)
    "最低分数范围"

    highest_score_cause_range: tuple[int, int] | None = Field(default=None)
    "最高分产生时间范围"

    lowest_score_cause_range: tuple[int, int] | None = Field(default=None)
    "最低分产生时间范围"

    modify_key_range: list[list[Any]] | None = Field(default=None)
    "指定点评次数范围"

    @classmethod
    def from_class_data(cls, data: AchievementTemplate) -> AchievementTemplateModel:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """
        name_equals: list[str] | None = None
        if data.name_eq is not None:
            name_equals = list(data.name_eq)

        name_not_equals: list[str] | None = None
        if data.name_ne is not None:
            name_not_equals = list(data.name_ne)

        num_equals: list[int] | None = None
        if data.num_eq is not None:
            num_equals = list(data.num_eq)

        num_not_equals: list[int] | None = None
        if data.num_ne is not None:
            num_not_equals = list(data.num_ne)

        score_range: list[list[float]] | None = None
        if data.score_range is not None:
            score_range = [[float(x) for x in item] for item in data.score_range]

        score_rank_range: tuple[int, int] | None = None
        if data.score_rank_down_limit is not None and data.score_rank_up_limit is not None:
            score_rank_range = (data.score_rank_down_limit, data.score_rank_up_limit)

        highest_score_range: tuple[float, float] | None = None
        if data.highest_score_down_limit is not None and data.highest_score_up_limit is not None:
            highest_score_range = (data.highest_score_down_limit, data.highest_score_up_limit)

        lowest_score_range: tuple[float, float] | None = None
        if data.lowest_score_down_limit is not None and data.lowest_score_up_limit is not None:
            lowest_score_range = (data.lowest_score_down_limit, data.lowest_score_up_limit)

        highest_score_cause_range: tuple[int, int] | None = None
        if data.highest_score_cause_range_down_limit is not None and data.highest_score_cause_range_up_limit is not None:
            highest_score_cause_range = (
                data.highest_score_cause_range_down_limit,
                data.highest_score_cause_range_up_limit,
            )

        lowest_score_cause_range: tuple[int, int] | None = None
        if data.lowest_score_cause_range_down_limit is not None and data.lowest_score_cause_range_up_limit is not None:
            lowest_score_cause_range = (
                data.lowest_score_cause_range_down_limit,
                data.lowest_score_cause_range_up_limit,
            )

        modify_key_range: list[list[Any]] | None = None
        if data.modify_ranges_orig is not None:
            modify_key_range = [list(item) for item in data.modify_ranges_orig]

        when_triggered = list(data.when_triggered) if data.when_triggered else ["any"]
        sound = data.sound
        icon = data.icon
        condition_info = data.condition_info
        further_info = data.further_info

        return cls(
            uuid=data.uuid,
            archive_uuid=data.archive_uuid,
            key=data.key,
            name=data.name,
            description=data.desc,
            active=data.active,
            when_triggered=list(when_triggered),
            sound=sound,
            icon=icon,
            condition_info=condition_info,
            further_info=further_info,
            name_equals=name_equals,
            name_not_equals=name_not_equals,
            num_equals=num_equals,
            num_not_equals=num_not_equals,
            score_range=score_range,
            score_rank_range=score_rank_range,
            highest_score_range=highest_score_range,
            lowest_score_range=lowest_score_range,
            highest_score_cause_range=highest_score_cause_range,
            lowest_score_cause_range=lowest_score_cause_range,
            modify_key_range=modify_key_range
        )

    def to_class_data(self) -> AchievementTemplate:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

        kwargs: dict[str, Any] = {
            "key": self.key,
            "name": self.name,
            "desc": self.description,
            "when_triggered": self.when_triggered,
            "sound": self.sound,
            "icon": self.icon,
            "condition_info": self.condition_info,
            "further_info": self.further_info,
        }

        if self.name_equals is not None:
            kwargs["name_equals"] = self.name_equals

        if self.name_not_equals is not None:
            kwargs["name_not_equals"] = self.name_not_equals

        if self.num_equals is not None:
            kwargs["num_equals"] = self.num_equals

        if self.num_not_equals is not None:
            kwargs["num_not_equals"] = self.num_not_equals

        if self.score_range is not None:
            kwargs["score_range"] = [tuple(item) for item in self.score_range]

        if self.score_rank_range is not None:
            kwargs["score_rank_range"] = self.score_rank_range

        if self.highest_score_range is not None:
            kwargs["highest_score_range"] = self.highest_score_range

        if self.lowest_score_range is not None:
            kwargs["lowest_score_range"] = self.lowest_score_range

        if self.highest_score_cause_range is not None:
            kwargs["highest_score_cause_range"] = self.highest_score_cause_range

        if self.lowest_score_cause_range is not None:
            kwargs["lowest_score_cause_range"] = self.lowest_score_cause_range

        if self.modify_key_range is not None:
            kwargs["modify_key_range"] = [tuple(item) for item in self.modify_key_range]

        obj = AchievementTemplate(**kwargs)
        obj.uuid = self.uuid
        obj.archive_uuid = self.archive_uuid
        obj.active = self.active
        return obj

    