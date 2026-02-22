from __future__ import annotations

import base64
import json
import pickle
from collections.abc import Callable
from typing import Any, Literal, Self, override

import dill as pickle # type: ignore

from ...algorithm import SupportsKeyOrdering, update_object_mapping
from ...basetypes import Base
from ...consts import inf, runtime_flags

from ..basetype import ClassDataType, StringObjectDataKind
from ..classdataloader import ClassDataLoader
from .classdata import ClassData

from ..observers.classstatobs import ClassStatusObserver
from .student import Student


class AchievementTemplate(ClassDataType, SupportsKeyOrdering):
    "成就模板"

    chunk_type_name: str = "AchievementTemplate"
    "类型名"

    is_unrelated_data_type = True
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "返回一个空的成就模板"
        t = cls(
            "dummy",
            "这个成就永远不会被达成",
            "就是不可能达成",
        )
        t.active = False
        return t

    def __init__(
        self,
        key: str,
        name: str,
        desc: str,
        # 满足以下所有条件才会给成就
        when_triggered: Literal["any", "on_reset"] | list[Literal["any", "on_reset"]] = "any",  # 触发时机
        # 名称等于/在列表中
        name_equals: str | list[str] | None = None,
        # 学号等于/在列表中
        num_equals: int | list[int] | None = None,
        # 名称不等于/在列表中
        name_not_equals: str | list[str] | None = None,
        # 学号不等于/在列表中
        num_not_equals: int | list[int] | None = None,
        score_range: tuple[float, float] | list[tuple[float, float]] | None = None,  # 分数范围
        # 名次范围（不计算并列）
        score_rank_range: tuple[int, int] | None = None,
        # 最高分数范围
        highest_score_range: tuple[float, float] | None = None,
        # 最低分数范围
        lowest_score_range: tuple[float, float] | None = None,
        highest_score_cause_range: tuple[int, int] | None = None,  # 最高分产生时间的范围（utc，*1000）
        # 最低分产生时间的范围
        lowest_score_cause_range: tuple[int, int] | None = None,
        modify_key_range: tuple[str, int | float, int | float]
        | list[tuple[str, int | float, int | float]]
        | None = None,
        # 指定点评次数的范围（必须全部符合）
        others: Callable[[ClassData], bool] | list[Callable[[ClassData], bool]] | None = None,
        # 其他条件
        sound: str | None = None,
        icon: str | None = None,
        condition_info: str = "具体就是这样，我也不清楚，没写",
        further_info: str = "貌似是那几个开发者懒得进行文学创作了，所以没有进一步描述",
    ):
        """
        成就模板构造函数。

        :param key: 成就key
        :param name: 成就名称
        :param desc: 成就描述
        :param when_triggered: 触发时机
        :param name_equals: 名称等于/在列表中
        :param num_equals: 学号等于/在列表中
        :param score_range: 分数范围
        :param score_rank_range: 名次范围（不计算并列的，名词按1-2-2-3-3之类计算）
        :param highest_score_range: 最高分数范围
        :param lowest_score_range: 最低分数范围
        :param highest_score_cause_range: 最高分产生时间的范围（utc，*1000）
        :param lowest_score_cause_range: 最低分产生时间的范围
        :param modify_key_range: 指定点评次数的范围（必须全部符合）
        :param others: 一个或者一个list的lambda或者function，传进来一个Student
        :param sound: 成就达成时的音效
        :param icon: 成就图标（在提示中的）
        """

        self.key = key
        self.name = name
        self.desc = desc

        self.active = True

        self.name_eq: list[str] | None = None
        if name_equals is not None:
            self.name_eq = list(name_equals) if isinstance(name_equals, list) else [name_equals]

        self.name_ne: list[str] | None = None
        if name_not_equals is not None:
            self.name_ne = list(name_not_equals) if isinstance(name_not_equals, list) else [name_not_equals]

        self.num_eq: list[int] | None = None
        if num_equals is not None:
            self.num_eq = list(num_equals) if isinstance(num_equals, list) else [num_equals]

        self.num_ne: list[int] | None = None
        if num_not_equals is not None:
            self.num_ne = list(num_not_equals) if isinstance(num_not_equals, list) else [num_not_equals]

        self.score_range: list[tuple[float, float]] | None = None
        if score_range is not None:
            if not score_range:
                Base.log(
                    "W",
                    "score_range为一个空列表，将会忽略此属性",
                    "AchievementTemplate.__init__",
                )
            else:
                if isinstance(score_range, tuple):
                    score_range = [score_range]
                self.score_range = list(score_range)

        self.score_rank_down_limit: int | None = None
        self.score_rank_up_limit: int | None = None
        if score_rank_range is not None:
            self.score_rank_down_limit = score_rank_range[0]
            self.score_rank_up_limit = score_rank_range[1]

        self.highest_score_down_limit: float | None = None
        self.highest_score_up_limit: float | None = None
        if highest_score_range is not None:
            self.highest_score_down_limit = highest_score_range[0]
            self.highest_score_up_limit = highest_score_range[1]

        self.lowest_score_down_limit: float | None = None
        self.lowest_score_up_limit: float | None = None
        if lowest_score_range is not None:
            self.lowest_score_down_limit = lowest_score_range[0]
            self.lowest_score_up_limit = lowest_score_range[1]

        self.highest_score_cause_range_down_limit: int | None = None
        self.highest_score_cause_range_up_limit: int | None = None
        if highest_score_cause_range is not None:
            self.highest_score_cause_range_down_limit = highest_score_cause_range[0]
            self.highest_score_cause_range_up_limit = highest_score_cause_range[1]

        self.lowest_score_cause_range_down_limit: int | None = None
        self.lowest_score_cause_range_up_limit: int | None = None
        if lowest_score_cause_range is not None:
            self.lowest_score_cause_range_down_limit = lowest_score_cause_range[0]
            self.lowest_score_cause_range_up_limit = lowest_score_cause_range[1]

        self.modify_ranges_orig: list[tuple[str, int | float, int | float]] | None = None
        self.modify_ranges: list[dict[str, str | int | float]] | None = None
        if modify_key_range is not None:
            if not len(modify_key_range):
                Base.log(
                    "W",
                    "score_range为一个空列表，将会忽略此属性",
                    "AchievementTemplate.__init__",
                )
            else:
                if isinstance(modify_key_range, tuple):
                    modify_key_range = [modify_key_range]

                self.modify_ranges_orig = modify_key_range
                self.modify_ranges = [
                    {"key": item[0], "lowest": item[1], "highest": item[2]} for item in self.modify_ranges_orig
                ]
        
        self.other: list[Callable[[ClassData], bool]] = []
        if others is not None:
            if not isinstance(others, list):
                self.other = [others]
            else:
                self.other = others
        
        self.when_triggered: list[Literal["any", "on_reset"]] = (
            when_triggered if isinstance(when_triggered, list) else [when_triggered]
        )
        self.sound = sound
        self.icon = icon
        self.further_info = further_info
        self.condition_info = condition_info
        self.archive_uuid = ClassDataLoader.get_archive_uuid()

    @property
    def kwargs(self):
        "等同于构造函数关键字参数的字典"
        kwargs: dict[str, Any] = {
            "key": self.key,
            "name": self.name,
            "desc": self.desc,
        }
        if self.name_eq is not None:
            kwargs["name_equals"] = self.name_eq
        if self.name_ne is not None:
            kwargs["name_not_equals"] = self.name_ne
        if self.num_eq is not None:
            kwargs["num_equals"] = self.num_eq
        if self.num_ne is not None:
            kwargs["num_not_equals"] = self.num_ne
        if self.score_range is not None:
            kwargs["score_range"] = self.score_range
        if self.score_rank_down_limit is not None:
            kwargs["score_rank_range"] = [
                self.score_rank_down_limit,
                self.score_rank_up_limit,
            ]
        if self.highest_score_down_limit is not None:
            kwargs["highest_score_range"] = [
                self.highest_score_down_limit,
                self.highest_score_up_limit,
            ]
        if self.lowest_score_down_limit is not None:
            kwargs["lowest_score_range"] = [
                self.lowest_score_down_limit,
                self.lowest_score_up_limit,
            ]
        if self.highest_score_cause_range_down_limit is not None:
            kwargs["highest_score_cause_range"] = [
                self.highest_score_cause_range_down_limit,
                self.highest_score_cause_range_up_limit,
            ]
        if self.lowest_score_cause_range_down_limit is not None:
            kwargs["lowest_score_cause_range"] = [
                self.lowest_score_cause_range_down_limit,
                self.lowest_score_cause_range_up_limit,
            ]
        if self.modify_ranges_orig is not None:
            kwargs["modify_key_range"] = self.modify_ranges_orig
        if self.other:
            kwargs["others"] = self.other
        kwargs["when_triggered"] = self.when_triggered
        if self.sound is not None:
            kwargs["sound"] = self.sound
        if self.icon is not None:
            kwargs["icon"] = self.icon
        kwargs["further_info"] = self.further_info
        kwargs["condition_info"] = self.condition_info
        return kwargs

    def achieved_by(self, student: Student, class_obs: ClassStatusObserver) -> bool:
        """
        判断一个成就是否达成

        :param student: 学生
        :param class_obs: 班级状态侦测器
        :raise ObserverError: lambda或者function爆炸了
        :return: 是否达成
        """
        from ..classdataset import ClassDataSet

        # 反人类写法又出现了

        assert class_obs is not None, "没有传入班级侦测器/班级侦测器还没有初始化完成"
        assert class_obs.dataset.achievement_obs is not None, "班级侦测器的成就侦测器还没有初始化完成"

        if not self.active:
            return False

        if ("on_reset" in self.when_triggered and "any" not in self.when_triggered) and (
            not student.highest_score == student.lowest_score == student.score == 0
        ):
            return False

        if self.name_ne is not None and student.name in self.name_ne:
            return False

        if self.num_ne is not None and student.num in self.num_ne:
            return False

        if self.name_eq is not None and student.name not in self.name_eq:
            return False

        if self.num_eq is not None and student.num not in self.num_eq:
            return False

        if self.score_range is not None and not any([i[0] <= student.score <= i[1] for i in self.score_range]):
            return False
        
        AccessErrorTypes = (
            KeyError,           # 索引不存在
            IndexError,         # 一样
            TypeError,          # 类型错误，可能出现在lambda里面
            AttributeError,     # 可能出现在（老版本序列化方案）数据还没加载完的时候
            RuntimeError        # 迭代时可迭代对象的大小改变了
        )

        try:
            if self.score_rank_down_limit is not None and self.score_rank_up_limit is not None:
                lowest_rank = max(*([i[0] for i in class_obs.rank_dumplicate]))
                l = (
                    (lowest_rank + self.score_rank_down_limit + 1)
                    if self.score_rank_down_limit < 0
                    else self.score_rank_down_limit
                )
                r = (
                    (lowest_rank + self.score_rank_up_limit + 1)
                    if self.score_rank_up_limit < 0
                    else self.score_rank_up_limit
                )
                if not (l <= next(i[0] for i in class_obs.rank_dumplicate if i[1].num == student.num) <= r):
                    return False
        except AccessErrorTypes:
            return False

        if self.highest_score_down_limit is not None and self.highest_score_up_limit is not None and (
            not self.highest_score_down_limit <= student.highest_score <= self.highest_score_up_limit
        ):
            return False

        if self.highest_score_cause_range_down_limit is not None and self.highest_score_cause_range_up_limit is not None and (
            (not student.highest_score_cause_time)
            or (
                not self.highest_score_cause_range_down_limit
                <= student.highest_score_cause_time
                <= self.highest_score_cause_range_up_limit
            )
        ):
            return False

        if self.lowest_score_down_limit is not None and self.lowest_score_up_limit is not None and (
            not self.lowest_score_down_limit <= student.lowest_score <= self.lowest_score_up_limit
        ):
            return False

        if self.lowest_score_cause_range_down_limit is not None and self.lowest_score_cause_range_up_limit is not None and (
            (not student.lowest_score_cause_time)
            or (
                not self.lowest_score_cause_range_down_limit
                <= student.lowest_score_cause_time
                <= self.lowest_score_cause_range_up_limit
            )
        ):
            return False
        try:
            if self.modify_ranges is not None and not all(
                [
                    item["lowest"]
                    <= [history.temp.key for history in student.history.values() if history.executed].count(item["key"])  # type: ignore
                    <= item["highest"]
                    for item in self.modify_ranges
                ]
            ):
                return False
        except AccessErrorTypes:
            return False

        if self.other:
            try:
                d = ClassData(
                    student=student,
                    classes=class_obs.classes,
                    class_obs=class_obs,
                    achievement_obs=class_obs.dataset.achievement_obs,
                )
                for item in self.other:
                    if not item(d):
                        return False

            except AccessErrorTypes as e:
                if isinstance(e, ClassDataSet.OperationalError):
                    return False

                error_id = f"noticed_achievement_lambda_error_{self.uuid}"

                if error_id in runtime_flags: # 提示一次就够了
                    return False
                
                runtime_flags[error_id] = True
                if e.args:
                    if e.args[0] == "name 'student' is not defined":
                        Base.log(
                            "W",
                            "未加载完成，未定义student",
                            "AchievementTemplate.achieved",
                        )
                    elif e.args[0] == "unknown opcode":
                        Base.log(
                            "W",
                            "存档的成就来自不同的版本",
                            "AchievementTemplate.achieved",
                        )
                
                        if "noticed_pyversion_changed" not in runtime_flags:
                            Base.log(
                                "W",
                                "当前很可能在跨Python版本运行，这大概率是问题出现的根本原因（序列化问题），"
                                "请尽量不要切换py版本，或者自己试着修一下lambda的序列化",
                                "AchievementTemplate.achieved_by",
                            )
                            runtime_flags["noticed_pyversion_changed"] = True

                Base.log_exc(
                    f"位于成就{self.name}({self.key})的lambda函数出错：",
                    "AchievementTemplate.achieved",
                )
                Base.log("W", "将不会再次展示此提示，请检查数据完整性（当然，也可能是正常现象）")

                if self.key in class_obs.dataset.default_achievements:
                    if isinstance(self.other, list): # type: ignore
                        if not isinstance(self.other[0], Callable): # type: ignore
                            # 还没加载，先跳过
                            return False
                        # 还没加载，先跳过
                    elif isinstance(self.other, str): # type: ignore
                        return False
                    self.other = class_obs.dataset.default_achievements[self.key].other
                    Base.log("I", "已经重置为默认值", "AchievementTemplate.achieved")
                else:
                    raise ClassDataLoader.ObserverError(f"位于成就{self.name}({self.key})的lambda函数出错")
                return False
        return True

    achieved = achieved_by
    got = achieved_by

    def condition_desc(self, class_obs: ClassStatusObserver):
        """
        条件描述。

        :param class_obs: 班级状态侦测器

        :return: 一个字符串"""
        return_str = ""
        if self.name_eq is not None:
            return_str += "仅适用于" + "，".join(self.name_eq) + "\n"

        if self.num_eq is not None:
            return_str += "仅适用于学号为" + "，".join([str(n) for n in self.num_eq]) + "的学生\n"

        if self.name_ne is not None:
            return_str += "不适用于" + "，".join(self.name_ne) + "\n"

        if self.num_ne is not None:
            return_str += "不适用于学号为" + "，".join([str(n) for n in self.num_ne]) + "的学生\n"

        if self.score_range is not None:
            first = True
            for item in self.score_range:
                if not first:
                    return_str += "或者"
                first = False
                down = item[0]
                up = item[1]
                if -(2**63) < down < up < 2**63:
                    return_str += f"达成时分数介于{down:.1f}和{up:.1f}之间\n"
                elif up == down:
                    return_str += f"达成时分数为{down:.1f}\n"
                elif up > 2**63:
                    return_str += f"达成时分数高于{down:.1f}\n"
                elif down < -(2**63):
                    return_str += f"达成时分数低于{up:.1f}\n"

                else:
                    return_str += "分数为0\n"

        if self.score_rank_down_limit is not None:
            if self.score_rank_down_limit == self.score_rank_up_limit:
                return_str += (
                    f"位于班上{('倒数' if self.score_rank_down_limit < 0 else '')}"
                    + "第"
                    + str(abs(self.score_rank_down_limit))
                    + "名\n"
                )
            else:
                return_str += (
                    f"排名介于{('倒数' if self.score_rank_down_limit < 0 else '')}"
                    + "第"
                    + f"{abs(self.score_rank_down_limit)}"
                    + "和"  # pylint: disable=E1130
                    + ("倒数" if self.score_rank_up_limit is not None and self.score_rank_up_limit < 0 else "")
                    + "第"
                    + f"{abs(self.score_rank_up_limit) if self.score_rank_up_limit is not None else 0}"
                    + "之间\n"
                )  # pylint: disable=E1130

        if self.highest_score_down_limit is not None and self.highest_score_up_limit is not None:
            down = self.highest_score_down_limit
            up = self.highest_score_up_limit
            if -(2**63) < down < up < 2**63:
                return_str += f"历史最高分数介于{down:.1f}和{up:.1f}之间\n"
            elif up == down:
                return_str += f"历史最高分数为{down:.1f}\n"
            elif up > 2**63:
                return_str += f"历史最高分数高于{down:.1f}\n"
            elif down < -(2**63):
                return_str += f"历史最高分数低于{up:.1f}\n"
            else:
                return_str += "没看懂，反正对历史最高分有要求（写的抽象了没法判断）\n"

        if self.lowest_score_down_limit is not None and self.lowest_score_up_limit is not None:
            down = self.lowest_score_down_limit
            up = self.lowest_score_up_limit
            if -(2**63) < down < up < 2**63:
                return_str += f"历史最低分数介于{down:.1f}和{up:.1f}之间\n"
            elif up == down:
                return_str += f"历史最低分数为{down:.1f}\n"
            elif up > 2**63:
                return_str += f"历史最低分数高于{down:.1f}\n"
            elif down < -(2**63):
                return_str += f"历史最低分数低于{up:.1f}\n"
            else:
                return_str += "没看懂，反正对历史最低分有要求（写的抽象了没法判断）\n"

        if self.modify_ranges is not None:
            for item in self.modify_ranges:
                lowest: int | float = item["lowest"]  # type: ignore
                highest: int | float = item["highest"]  # type: ignore
                key: str = item["key"]  # type: ignore
                return_str += (
                    f'达成{lowest}到{highest}次"{class_obs.templates[key].title}"\n'
                    if lowest not in (highest, inf) and highest != inf
                    else (
                        f'达成{lowest}次"{class_obs.templates[key].title}"\n'
                        if lowest == highest != inf
                        else (
                            f'达成大于等于{lowest}次"{class_obs.templates[key].title}"\n'
                            if highest == inf
                            else ("这写的什么抽象表达式，我看不懂\n")
                        )
                    )
                )

        if self.other:
            return_str += "有一些其他条件，如果没写就自己摸索吧\n"

        if return_str == "":
            return_str = "(无条件)"
        return_str += "\n" * 2 + self.condition_info
        return return_str

    def to_string(self) -> StringObjectDataKind[Self]:
        "从字符串加载成就模板对象。"
        obj = {"type": self.chunk_type_name}
        obj.update(self.kwargs)
        if "others" in obj:
            obj["others"] = base64.b64encode(
                pickle.dumps(obj["others"], protocol=pickle.HIGHEST_PROTOCOL)  # pyright: ignore[reportUnknownMemberType]
            ).decode()
        obj["uuid"] = str(self.uuid)
        obj["archive_uuid"] = str(self.archive_uuid)
        return StringObjectDataKind(json.dumps(obj))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "从字符串加载成就模板对象。"
        d: dict[str, Any] = json.loads(string)
        if d["type"] != cls.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {cls.chunk_type_name}")
        try:
            if "others" in d:
                d["others"] = pickle.loads(base64.b64decode(d["others"]))  # pyright: ignore[reportUnknownMemberType]
        except SystemError as e:
            if e.args[0] == "unknown opcode":
                Base.log(
                    "E",
                    "由于版本变化，无法加载lambda，请手动修改",
                    "AchievementTemplate.from_string",
                )
                d.pop("others")
            else:
                raise
        d.pop("type")
        uuid = d.pop("uuid")
        archive_uuid = d.pop("archive_uuid")
        obj = cls(**d)
        obj.uuid = uuid
        obj.archive_uuid = archive_uuid
        obj.active = True
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
        from ..pydantic_loader.models.achievement_template import AchievementTemplateModel
        return AchievementTemplateModel.from_class_data(self)
