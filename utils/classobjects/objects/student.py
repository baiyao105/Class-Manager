from __future__ import annotations

import copy
import json
import time
from typing import TYPE_CHECKING, Any, Self, override

from ...algorithm import SupportsKeyOrdering, update_object_mapping
from ...basetypes import Base
from .datatag import TagSigned, DataTag
from ..basetype import ClassDataType, ClassDataTypeUUID, DataProperty, StringObjectDataKind
from ..classdataloader import ClassDataLoader

if TYPE_CHECKING:
    from ..observers.classstatobs import ClassStatusObserver
    from .achievement import Achievement
    from .group import Group
    from .scoremod import ScoreModification


class Student(ClassDataType, SupportsKeyOrdering, TagSigned):
    "一个学牲"

    chunk_type_name: str = "Student"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    score_dtype = float
    "记录分数的数据类型（还没做完别乱改）"

    last_reset_info_keep_turns = 2
    "在存档中上次重置信息的轮数"

    class NoBelongningClassError(ClassDataType.DataTypeError):
        "学生没有所属班级。"

    class NoBelongningGroupError(ClassDataType.DataTypeError):
        "学生没有所属小组。"

    class UnsupportedOperationError(ClassDataType.DataTypeError):
        "操作不支持。"
    
    class ObserverMismatchError(ClassDataType.DataTypeError):
        "侦测器和学生的班级不匹配。"

    class CannotFindStudentInClassError(ClassDataType.DataTypeError):
        "在侦测器的班级里找不到这个学生。"

    @classmethod
    def new_dummy(cls) -> Self:
        "返回一个空学生"
        return cls("dummy", 0, 0.0, "dummy")

    def __init__(
        self,
        name: str,
        num: int,
        score: float,
        belongs_to: str,
        history: dict[Any, ScoreModification] | None = None,
        last_reset: float | None = None,
        highest_score: float | None = None,
        lowest_score: float | None = None,
        achievements: dict[int, Achievement] | None = None,
        total_score: float | None = None,
        highest_score_cause_time: float | None = None,
        lowest_score_cause_time: float | None = None,
        belongs_to_group: str | None = None,
        last_reset_info: Student | None = None,
        tags: list[DataTag] | None = None,
    ):
        """
        一个学生。

        :param name: 姓名
        :param num: 学号
        :param score: 当前分数
        :param belongs_to: 所属班级
        :param history: 历史记录
        :param last_reset: 上次重置时间
        :param highest_score: 最高分
        :param lowest_score: 最低分
        :param achievements: 成就
        :param total_score: 总分
        :param highest_score_cause_time: 最高分产生时间
        :param lowest_score_cause_time: 最低分产生时间
        :param belongs_to_group: 所属小组对应key
        :param last_reset_info: 上次重置的信息
        :param tags: 携带的标签
        """
        super().__init__()
        self._name = name
        # 带下划线的属性为内部存储用，实际访问应使用property
        self._num = num
        self._score = score
        self._belongs_to: str = belongs_to
        self._highest_score: float = highest_score or 0.0
        self._lowest_score: float = lowest_score or 0.0
        self._total_score: float = total_score or score
        self._last_reset = last_reset
        "分数上次重置的时间"
        self._highest_score_cause_time = highest_score_cause_time
        self._lowest_score_cause_time = lowest_score_cause_time
        self.history: dict[int, ScoreModification] = history or {}
        "历史记录， key为时间戳（utc*1000）"
        self.achievements: dict[int, Achievement] = achievements or {}
        "所获得的所有成就， key为时间戳（utc*1000）"
        self.belongs_to_group = belongs_to_group
        "所属小组"
        self._last_reset_info = last_reset_info
        "上次重置的信息"
        self.archive_uuid = ClassDataLoader.get_archive_uuid()
        "归档uuid"
        self.tags: list[DataTag] = tags or []
        "标签"

    @DataProperty
    def last_reset(self) -> float | None:
        "上次重置的时间"
        return self._last_reset

    @last_reset.setter
    def last_reset(self, value: float | None) -> None:
        self._last_reset = value

    @DataProperty
    def last_reset_info(self) -> Student:
        "上次重置的信息"
        return self._last_reset_info if self._last_reset_info is not None else self.new_dummy()

    @last_reset_info.setter
    def last_reset_info(self, value: Student | None):
        self._last_reset_info = value

    @DataProperty
    def highest_score(self):
        "最高分"
        return float(self._highest_score)

    @highest_score.setter
    def highest_score(self, value: score_dtype | float):
        self._highest_score = self.score_dtype(value)

    @DataProperty
    def lowest_score(self):
        "最低分"
        return float(self._lowest_score)

    @lowest_score.setter
    def lowest_score(self, value: score_dtype | float):
        self._lowest_score = self.score_dtype(value)

    @DataProperty
    def highest_score_cause_time(self):
        "最高分对应时间"
        return self._highest_score_cause_time

    @highest_score_cause_time.setter
    def highest_score_cause_time(self, value: float):
        self._highest_score_cause_time = value

    @DataProperty
    def lowest_score_cause_time(self):
        "最低分对应时间"
        return self._lowest_score_cause_time

    @lowest_score_cause_time.setter
    def lowest_score_cause_time(self, value: float):
        self._lowest_score_cause_time = value

    def __repr__(self):
        return (
            f"Student(name={self._name.__repr__()}, "
            + f"num={self._num.__repr__()}, score={self._score.__repr__()}, "
            + f"belongs_to={self._belongs_to.__repr__()}, "
            + ("history={...}, " if hasattr(self, "history") else "")
            + f"last_reset={self.last_reset!r}, "
            + f"highest_score={self.highest_score!r}, "
            + f"lowest_score={self.highest_score!r}, "
            + f"total_score={self.highest_score!r}, "
            + ("achievements={...}, " if hasattr(self, "achievements") else "")
            + f"highest_score_cause_time = {self.highest_score_cause_time!r}, "
            + f"lowest_score_cause_time = {self.lowest_score_cause_time!r}, "
            + f"belongs_to_group={self.belongs_to_group!r})"
        )

    @DataProperty
    def name(self):
        "学生的名字。"
        return self._name

    @name.setter
    def name(self, val: str):
        self._name = val

    @name.deleter
    def name(self):
        Base.log("E", "错误：用户尝试删除学生名", "Student.num.deleter")
        raise Student.UnsupportedOperationError("不允许删除学生的名字")

    @DataProperty
    def num(self) -> int:
        "学生的学号。"
        return self._num

    @num.setter
    def num(self, val: int):
        Base.log(
            "W",
            f"正在尝试更改学号为{self._name}的学生的学号：由{self._num}更改为{val}",
            "Student.num.setter",
        )
        self._num = val
        Base.log("D", "更改完成！", "Student.name.setter")

    @num.deleter
    def num(self):
        Base.log("E", "错误：用户尝试删除学号（？？？？）", "Student.name.deleter")
        raise Student.UnsupportedOperationError("不允许删除学生的学号")

    @DataProperty
    def score(self):
        "学生的分数，操作时仅保留1位小数。"
        return float(self._score)

    @score.setter
    def score(self, val: float):
        self.total_score += val - self.score
        self._score = self.score_dtype(round(val, 1))
        self.highest_score = max(self.highest_score, self.score)
        self.lowest_score = min(self.lowest_score, self.score)

    @score.deleter
    def score(self):
        Base.log("E", "错误：用户尝试删除分数（？？？？）", "Student.score.deleter")
        raise Student.UnsupportedOperationError("不允许直接删除学生的分数")

    @DataProperty
    def belongs_to(self):
        "学生归属班级。"
        return self._belongs_to

    @belongs_to.setter
    def belongs_to(self, _):
        Base.log("E", "错误：用户尝试修改班级", "Student.belongs_to.setter")
        raise Student.UnsupportedOperationError("不允许直接修改学生的班级")

    @belongs_to.deleter
    def belongs_to(self):
        Base.log(
            "E",
            "错误：用户尝试删除班级（？？？？？？？）",
            "Student.belongs_to.deleter",
        )
        raise Student.UnsupportedOperationError("不允许直接删除学生的班级")

    @DataProperty
    def total_score(self):
        "学生总分数。"
        return (
            round(self._total_score, 1) if isinstance(self._total_score, float) else round(float(self._total_score), 1)
        )

    @total_score.setter
    def total_score(self, value: float):
        self._total_score = self.score_dtype(value)

    def reset_score(
        self,
    ) -> tuple[float, float, float, dict[int, ScoreModification]]:
        """重置学生分数。

        :return: Tuple[当前分数, 历史最高分, 历史最低分,
        Dict[分数变动时间utc*1000, 分数变动记录], Dict[成就达成时间utc*1000, 成就]"""
        Base.log("W", f"  -> 重置{self.name} ({self.num})的分数")

        returnval = (
            float(self.score),
            float(self.highest_score),
            float(self.lowest_score),
            dict(self.history),
        )
        self.score = 0.0
        self.highest_score = 0.0
        self.lowest_score = 0.0
        self.highest_score_cause_time = 0.0
        self.lowest_score_cause_time = 0.0
        self.last_reset = time.time()
        self.history = dict()
        self.achievements = dict()
        return returnval

    def reset_achievements(self) -> dict[int, Achievement]:
        """重置学生成就。

        :return: Dict[成就达成时间utc*1000, 成就]"""
        Base.log("W", f"  -> 重置{self.name} ({self.num})的成就")
        returnval = dict(self.achievements)
        self.achievements = dict()
        return returnval

    def reset(
        self, reset_achievments: bool = True
    ) -> tuple[
        float,
        float,
        float,
        dict[int, ScoreModification],
        dict[int, Achievement] | None,
    ]:
        """
        重置学生分数和成就。
        这个操作会更新学生的last_reset_info属性，以记录重置前的分数和成就。

        :param reset_achievments: 是否重置成就
        :return: Tuple[当前分数, 历史最高分, 历史最低分,
        Dict[分数变动时间utc*1000, 分数变动记录], Dict[成就达成时间utc*1000, 成就]
        """
        self.last_reset_info = copy.deepcopy(self)
        score, highest, lowest, history = self.reset_score()
        achievements = None
        if reset_achievments:
            achievements = self.reset_achievements()
        self.refresh_uuid()
        return (score, highest, lowest, history, achievements)

    def get_group(self, class_obs: ClassStatusObserver) -> Group:
        """
        获取学生所在小组。

        :param class_obs: 班级侦测器
        :return: Group对象
        """
        if not self._belongs_to:
            raise Student.NoBelongningClassError(f"尝试访问没有所属班级的学生{self!r}所在的小组")

        if not self.belongs_to_group:
            raise Student.NoBelongningGroupError(f"尝试访问没有所属小组的学生{self!r}所在的小组")

        if self._belongs_to != class_obs.class_id:
            raise Student.ObserverMismatchError(
                f"但是从理论层面来讲你不应该把{class_obs.class_id!r}的侦测器给一个{self._belongs_to!r}的学生"
            )

        return class_obs.classes[self._belongs_to].groups[self.belongs_to_group]

    def get_dumplicated_ranking(self, class_obs: ClassStatusObserver) -> int:
        """
        获取学生在班级中计算重复名次的排名。

        :param class_obs: 班级侦测器
        :return: 排名
        """
        if self._belongs_to != class_obs.class_id:
            raise Student.ObserverMismatchError(
                f"但是从理论层面来讲你不应该把{class_obs.class_id!r}的侦测器给一个{self._belongs_to!r}的学生"
            )

        ranking_data: list[tuple[int, Student]] = class_obs.rank_non_dumplicate
        for index, student in ranking_data:
            if student.num == self.num:
                return index
        raise Student.CannotFindStudentInClassError(f"这个学生({self.num})貌似在这个班({class_obs.class_id})找不到")

    def get_non_dumplicated_ranking(self, class_obs: ClassStatusObserver) -> int:
        """
        获取学生在班级中计算非重复名次的排名。

        :param class_obs: 班级侦测器
        :return: 排名
        """
        if self._belongs_to != class_obs.class_id:
            raise Student.ObserverMismatchError(
                f"但是从理论层面来讲你不应该把{class_obs.class_id!r}的侦测器给一个{self._belongs_to!r}的学生"
            )

        ranking_data: list[tuple[int, Student]] = class_obs.rank_non_dumplicate
        for index, student in ranking_data:
            if student.num == self.num:
                return index
        raise Student.CannotFindStudentInClassError(f"这个学生({self.num})貌似在这个班({class_obs.class_id})找不到")

    def __add__(self, value: Student | float) -> Student:
        "这种东西做出来是致敬班级小管家的（bushi"
        if isinstance(value, Student):
            history = self.history.copy()
            history.update(value.history)
            achievements = self.achievements.copy()
            achievements.update(value.achievements)
            Base.log(
                "W",
                f"  -> 合并学生：({self.name}, {value.name})",
                "Student.__add__",
            )
            Base.log("W", "孩子，这不好笑", "Student.__add__")
            return Student(
                "合并学生："
                f"({self.name.replace('合并学生：(', '').replace(')', '')}, "
                f"{value.name.replace('合并学生：(', '').replace(')', '')})",
                num=self.num + value.num,
                score=self.score + value.score,
                belongs_to=self.belongs_to,
                history=history,
                last_reset=self.last_reset,
                achievements=achievements,
                highest_score=self.highest_score + value.highest_score,
                lowest_score=self.lowest_score + value.lowest_score,
                highest_score_cause_time=(self.highest_score_cause_time or 0) + (value.highest_score_cause_time or 0),
                lowest_score_cause_time=self.lowest_score_cause_time,
                belongs_to_group=self.belongs_to_group,
                total_score=self.total_score + value.total_score,
            ).copy()

        self.score += value
        return self

    def __iadd__(self, value: Student | float) -> Student:
        if isinstance(value, Student):
            self.achievements.update(value.achievements)
            self.history.update(value.history)
            self.score += value.score
            self.total_score += value.total_score
            return self
        self.score += value
        self.total_score += value
        return self

    def dump_history(self) -> list[tuple[int, str]]:
        "将学生的历史记录转换为字符串映射。"
        return [(h.execute_time_key, str(h.uuid)) for h in self.history.values() if h.executed]

    @staticmethod
    def load_history(d: dict[str, Any]) -> dict[int, ScoreModification]:
        "从数据字典加载学生的历史记录。"
        from .scoremod import ScoreModification
        result: dict[int, ScoreModification] = {}
        for k, v in d["history"]:
            k: int
            v: ClassDataTypeUUID[ScoreModification]
            item = ClassDataLoader.LoadUUID(v, ScoreModification)
            assert item is not None, f"目标的历史记录{k}加载失败"
            result[k] = item
        return result

    def dump_achievements(self) -> list[tuple[int, str]]:
        "将学生的成就记录转换为字符串映射。"
        return [(a.time_key, str(a.uuid)) for a in self.achievements.values()]

    @staticmethod
    def load_achievements(d: dict[str, Any]) -> dict[int, Achievement]:
        "从数据字典加载学生的成就记录。"
        from .achievement import Achievement
        result: dict[int, Achievement] = {}
        for k, v in d["achievements"]:
            k: int
            v: ClassDataTypeUUID[Achievement]
            item = ClassDataLoader.LoadUUID(v, Achievement)
            assert item is not None, f"目标的成就记录{k}加载失败"
            result[k] = item
        return result

    def dump_last_reset_info(self) -> str | None:
        "将学生的上次重置信息转换为字符串。"
        return str(self.last_reset_info.uuid) if self._last_reset_info else None
    
    @staticmethod
    def load_last_reset_info(d: dict[str, Any]) -> Student | None:
        "从数据字典加载学生的上次重置信息。"
        from .student import Student
        if "last_reset_info" in d and d["last_reset_info"] is not None:
            return ClassDataLoader.LoadUUID(d["last_reset_info"], Student) 
        return None

    def dump_tags(self) -> list[str]:
        "将学生的标签转换为字符串列表。"
        return [str(t.uuid) for t in self.tags]

    @staticmethod
    def load_tags(d: dict[str, Any]) -> list[DataTag]:
        "从数据字典加载学生的标签。"
        from .datatag import DataTag
        result: list[DataTag] = []
        for t in d["tags"]:
            t: ClassDataTypeUUID[DataTag]
            item = ClassDataLoader.LoadUUID(t, DataTag)
            assert item is not None, f"目标标签{t}加载失败"
            result.append(item)
        return result


    def to_string(self) -> StringObjectDataKind[Self]:
        "将学生对象转换为JSON格式"
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "name": self.name,
                "num": self.num,
                "score": float(self.score),
                "belongs_to": self.belongs_to,
                "history": self.dump_history(),
                "last_reset": self.last_reset,
                "achievements": self.dump_achievements(),
                "highest_score": self.highest_score,
                "lowest_score": self.lowest_score,
                "highest_score_cause_time": self.highest_score_cause_time,
                "lowest_score_cause_time": self.lowest_score_cause_time,
                "belongs_to_group": self.belongs_to_group,
                "total_score": self.total_score,
                "last_reset_info": self.dump_last_reset_info(),
                "tags": self.dump_tags(),
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "将字符串转换为学生对象。"

        data = json.loads(string)
        if data["type"] != cls.chunk_type_name:
            raise TypeError(f"类型不匹配：{data['type']} != {cls.chunk_type_name}")
        obj = cls(
            name=data["name"],
            num=data["num"],
            score=cls.score_dtype(data["score"]),
            belongs_to=data["belongs_to"],
            history=cls.load_history(data),
            last_reset=data["last_reset"],
            highest_score=data["highest_score"],
            lowest_score=data["lowest_score"],
            achievements=cls.load_achievements(data),
            total_score=data["total_score"],
            highest_score_cause_time=data["highest_score_cause_time"],
            lowest_score_cause_time=data["lowest_score_cause_time"],
            belongs_to_group=data["belongs_to_group"],
            last_reset_info=cls.load_last_reset_info(data),
            tags=cls.load_tags(data)
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
        from ..pydantic_loader.models.student import StudentModel
        return StudentModel.from_class_data(self)
