from __future__ import annotations

import copy
import json
import time
from typing import TYPE_CHECKING, Any, Literal

from ...algorithm import SupportsKeyOrdering
from ...basetypes import Base
from .datatag import TagSigned, DataTag
from ..basetype import ClassDataType, DataProperty
from ..classdataobj import ClassDataObj

if TYPE_CHECKING:
    from ..observers.classstatobs import ClassStatusObserver
    from .achievement import Achievement
    from .group import Group
    from .scoremod import ScoreModification


class Student(ClassDataType, SupportsKeyOrdering, TagSigned):
    "一个学牲"

    chunk_type_name: Literal["Student"] = "Student"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    score_dtype = float
    "记录分数的数据类型（还没做完别乱改）"

    last_reset_info_keep_turns = 2
    "在存档中上次重置信息的轮数"

    class NoBelongningClass(Exception):
        "学生没有所属班级。"

    class NoBelongningGroup(Exception):
        "学生没有所属小组。"

    @staticmethod
    def new_dummy():
        "返回一个空学生"
        return Student("dummy", 0, 0.0, "dummy")

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
        self.archive_uuid = ClassDataObj.get_archive_uuid()
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
        raise ClassDataObj.OpreationError("不允许删除学生的名字")

    @DataProperty
    def num(self):
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
        raise ClassDataObj.OpreationError("不允许删除学生的学号")

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
        raise ClassDataObj.OpreationError("不允许直接删除学生的分数")

    @DataProperty
    def belongs_to(self):
        "学生归属班级。"
        return self._belongs_to

    @belongs_to.setter
    def belongs_to(self, _):
        Base.log("E", "错误：用户尝试修改班级", "Student.belongs_to.setter")
        raise ClassDataObj.OpreationError("不允许直接修改学生的班级")

    @belongs_to.deleter
    def belongs_to(self):
        Base.log(
            "E",
            "错误：用户尝试删除班级（？？？？？？？）",
            "Student.belongs_to.deleter",
        )
        raise ClassDataObj.OpreationError("不允许直接删除学生的班级")

    @DataProperty
    def total_score(self):
        "学生总分数。"
        return (
            round(self._total_score, 1) if isinstance(self._total_score, float) else round(float(self._total_score), 1)
        )

    @total_score.setter
    def total_score(self, value):
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
            raise Student.NoBelongningClass(f"尝试访问没有所属班级的学生{self!r}所在的小组")

        if not self.belongs_to_group:
            raise Student.NoBelongningGroup(f"尝试访问没有所属小组的学生{self!r}所在的小组")

        if self._belongs_to != class_obs.class_id:
            raise ClassDataObj.ObserverError(
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
            raise ValueError(
                f"但是从理论层面来讲你不应该把{class_obs.class_id!r}的侦测器给一个{self._belongs_to!r}的学生"
            )

        ranking_data: list[tuple[int, Student]] = class_obs.rank_non_dumplicate
        for index, student in ranking_data:
            if student.num == self.num:
                return index
        raise ValueError(f"你确定这个学生({self.belongs_to})在这个班({class_obs.class_id})？")

    def get_non_dumplicated_ranking(self, class_obs: ClassStatusObserver) -> int:
        """
        获取学生在班级中计算非重复名次的排名。

        :param class_obs: 班级侦测器
        :return: 排名
        """
        if self._belongs_to != class_obs.class_id:
            raise ValueError(
                f"但是从理论层面来讲你不应该把{class_obs.class_id!r}的侦测器给一个{self._belongs_to!r}的学生"
            )

        ranking_data: list[tuple[int, Student]] = class_obs.rank_non_dumplicate
        for index, student in ranking_data:
            if student.num == self.num:
                return index
        raise ValueError(f"你确定这个学生({self.belongs_to})在这个班({class_obs.class_id})？")

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

    def to_string(self) -> str:
        "将学生对象转换为JSON格式"
        return json.dumps(
            {
                "type": self.chunk_type_name,
                "name": self.name,
                "num": self.num,
                "score": float(self.score),
                "belongs_to": self.belongs_to,
                "history": [(h.execute_time_key, str(h.uuid)) for h in self.history.values() if h.executed],
                "last_reset": self.last_reset,
                "achievements": [(a.time_key, str(a.uuid)) for a in self.achievements.values()],
                "highest_score": self.highest_score,
                "lowest_score": self.lowest_score,
                "highest_score_cause_time": self.highest_score_cause_time,
                "lowest_score_cause_time": self.lowest_score_cause_time,
                "belongs_to_group": self.belongs_to_group,
                "total_score": self.total_score,
                "last_reset_info": (str(self.last_reset_info.uuid) if self._last_reset_info else None),
                "tags": [str(t.uuid) for t in self.tags],
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        )

    @staticmethod
    def from_string(string: str) -> Student:
        "将字符串转换为学生对象。"
        from .achievement import Achievement
        from .scoremod import ScoreModification

        data = json.loads(string)
        if data["type"] != Student.chunk_type_name:
            raise TypeError(f"类型不匹配：{data['type']} != {Student.chunk_type_name}")
        obj = Student(
            name=data["name"],
            num=data["num"],
            score=Student.score_dtype(data["score"]),
            belongs_to=data["belongs_to"],
            history={k: ClassDataObj.LoadUUID(v, ScoreModification) for k, v in data["history"]},
            last_reset=data["last_reset"],
            highest_score=data["highest_score"],
            lowest_score=data["lowest_score"],
            achievements={k: ClassDataObj.LoadUUID(v, Achievement) for k, v in data["achievements"]},
            total_score=data["total_score"],
            highest_score_cause_time=data["highest_score_cause_time"],
            lowest_score_cause_time=data["lowest_score_cause_time"],
            belongs_to_group=data["belongs_to_group"],
            last_reset_info=ClassDataObj.LoadUUID(data["last_reset_info"], Student),
            tags=[ClassDataObj.LoadUUID(t, DataTag) for t in data["tags"]],
        )

        obj.uuid = data["uuid"]
        obj.archive_uuid = data["archive_uuid"]
        return obj

    def inst_from_string(self, string: str):
        "将字符串加载与本身。"
        obj = self.from_string(string)
        self.__dict__.update(obj.__dict__)
        return self
