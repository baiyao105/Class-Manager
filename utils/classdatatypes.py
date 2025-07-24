"""
班级数据类型
"""

import base64
import copy
import time
import json
import traceback
from queue import Queue
from typing import (
    Union,
    TypeVar,
    Generic,
    Optional,
    Dict,
    Any,
    Callable,
    Type,
    Literal,
    Tuple,
    List,
    overload,
    Iterable,
)


import pickle  # pylint: disable=unused-import
import dill as pickle  # pylint: disable=shadowed-import


from utils.basetypes import Base, Object
from utils.consts import inf, debug, runtime_flags
from utils.algorithm import SupportsKeyOrdering, OrderedKeyList, Stack
from utils.functions.prompts import send_notice as _send_notice
from utils.functions.numbers import utc
from utils.events.event import EventSignal, EventType


def send_notice(
    title: str, content: str, msg_type: Literal["info", "warn", "error"] = "info"
):
    "发送通知"
    Base.log("I", f"发送通知, title={title!r}, content={content!r}")
    _send_notice(title, content, msg_type)


ClassDataType = Union[
    "Student",
    "Class",
    "Group",
    "AttendanceInfo",
    "ScoreModification",
    "ScoreModificationTemplate",
    "Achievement",
    "AchievementTemplate",
    "DayRecord",
]


_UT = TypeVar("_UT")




class DataProperty(property):
    "数据属性，用于ClassDataType的属性"

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        super().__init__(fget, fset, fdel, doc)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return super().__get__(instance, owner)

    def __set__(self, instance, value):
        if instance is None:
            return
        ClassDataObj.has_unsaved_changes = True
        ClassDataObj.has_unprocessed_data = True
        return super().__set__(instance, value)

    def __delete__(self, instance):
        if instance is None:
            return
        return super().__delete__(instance)
    


class UUIDKind(Generic[_UT], str):
    "uuid类型, UUIDKind[Student]代表这个uuid可以加载出一个学牲"

    def __init__(self, uuid: str, data_type: ClassDataType):
        self.uuid = uuid
        self.type_name = data_type.chunk_type_name

    def __hash__(self):
        return hash(self.uuid)

    def __eq__(self, other):
        return isinstance(other, UUIDKind) and self.uuid == other.uuid

    def __repr__(self):
        return f"UUIDKind({self.uuid})"

    def __str__(self):
        return self.uuid


class ClassDataObj(Base):
    "班级数据对象"

    archive_uuid: Optional[str] = None
    "归档uuid，每重置一次存档就换新的"

    has_unsaved_changes = False
    "是否有未保存的更改"

    has_unprocessed_data = False
    "是否有未处理的数据"

    class OpreationError(Exception):
        "修改出现错误。"

    LoadUUID: Callable[
        [UUIDKind[ClassDataType], Type[ClassDataType], Optional[UUIDKind["History"]]],
        ClassDataType,
    ]
    "加载uuid的函数，传入一个uuid和数据类型，返回一个ClassDataType，在utils.dataloader里面实现"

    # Tip:如果需要在类型标注中使用尚未定义的类，可以用引号括起来
    class Student(Object, SupportsKeyOrdering):
        "一个学牲"

        chunk_type_name: Literal["Student"] = "Student"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        score_dtype = float
        "记录分数的数据类型（还没做完别乱改）"

        last_reset_info_keep_turns = 2
        "在存档中上次重置信息的轮数"

        dummy: "Student" = None
        "空学生"

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
            history: Dict[Any, "ScoreModification"] = None,
            last_reset: Optional[float] = None,
            highest_score: float = 0.0,
            lowest_score: float = 0.0,
            achievements: Dict[int, "Achievement"] = None,
            total_score: float = None,
            highest_score_cause_time: float = 0.0,
            lowest_score_cause_time: float = 0.0,
            belongs_to_group: Optional[str] = None,
            last_reset_info: Optional["Student"] = None,
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
            """
            super().__init__()
            self._name = name
            # 带下划线的属性为内部存储用，实际访问应使用property
            self._num = num
            self._score = score
            self._belongs_to: str = belongs_to
            self._highest_score: float = highest_score
            self._lowest_score: float = lowest_score
            self._total_score: float = total_score or score
            self._last_reset = last_reset
            "分数上次重置的时间"
            self._highest_score_cause_time = highest_score_cause_time
            self._lowest_score_cause_time = lowest_score_cause_time
            self.history: Dict[int, "ScoreModification"] = history or {}
            "历史记录， key为时间戳（utc*1000）"
            self.achievements: Dict[int, "Achievement"] = achievements or {}
            "所获得的所有成就， key为时间戳（utc*1000）"
            self.belongs_to_group = belongs_to_group
            "所属小组"
            self._last_reset_info = last_reset_info
            "上次重置的信息"
            self.archive_uuid = ClassDataObj.archive_uuid
            "归档uuid"
        
        @DataProperty
        def last_reset(self) -> Optional[float]:
            "上次重置的时间"
            return self._last_reset

        @last_reset.setter
        def last_reset(self, value):
            self._last_reset = value
        


        @DataProperty
        def last_reset_info(self):
            "上次重置的信息"
            return (
                self._last_reset_info
                if self._last_reset_info is not None
                else dummy_student()
            )

        @last_reset_info.setter
        def last_reset_info(self, value):
            self._last_reset_info = value

        @DataProperty
        def highest_score(self):
            "最高分"
            return float(self._highest_score)

        @highest_score.setter
        def highest_score(self, value):
            # Base.log("D", f"{self.name} 更改最高分：{self._highest_score} -> {value}")
            self._highest_score = self.score_dtype(value)

        @DataProperty
        def lowest_score(self):
            "最低分"
            return float(self._lowest_score)

        @lowest_score.setter
        def lowest_score(self, value):
            self._lowest_score = self.score_dtype(value)

        @DataProperty
        def highest_score_cause_time(self):
            "最高分对应时间"
            return self._highest_score_cause_time

        @highest_score_cause_time.setter
        def highest_score_cause_time(self, value):
            self._highest_score_cause_time = value

        @DataProperty
        def lowest_score_cause_time(self):
            "最低分对应时间"
            return self._lowest_score_cause_time

        @lowest_score_cause_time.setter
        def lowest_score_cause_time(self, value):
            self._lowest_score_cause_time = value

        def __repr__(self):
            return (
                f"Student(name={self._name.__repr__()}, "
                + f"num={self._num.__repr__()}, score={self._score.__repr__()}, "
                + f"belongs_to={self._belongs_to.__repr__()}, "
                + ("history={...}, " if hasattr(self, "history") else "")
                + f"last_reset={repr(self.last_reset)}, "
                + f"highest_score={repr(self.highest_score)}, "
                + f"lowest_score={repr(self.highest_score)}, "
                + f"total_score={repr(self.highest_score)}, "
                + ("achievements={...}, " if hasattr(self, "achievements") else "")
                + f"highest_score_cause_time = {repr(self.highest_score_cause_time)}, "
                + f"lowest_score_cause_time = {repr(self.lowest_score_cause_time)}, "
                + f"belongs_to_group={repr(self.belongs_to_group)})"
            )

        @DataProperty
        def name(self):
            "学生的名字。"
            return self._name

        @name.setter
        def name(self, val):
            # if len(val) >= 50:
                # Base.log(
                    # "E",
                    # f"更改名字失败：不是谁名字有{len(val)}个字啊？？？？",
                    # "Student.name.setter",
                # )
                # raise ClassDataObj.OpreationError(f'请求更改的名字"{val}"过长')
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
            # if abs(val) > 1024:
                # Base.log("E", "更改学号失败：学号过大了，不合理", "Student.name.setter")
                # raise ClassDataObj.OpreationError(f"请求更改的学号{val}过大了, 无法设置")
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
            if self.score > self.highest_score:
                self.highest_score = self.score
            if self.score < self.lowest_score:
                self.lowest_score = self.score

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
                round(self._total_score, 1)
                if isinstance(self._total_score, float)
                else round(float(self._total_score), 1)
            )

        @total_score.setter
        def total_score(self, value):
            self._total_score = self.score_dtype(value)

        def reset_score(
            self,
        ) -> Tuple[float, float, float, Dict[int, "ScoreModification"]]:
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
            self.history: Dict[int, ScoreModification] = dict()
            self.achievements = dict()
            return returnval

        def reset_achievements(self) -> Dict[int, "Achievement"]:
            """重置学生成就。

            :return: Dict[成就达成时间utc*1000, 成就]"""
            Base.log("W", f"  -> 重置{self.name} ({self.num})的成就")
            returnval = dict(self.achievements)
            self.achievements = dict()
            return returnval

        def reset(self, reset_achievments: bool = True) -> Tuple[
            float,
            float,
            float,
            Dict[int, "ScoreModification"],
            Optional[Dict[int, "Achievement"]],
        ]:
            """重置学生分数和成就。
                这个操作会更新学生的last_reset_info属性，以记录重置前的分数和成就。

            :param reset_achievments: 是否重置成就
            :return: Tuple[当前分数, 历史最高分, 历史最低分,
            Dict[分数变动时间utc*1000, 分数变动记录], Dict[成就达成时间utc*1000, 成就]"""
            self.last_reset_info = copy.deepcopy(self)
            score, highest, lowest, history = self.reset_score()
            achievements = None
            if reset_achievments:
                achievements = self.reset_achievements()
            self.refresh_uuid()
            return (score, highest, lowest, history, achievements)

        def get_group(self, class_obs: "ClassStatusObserver") -> "Group":
            """获取学生所在小组。

            :param class_obs: 班级侦测器
            :return: Group对象"""
            return class_obs.classes[self._belongs_to].groups[self.belongs_to_group]

        def get_dumplicated_ranking(self, class_obs: "ClassStatusObserver") -> int:
            """获取学生在班级中计算重复名次的排名。

            :param class_obs: 班级侦测器
            :return: 排名"""
            if self._belongs_to != class_obs.class_id:
                raise ValueError(
                    "但是从理论层面来讲"
                    f"你不应该把{repr(class_obs.class_id)}的侦测器"
                    f"给一个{repr(self._belongs_to)}的学生"
                )

            else:
                ranking_data: List[Tuple[int, "Student"]] = (
                    class_obs.rank_non_dumplicate
                )
                for index, student in ranking_data:
                    if student.num == self.num:
                        return index
            raise ValueError(
                f"你确定这个学生({self.belongs_to})在这个班({class_obs.class_id})？"
            )

        def get_non_dumplicated_ranking(self, class_obs: "ClassStatusObserver") -> int:
            """获取学生在班级中计算非重复名次的排名。

            :param class_obs: 班级侦测器
            :return: 排名"""
            if self._belongs_to != class_obs.class_id:
                raise ValueError(
                    "但是从理论层面来讲"
                    f"你不应该把{repr(class_obs.class_id)}的侦测器"
                    f"给一个{repr(self._belongs_to)}的学生"
                )

            else:
                ranking_data: List[Tuple[int, "Student"]] = (
                    class_obs.rank_non_dumplicate
                )
                for index, student in ranking_data:
                    if student.num == self.num:
                        return index
            raise ValueError(
                f"你确定这个学生({self.belongs_to})在这个班({class_obs.class_id})？"
            )

        def __add__(
            self, value: Union["Student", float]
        ) -> "Student":
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
                    highest_score_cause_time=self.highest_score_cause_time
                    + value.highest_score_cause_time,
                    lowest_score_cause_time=self.lowest_score_cause_time,
                    belongs_to_group=self.belongs_to_group,
                    total_score=self.total_score + value.total_score,
                ).copy()

            else:
                self.score += value
                return self

        def __iadd__(
            self, value: Union["Student", float]
        ) -> "Student":
            if isinstance(value, Student):
                self.achievements.update(value.achievements)
                self.history.update(value.history)
                self.score += value
                self.total_score += value
                return self
            else:
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
                    "history": [
                        (h.execute_time_key, h.uuid)
                        for h in self.history.values()
                        if h.executed
                    ],
                    "last_reset": self.last_reset,
                    "achievements": [
                        (a.time_key, a.uuid) for a in self.achievements.values()
                    ],
                    "highest_score": self.highest_score,
                    "lowest_score": self.lowest_score,
                    "highest_score_cause_time": self.highest_score_cause_time,
                    "lowest_score_cause_time": self.lowest_score_cause_time,
                    "belongs_to_group": self.belongs_to_group,
                    "total_score": self.total_score,
                    "last_reset_info": (
                        self.last_reset_info.uuid if self._last_reset_info else None
                    ),
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str) -> "Student":
            "将字符串转换为学生对象。"
            data = json.loads(string)
            if data["type"] != Student.chunk_type_name:
                raise TypeError(
                    f"类型不匹配：{data['type']} != {Student.chunk_type_name}"
                )
            obj = Student(
                name=data["name"],
                num=data["num"],
                score=Student.score_dtype(data["score"]),
                belongs_to=data["belongs_to"],
                history={
                    k: ClassDataObj.LoadUUID(v, ScoreModification)
                    for k, v in data["history"]
                },
                last_reset=data["last_reset"],
                highest_score=data["highest_score"],
                lowest_score=data["lowest_score"],
                achievements={
                    k: ClassDataObj.LoadUUID(v, Achievement)
                    for k, v in data["achievements"]
                },
                total_score=data["total_score"],
                highest_score_cause_time=data["highest_score_cause_time"],
                lowest_score_cause_time=data["lowest_score_cause_time"],
                belongs_to_group=data["belongs_to_group"],
                last_reset_info=ClassDataObj.LoadUUID(data["last_reset_info"], Student),
            )

            obj.uuid = data["uuid"]
            obj.archive_uuid = data["archive_uuid"]
            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

    class SimpleStudent(Student):
        "一个简单的学生对象，用于存储学生信息"

        @overload
        def __init__(self, stu: "Student"): ...

        @overload
        def __init__(
            self, name: str, num: int, score: float, belongs_to: str, history: dict
        ): ...

        def __init__(
            self,
            stu_or_name,
            num=None,
            score=None,
            belongs_to=None,
            history=None,
            **kwargs,
        ):
            if isinstance(stu_or_name, Student):
                super().__init__(
                    stu_or_name._name,
                    stu_or_name._num,
                    stu_or_name._score,
                    stu_or_name._belongs_to,
                    {},
                    **(kwargs),
                )
            else:
                super().__init__(stu_or_name, num, score, belongs_to, {})
            del self.history  # 单独处理历史记录(防炸)

    class Group(Object):
        "一个小组"

        chunk_type_name: Literal["Group"] = "Group"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "Group" = None
        "空小组"

        @staticmethod
        def new_dummy():
            "创建一个空的小组"
            return Group("dummy", "dummy", Student.new_dummy(), [], "dummy")

        def __init__(
            self,
            key: str,
            name: str,
            leader: "Student",
            members: List["Student"],
            belongs_to: str,
            further_desc: str = "这个小组的组长还没有为这个小组提供详细描述",
        ) -> None:
            """
            小组的构造函数。

            :param key: 在dict中对应的key
            :param name: 名称
            :param leader: 组长
            :param members: 组员（包括组长）
            :param belongs_to: 所属班级
            :param further_desc: 详细描述
            """

            self.key = key
            "在dict中对应的key"
            self.name = name
            "名称"
            self.leader = leader
            "组长"
            self.members = members
            "所有成员（包括组长）"
            self.further_desc = further_desc
            "详细描述"
            self.belongs_to = belongs_to
            "所属班级"
            self.archive_uuid = ClassDataObj.archive_uuid
            "归档uuid"

        @property
        def total_score(self):
            "查看小组的总分。"
            return round(sum([s.score for s in self.members]), 1)

        @property
        def average_score(self):
            "查看小组的平均分。"
            return round(sum([s.score for s in self.members]) / len(self.members), 2)

        @property
        def average_score_without_lowest(self):
            "查看小组去掉最低分后的平均分。"
            return (
                (
                    round(
                        (
                            sum([s.score for s in self.members])
                            - min(*[s.score for s in self.members])
                        )
                        / (len(self.members) - 1),
                        2,
                    )
                )
                if len(self.members) > 1
                else 0.0
            )

        # 如果只有一人则返回0

        def has_member(self, student: "Student"):
            "查看一个学生是否在这个小组。"
            return any([s.num == student.num for s in self.members])

        def to_string(self):
            "将小组对象转化为字符串。"
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "key": self.key,
                    "name": self.name,
                    "leader": self.leader.uuid,
                    "members": [s.uuid for s in self.members],
                    "belongs_to": self.belongs_to,
                    "further_desc": self.further_desc,
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str):
            "将字符串转化为小组对象。"
            string = json.loads(string)
            if string["type"] != Group.chunk_type_name:
                raise TypeError(
                    f"类型不匹配：{string['type']} != {Group.chunk_type_name}"
                )
            obj = Group(
                key=string["key"],
                name=string["name"],
                leader=ClassDataObj.LoadUUID(string["leader"], Student),
                members=[ClassDataObj.LoadUUID(s, Student) for s in string["members"]],
                belongs_to=string["belongs_to"],
                further_desc=string["further_desc"],
            )
            obj.uuid = string["uuid"]
            obj.archive_uuid = string["archive_uuid"]

            return obj

        def inst_from_string(self, string: str):
            "将字符串转化为小组对象。"
            obj = Group.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

        def __repr__(self):
            return (
                f"Group(key={repr(self.key)}, "
                f"name={repr(self.name)}, "
                f"leader={repr(self.leader)}, "
                f"members={repr(self.members)}, "
                f"belongs_to={repr(self.belongs_to)}, "
                f"further_desc={repr(self.further_desc)}"
            )

    @staticmethod
    def dummy_student():
        "返回一个空的学生。"
        return Student("工具人", 0, 0, "dummy_student")

    class ScoreModificationTemplate(Object, SupportsKeyOrdering):
        "分数加减操作的模板。"

        chunk_type_name: Literal["ScoreModificationTemplate"] = (
            "ScoreModificationTemplate"
        )
        "类型名"

        is_unrelated_data_type = True
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "ScoreModificationTemplate" = None
        "空的分数加减操作模板"

        @staticmethod
        def new_dummy():
            "返回一个空的分数加减操作模板"
            return ScoreModificationTemplate("dummy", 0, "dummy")

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
            self.key = key
            self.mod = modification
            self.title = title
            self.desc = description
            self.cant_replace = cant_replace
            self.is_visible = is_visible
            self.archive_uuid = ClassDataObj.archive_uuid

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
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str):
            "将字符串转化为分数加减模板对象。"
            string = json.loads(string)
            if string["type"] != ScoreModificationTemplate.chunk_type_name:
                raise TypeError(
                    f"类型不匹配：{string['type']} != "
                    f"{ScoreModificationTemplate.chunk_type_name}"
                )
            obj = ScoreModificationTemplate(
                key=string["key"],
                modification=string["modification"],
                title=string["title"],
                description=string["description"],
                cant_replace=string["cant_replace"],
                is_visible=string["is_visible"],
            )
            obj.uuid = string["uuid"]
            obj.archive_uuid = string["archive_uuid"]

            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

    class ScoreModification(Object):
        "分数修改记录。"

        chunk_type_name: Literal["ScoreModification"] = "ScoreModification"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "ScoreModification" = None
        "空的分数加减操作记录"

        @staticmethod
        def new_dummy():
            "返回一个空的分数加减操作"
            return ScoreModification(
                ScoreModificationTemplate.new_dummy(), Student.new_dummy()
            )

        def __init__(
            self,
            template: "ScoreModificationTemplate",
            target: "Student",
            title: Optional[str] = None,
            desc: Optional[str] = None,
            mod: Optional[float] = None,
            execute_time: Optional[str] = None,
            create_time: Optional[str] = None,
            executed: bool = False,
        ):
            """
            分数加减操作的构造函数。

            :param template: 模板
            :param target: 目标学生
            :param title: 标题
            :param desc: 描述
            :param mod: 修改分数
            :param execute_time: 执行时间
            :param create_time: 创建时间
            :param executed: 是否已执行
            """
            if create_time is None:
                create_time = Base.gettime()
            self.temp = template

            if title == self.temp.title or title is None:
                self.title = self.temp.title
            else:
                self.title = title

            if desc == self.temp.desc or desc is None:
                self.desc = self.temp.desc
            else:
                self.desc = desc

            if mod == self.temp.mod or mod is None:
                self.mod = self.temp.mod
            else:
                self.mod = mod
            self.target = target
            self.execute_time = execute_time
            self.create_time = create_time
            self.executed = executed
            self.archive_uuid = ClassDataObj.archive_uuid
            self.execute_time_key = 0

        def __repr__(self):
            return (
                f"ScoreModification(template={repr(self.temp)}, "
                f"target={repr(self.target)}, title={repr(self.title)}, "
                f"desc={repr(self.desc)}, mod={repr(self.mod)}, "
                f"execute_time={repr(self.execute_time)}, create_time={repr(self.create_time)}, "
                f"executed={repr(self.executed)})"
            )

        def execute(self) -> bool:
            "执行当前的操作"
            if self.executed:
                Base.log(
                    "W",
                    "执行已经完成，无需再次执行，如需重新执行请创建新的ScoreModification对象",
                    "ScoreModification.execute",
                )
                return False

            try:
                self.execute_time = Base.gettime()
                self.execute_time_key = int(time.time() * 1000)
                if self.target.highest_score < self.target.score + self.mod:
                    self.target.highest_score = self.target.score + self.mod
                    self.target.highest_score_cause_time = self.execute_time_key

                if self.target.lowest_score > self.target.score + self.mod:
                    self.target.lowest_score = self.target.score + self.mod
                    self.target.lowest_score_cause_time = self.execute_time_key

                self.target.score += self.mod
                self.executed = True
                self.target.history[self.execute_time_key] = self
                return True

            except (
                KeyError,
                MemoryError,
                TypeError,
                ValueError,
                OverflowError,
                ZeroDivisionError,
            ) as exception:
                if debug:
                    raise ClassDataObj.OpreationError(
                        "执行加减分操作时发生错误"
                    ) from exception
                Base.log(
                    "E",
                    "执行时出现错误：\n\t\t"
                    + ("\t" * 2)
                    .join(str(traceback.format_exc()).splitlines(True))
                    .strip(),
                    "ScoreModification.execute",
                )
                return False

        def retract(self) -> Tuple[bool, str]:
            """撤销执行的操作

            :return: 是否执行成功（bool: 结果, str: 成功/失败原因）
            """
            if self not in self.target.history.values():
                Base.log("W", "当前操作未执行，无法撤回", "ScoreModification.retract")
                return False, "并不在本周历史中"
            if self.executed:
                try:
                    if self.mod < 0:
                        findscore = 0.0
                        lowestscore = 0.0
                        lowesttimekey = 0
                        # 重新计算最高分和最低分
                        for i in self.target.history:
                            tmp: ScoreModification = self.target.history[i]

                            if (
                                tmp.execute_time_key != self.execute_time_key
                                and tmp.executed
                            ):  # 排除自身
                                findscore += tmp.mod

                            if (
                                lowestscore > findscore
                                and tmp.execute_time_key != self.execute_time_key
                            ):
                                lowesttimekey = tmp.execute_time_key
                                lowestscore = findscore

                        if self.execute_time_key == lowesttimekey:
                            lowestscore = 0

                        if self.target.lowest_score_cause_time != lowesttimekey:
                            self.target.lowest_score_cause_time = lowesttimekey

                        if self.target.lowest_score != lowestscore:
                            self.target.lowest_score = lowestscore

                    else:
                        findscore = 0.0
                        highestscore = 0.0
                        highesttimekey = 0
                        for i in self.target.history:
                            tmp: ScoreModification = self.target.history[i]
                            if (
                                tmp.execute_time_key != self.execute_time_key
                                and tmp.executed
                            ):
                                findscore += tmp.mod

                            if (
                                highestscore < findscore
                                and tmp.execute_time_key != self.execute_time_key
                            ):
                                highesttimekey = tmp.execute_time_key
                                highestscore = findscore
                        if self.execute_time_key == highesttimekey:
                            highestscore = 0
                        if self.target.highest_score_cause_time != highesttimekey:
                            self.target.highest_score_cause_time = highesttimekey

                        if self.target.highest_score != highestscore:
                            self.target.highest_score = highestscore

                    self.target.score -= self.mod
                    self.executed = False
                    self.execute_time = None
                    del self
                    return True, "操作成功完成"
                except (
                    KeyError,
                    MemoryError,
                    TypeError,
                    AttributeError,
                    ValueError,
                    OverflowError,
                    ZeroDivisionError,
                ) as exception:
                    if debug:
                        raise exception
                    Base.log(
                        "E",
                        "执行时出现错误：\n\t\t"
                        + ("\t" * 2)
                        .join(str(traceback.format_exc()).splitlines(True))
                        .strip(),
                        "ScoreModification.retract",
                    )
                    return False, "执行时出现不可预测的错误"
            else:
                Base.log("W", "操作并未执行，无需撤回", "ScoreModification.retract")
                return False, "操作并未执行, 无需撤回"

        def to_string(self):
            "将分数修改记录对象转为字符串。"
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "template": self.temp.uuid,
                    "target": self.target.uuid,
                    "title": self.title,
                    "mod": self.mod,
                    "desc": self.desc,
                    "executed": self.executed,
                    "create_time": self.create_time,
                    "execute_time": self.execute_time,
                    "execute_time_key": self.execute_time_key,
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str):
            "将字符串转换为分数修改对象。"
            d = json.loads(string)
            if d["type"] != ScoreModification.chunk_type_name:
                raise ValueError(
                    f"类型不匹配：{d['type']} != "
                    f"{ScoreModification.chunk_type_name}"
                )
            obj = ScoreModification(
                template=ClassDataObj.LoadUUID(d["template"], ScoreModificationTemplate),
                target=ClassDataObj.LoadUUID(d["target"], Student),
                title=d["title"],
                mod=d["mod"],
                execute_time=d["execute_time"],
                create_time=d["create_time"],
                executed=d["executed"],
                desc=d["desc"],
            )
            obj.uuid = d["uuid"]
            obj.archive_uuid = d["archive_uuid"]
            obj.execute_time_key = d["execute_time_key"]
            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

    class HomeworkRule(Object, SupportsKeyOrdering):
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
            self.archive_uuid = ClassDataObj.archive_uuid

        def to_string(self):
            "将作业规则对象转为字符串。"
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "key": self.key,
                    "subject_name": self.subject_name,
                    "ruler": self.ruler,
                    "rule_mapping": dict(
                        [(n, t.uuid) for n, t in self.rule_mapping.items()]
                    ),
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
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

    class Class(Object, SupportsKeyOrdering):
        "一个班级"

        chunk_type_name: Literal["Class"] = "Class"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "Class" = None
        "空班级"

        @staticmethod
        def new_dummy():
            "返回一个空班级"
            return Class("工具人班寄", "dummy", {}, "dummy", {}, {}, {})

        def __init__(
            self,
            name: str,
            owner: str,
            students: Union[
                Dict[int, "Student"], OrderedKeyList["Student"]
            ],
            key: str,
            groups: Union[
                Dict[str, "Group"], OrderedKeyList["Group"]
            ],
            cleaning_mapping: Optional[
                Dict[int, Dict[Literal["member", "leader"], List["Student"]]]
            ] = None,
            homework_rules: Optional[
                Union[
                    Dict[str, "HomeworkRule"],
                    OrderedKeyList["HomeworkRule"],
                ]
            ] = None,
        ):
            """
            班级构造函数。

            :param name: 班级名称
            :param owner: 班主任
            :param students: 学生列表
            :param key: 在self.classes中对应的key
            :param cleaning_mapping: 打扫卫生人员的映射
            :param homework_rules: 作业规则
            """
            self.name = name
            self.owner = owner
            self.groups = groups if isinstance(groups, dict) else groups.to_dict()
            self.students = (
                students if isinstance(students, dict) else students.to_dict()
            )
            self.key = key
            self.cleaning_mapping = cleaning_mapping or {}
            self.homework_rules = OrderedKeyList(homework_rules or [])
            self.archive_uuid = ClassDataObj.archive_uuid

        def __repr__(self):
            return (
                f"Class(name={self.name!r}, "
                f"owner={self.owner!r}, students={self.students!r}, "
                f"key={self.key!r}, cleaning_mapping={self.cleaning_mapping!r})"
            )

        @property
        def total_score(self):
            "班级总分"
            return sum([s.score for s in self.students.values()])

        @property
        def student_count(self):
            "班级人数"
            return len(self.students)

        @property
        def student_total_score(self):
            "学生总分（好像写过了）"
            return sum([s.score for s in self.students.values()])

        @property
        def student_avg_score(self):
            "学生平均分"
            # Tip:避免除以零错误
            return self.student_total_score / max(self.student_count, 1)

        @property
        def stu_score_ord(self):
            "学生分数排序，这个不常用"
            return dict(
                enumerate(
                    sorted(list(self.students.values()), key=lambda a: a.score), start=1
                )
            )

        @property
        def rank_non_dumplicate(self):
            """学生分数排序，去重

            至于去重是个什么概念，举个例子
            >>> target_class.rank_non_dumplicate
            [
                (1, Student(name="某个学生", score=114, ...)),
                (2, Student(name="某个学生", score=51,  ...)),
                (2, Student(name="某个学生", score=51,  ...)),
                (4, Student(name="某个学生", score=41,  ...)),
                (5, Student(name="某个学生", score=9,   ...)),
                (5, Student(name="某个学生", score=9,   ...)),
                (7, Student(name="某个学生", score=1,   ...))
            ]"""
            stu_list = self.students.values()
            stu_list = sorted(stu_list, key=lambda s: s.score, reverse=True)
            stu_list2: List[Tuple[int, "Student"]] = []
            last = inf
            last_ord = 0
            cur_ord = 0
            for stu in stu_list:
                cur_ord += 1
                if stu.score == last:
                    _ord = last_ord
                else:
                    _ord = cur_ord
                    last_ord = cur_ord
                stu_list2.append((_ord, stu))
                last = stu.score
            return stu_list2

        @property
        def rank_dumplicate(self):
            """学生分数排序，不去重

            也举个例子
            >>> target_class.rank_non_dumplicate
            [
                (1, Student(name="某个学生", score=114, ...)),
                (2, Student(name="某个学生", score=51,  ...)),
                (2, Student(name="某个学生", score=51,  ...)),
                (3, Student(name="某个学生", score=41,  ...)),
                (4, Student(name="某个学生", score=9,   ...)),
                (4, Student(name="某个学生", score=9,   ...)),
                (5, Student(name="某个学生", score=1,   ...))
            ]"""
            stu_list = self.students.values()
            stu_list = sorted(stu_list, key=lambda s: s.score, reverse=True)
            stu_list2: List[Tuple[int, "Student"]] = []
            last = inf
            last_ord = 0
            for stu in stu_list:
                if stu.score != last:
                    last_ord += 1
                    last = stu.score
                stu_list2.append((last_ord, stu))
                
            return stu_list2

        def reset(self) -> "Class":
            "重置班级"
            class_orig = copy.deepcopy(self)
            Base.log("W", f" -> 重置班级：{self.name} ({self.key})")
            for s in self.students.values():
                s.reset()
            self.refresh_uuid()
            return class_orig

        def to_string(self) -> str:
            "将班级对象转换为字符串。"
            if hasattr(self, "cleaing_mapping") and not hasattr(
                self, "cleaning_mapping"
            ):
                # 也是因为之前的拼写错误
                self.cleaning_mapping: Optional[
                    Dict[
                        int, Dict[Literal["member", "leader"], List["Student"]]
                    ]
                ] = getattr(self, "cleaing_mapping")
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "key": self.key,
                    "name": self.name,
                    "owner": self.owner,
                    "students": [(s.num, s.uuid) for s in self.students.values()],
                    "groups": [(g.key, g.uuid) for g in self.groups.values()],
                    "cleaning_mapping": [
                        (k, [(t, [_s.uuid for _s in s]) for t, s in v.items()])
                        for k, v in self.cleaning_mapping.items()
                    ],
                    "homework_rules": [
                        (n, h.to_string()) for n, h in self.homework_rules.items()
                    ],
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str) -> "Class":
            "从字符串加载班级对象。"
            d = json.loads(string)
            if d["type"] != Class.chunk_type_name:
                raise ValueError(f"类型不匹配：{d['type']} != {Class.chunk_type_name}")
            obj = Class(
                name=d["name"],
                owner=d["owner"],
                students={
                    n: ClassDataObj.LoadUUID(s, Student) for n, s in d["students"]
                },
                key=d["key"],
                groups={
                    k: ClassDataObj.LoadUUID(g, Group) for k, g in d["groups"]
                },
                cleaning_mapping={
                    k: {
                        t: [ClassDataObj.LoadUUID(s, Student) for s in s]
                        for t, s in v
                    }
                    for k, v in d["cleaning_mapping"]
                },
                homework_rules={
                    n: HomeworkRule.from_string(h)
                    for n, h in d["homework_rules"]
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

    class ClassData(Object):
        "班级数据，用于判断成就"

        def __init__(
            self,
            student: "Student",
            classes: Dict[str, "Class"] = None,
            class_obs: "ClassStatusObserver" = None,
            achievement_obs: "AchievementStatusObserver" = None,
        ):
            """班级数据构造函数。

            :param student: 学生
            :param classes: 班级字典
            :param class_obs: 班级侦测器
            :param achievement_obs: 成就侦测器
            """
            self.classes = classes
            "班级的dict"
            self.class_obs = class_obs
            "班级侦测器"
            self.achievement_obs = achievement_obs
            "成就侦测器"
            self.student = student
            "学生"
            self.student_class = self.classes[self.student.belongs_to]
            "学生所在的班级"
            self.student_group = (
                self.student_class.groups[self.student.belongs_to_group]
                if self.student.belongs_to_group
                else None
            )
            "学生所在的组"
            self.groups = self.student_class.groups
            "班级中的所有组"

    class ObserverError(Exception):
        "侦测器出错"

    class AchievementTemplate(Object, SupportsKeyOrdering):
        "成就模板"

        chunk_type_name: Literal["AchievementTemplate"] = "AchievementTemplate"
        "类型名"

        is_unrelated_data_type = True
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "AchievementTemplate" = None
        "空的成就模板"

        @staticmethod
        def new_dummy():
            "返回一个空的成就模板"
            t = AchievementTemplate(
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
            when_triggered: Union[
                Literal["any", "on_reset"], Iterable[Literal["any", "on_reset"]]
            ] = "any",  # 触发时机
            # 名称等于/在列表中
            name_equals: Optional[Union[str, Iterable[str]]] = None,
            # 学号等于/在列表中
            num_equals: Optional[Union[int, Iterable[int]]] = None,
            # 名称不等于/在列表中
            name_not_equals: Optional[Union[str, Iterable[str]]] = None,
            # 学号不等于/在列表中
            num_not_equals: Optional[Union[int, Iterable[int]]] = None,
            score_range: Optional[
                Union[Tuple[float, float], List[Tuple[float, float]]]
            ] = None,  # 分数范围
            # 名次范围（不计算并列）
            score_rank_range: Optional[Tuple[int, int]] = None,
            # 最高分数范围
            highest_score_range: Optional[Tuple[float, float]] = None,
            # 最低分数范围
            lowest_score_range: Optional[Tuple[float, float]] = None,
            highest_score_cause_range: Optional[
                Tuple[int, int]
            ] = None,  # 最高分产生时间的范围（utc，*1000）
            # 最低分产生时间的范围
            lowest_score_cause_range: Optional[Tuple[int, int]] = None,
            modify_key_range: Optional[
                Union[Tuple[str, int, int], Iterable[Tuple[str, int, int]]]
            ] = None,
            # 指定点评次数的范围（必须全部符合）
            others: Optional[
                Union[
                    Callable[["ClassData"], bool],
                    Iterable[Callable[["ClassData"], bool]],
                ]
            ] = None,
            # 其他条件
            sound: Optional[str] = None,
            icon: Optional[str] = None,
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

            if name_equals is not None:
                self.name_eq = (
                    list(name_equals)
                    if isinstance(name_equals, Iterable)
                    else [name_equals]
                )

            if name_not_equals is not None:
                self.name_ne = (
                    list(name_not_equals)
                    if isinstance(name_not_equals, Iterable)
                    else [name_not_equals]
                )

            if num_equals is not None:
                self.num_eq = (
                    list(num_equals)
                    if isinstance(num_equals, Iterable)
                    else [num_equals]
                )

            if num_not_equals is not None:
                self.num_ne = (
                    list(num_not_equals)
                    if isinstance(num_not_equals, Iterable)
                    else [num_not_equals]
                )

            if score_range is not None and isinstance(score_range, Iterable):
                if not score_range:
                    Base.log(
                        "W",
                        "score_range为一个空列表，将会忽略此属性",
                        "AchievementTemplate.__init__",
                    )
                else:

                    if not isinstance(score_range[0], Iterable):
                        score_range = [score_range]
                    self.score_range = list(score_range)

            if score_rank_range is not None:
                self.score_rank_down_limit = score_rank_range[0]
                self.score_rank_up_limit = score_rank_range[1]

            if highest_score_range is not None:
                self.highest_score_down_limit = highest_score_range[0]
                self.highest_score_up_limit = highest_score_range[1]

            if lowest_score_range is not None:
                self.lowest_score_down_limit = lowest_score_range[0]
                self.lowest_score_up_limit = lowest_score_range[1]

            if highest_score_cause_range is not None:
                self.highest_score_cause_range_down_limit = highest_score_cause_range[0]
                self.highest_score_cause_range_up_limit = highest_score_cause_range[1]

            if lowest_score_cause_range is not None:
                self.lowest_score_cause_range_down_limit = lowest_score_cause_range[0]
                self.lowest_score_cause_range_up_limit = lowest_score_cause_range[1]

            if modify_key_range is not None:
                if isinstance(modify_key_range, Iterable):
                    if not len(modify_key_range):
                        Base.log(
                            "W",
                            "score_range为一个空列表，将会忽略此属性",
                            "AchievementTemplate.__init__",
                        )
                    else:
                        if not isinstance(modify_key_range[0], Iterable) or isinstance(
                            modify_key_range[0], str
                        ):
                            # tip: str也是Iterable（
                            modify_key_range = [modify_key_range]
                        self.modify_ranges_orig = modify_key_range
                        self.modify_ranges = [
                            {"key": item[0], "lowest": item[1], "highest": item[2]}
                            for item in self.modify_ranges_orig
                        ]

            if others is not None:
                if not isinstance(others, Iterable):
                    self.other = [others]
                else:
                    self.other = others

            self.when_triggered = (
                when_triggered
                if isinstance(when_triggered, Iterable)
                else [when_triggered]
            )
            self.sound = sound
            self.icon = icon
            self.further_info = further_info
            self.condition_info = condition_info
            self.archive_uuid = ClassDataObj.archive_uuid

        @property
        def kwargs(self):
            "等同于构造函数关键字参数的字典"
            kwargs = {
                "key": self.key,
                "name": self.name,
                "desc": self.desc,
            }
            if hasattr(self, "name_eq"):
                kwargs["name_equals"] = self.name_eq
            if hasattr(self, "name_ne"):
                kwargs["name_not_equals"] = self.name_ne
            if hasattr(self, "num_eq"):
                kwargs["num_equals"] = self.num_eq
            if hasattr(self, "num_ne"):
                kwargs["num_not_equals"] = self.num_ne
            if hasattr(self, "score_range"):
                kwargs["score_range"] = self.score_range
            if hasattr(self, "score_rank_down_limit"):
                kwargs["score_rank_range"] = [
                    self.score_rank_down_limit,
                    self.score_rank_up_limit,
                ]
            if hasattr(self, "highest_score_down_limit"):
                kwargs["highest_score_range"] = [
                    self.highest_score_down_limit,
                    self.highest_score_up_limit,
                ]
            if hasattr(self, "lowest_score_down_limit"):
                kwargs["lowest_score_range"] = [
                    self.lowest_score_down_limit,
                    self.lowest_score_up_limit,
                ]
            if hasattr(self, "highest_score_cause_range_down_limit"):
                kwargs["highest_score_cause_range"] = [
                    self.highest_score_cause_range_down_limit,
                    self.highest_score_cause_range_up_limit,
                ]
            if hasattr(self, "lowest_score_cause_range_down_limit"):
                kwargs["lowest_score_cause_range"] = [
                    self.lowest_score_cause_range_down_limit,
                    self.lowest_score_cause_range_up_limit,
                ]
            if hasattr(self, "modify_ranges_orig"):
                kwargs["modify_key_range"] = self.modify_ranges_orig
            if hasattr(self, "other"):
                kwargs["others"] = self.other
            if hasattr(self, "when_triggered"):
                kwargs["when_triggered"] = self.when_triggered
            if hasattr(self, "sound"):
                kwargs["sound"] = self.sound
            if hasattr(self, "icon"):
                kwargs["icon"] = self.icon
            if hasattr(self, "further_info"):
                kwargs["further_info"] = self.further_info
            if hasattr(self, "condition_info"):
                kwargs["condition_info"] = self.condition_info
            return kwargs

        def achieved_by(
            self, student: "Student", class_obs: "ClassStatusObserver"
        ) -> bool:
            """
            判断一个成就是否达成

            :param student: 学生
            :param class_obs: 班级状态侦测器
            :raise ObserverError: lambda或者function爆炸了
            :return: 是否达成"""

            # 反人类写法又出现了

            if not self.active:
                return False
            if (
                "on_reset" in self.when_triggered and "any" not in self.when_triggered
            ) and (
                not student.highest_score == student.lowest_score == student.score == 0
            ):
                return False

            if hasattr(self, "name_ne") and student.name in self.name_ne:
                return False

            if hasattr(self, "num_ne") and student.num in self.num_ne:
                return False

            if hasattr(self, "name_eq") and student.name not in self.name_eq:
                return False

            if hasattr(self, "num_eq") and student.num not in self.num_eq:
                return False

            if hasattr(self, "score_range") and not any(
                [i[0] <= student.score <= i[1] for i in self.score_range]
            ):
                return False
            try:
                if hasattr(self, "score_rank_down_limit"):
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
                    if not (
                        l
                        <= [
                            i[0]
                            for i in class_obs.rank_dumplicate
                            if i[1].num == student.num
                        ][0]
                        <= r
                    ):
                        return False
            except (
                KeyError,
                IndexError,
                TypeError,
                AttributeError,
            ) as unused:  # pylint: disable=unused-variable
                return False

            if hasattr(self, "highest_score_down_limit") and (
                not self.highest_score_down_limit
                <= student.highest_score
                <= self.highest_score_up_limit
            ):
                return False

            if hasattr(self, "highest_score_cause_range_down_limit") and (
                not self.highest_score_cause_range_down_limit
                <= student.highest_score_cause_time
                <= self.highest_score_cause_range_up_limit
            ):
                return False

            if hasattr(self, "lowest_score_down_limit") and (
                not self.lowest_score_down_limit
                <= student.lowest_score
                <= self.lowest_score_up_limit
            ):
                return False

            if hasattr(self, "lowest_score_cause_range_down_limit") and (
                not self.lowest_score_cause_range_down_limit
                <= student.lowest_score_cause_time
                <= self.lowest_score_cause_range_up_limit
            ):
                return False
            try:
                if hasattr(self, "modify_ranges") and not all(
                    [
                        item["lowest"]
                        <= [
                            history.temp.key
                            for history in student.history.values()
                            if history.executed
                        ].count(item["key"])
                        <= item["highest"]
                        for item in self.modify_ranges
                    ]
                ):
                    return False
            except (
                KeyError,
                IndexError,
                TypeError,
                AttributeError,
            ) as unused:  # pylint: disable=unused-variable
                return False

            if hasattr(self, "other"):
                try:
                    d = ClassData(
                        student=student,
                        classes=class_obs.classes,
                        class_obs=class_obs,
                        achievement_obs=class_obs.base.achievement_obs,
                    )
                    for item in self.other:
                        if not item(d):
                            return False

                except (
                    NameError,
                    TypeError,
                    SystemError,
                    AttributeError,
                    RuntimeError
                ) as e:  # pylint: disable=unused-variable
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
                        send_notice(
                            "提示",
                            "当前正在跨Python版本运行，请尽量不要切换py版本",
                            "warn",
                        )
                        runtime_flags["noticed_pyversion_changed"] = True

                    Base.log_exc(
                        f"位于成就{self.name}({self.key})的lambda函数出错：",
                        "AchievementTemplate.achieved",
                    )
                    if self.key in class_obs.base.default_achievements:
                        if isinstance(self.other, list):
                            if not isinstance(self.other[0], Callable):
                                # 还没加载，先跳过
                                return False
                            # 还没加载，先跳过
                        elif isinstance(self.other, str):
                            return False
                        self.other = class_obs.base.default_achievements[self.key].other
                        Base.log(
                            "I", "已经重置为默认值", "AchievementTemplate.achieved"
                        )
                    else:
                        raise ClassDataObj.ObserverError(
                            f"位于成就{self.name}({self.key})的lambda函数出错"
                        )
                    return False
            return True

        achieved = achieved_by
        got = achieved_by

        def condition_desc(self, class_obs: "ClassStatusObserver"):
            """
            条件描述。

            :param class_obs: 班级状态侦测器

            :return: 一个字符串"""
            return_str = ""
            if hasattr(self, "name_eq"):
                return_str += "仅适用于" + "，".join(self.name_eq) + "\n"

            if hasattr(self, "num_eq"):
                return_str += (
                    "仅适用于学号为"
                    + "，".join([str(n) for n in self.num_eq])
                    + "的学生\n"
                )

            if hasattr(self, "name_ne"):
                return_str += "不适用于" + "，".join(self.name_eq) + "\n"

            if hasattr(self, "num_ne"):
                return_str += (
                    "不适用于学号为"
                    + "，".join([str(n) for n in self.num_eq])
                    + "的学生\n"
                )

            if hasattr(self, "score_range"):
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

            if hasattr(self, "score_rank_down_limit"):
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
                        + ("倒数" if self.score_rank_up_limit < 0 else "")
                        + "第"
                        + f"{abs(self.score_rank_up_limit)}"
                        + "之间\n"
                    )  # pylint: disable=E1130

            if hasattr(self, "highest_score_down_limit"):
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
                    return_str += (
                        "没看懂，反正对历史最高分有要求（写的抽象了没法判断）\n"
                    )

            if hasattr(self, "lowest_score_down_limit"):
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
                    return_str += (
                        "没看懂，反正对历史最低分有要求（写的抽象了没法判断）\n"
                    )

            if hasattr(self, "modify_ranges"):
                for item in self.modify_ranges:
                    lowest = item["lowest"]
                    highest = item["highest"]
                    key = item["key"]
                    return_str += (
                        f'达成{lowest}到{highest}次"{class_obs.templates[key].title}"\n'
                        if lowest != highest and lowest != inf and highest != inf
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

            if hasattr(self, "other"):
                return_str += "有一些其他条件，如果没写就自己摸索吧\n"

            if return_str == "":
                return_str = "(无条件)"
            return_str += "\n" * 2 + self.condition_info
            return return_str

        def to_string(self):
            "从字符串加载成就模板对象。"
            obj = {"type": self.chunk_type_name}
            obj.update(self.kwargs)
            if "others" in obj:
                obj["others"] = base64.b64encode(pickle.dumps(obj["others"])).decode()
            obj["uuid"] = self.uuid
            obj["archive_uuid"] = self.archive_uuid
            return json.dumps(obj)

        @staticmethod
        def from_string(string: str):
            "从字符串加载成就模板对象。"
            d: Dict[str, Any] = json.loads(string)
            if d["type"] != AchievementTemplate.chunk_type_name:
                raise ValueError(
                    f"类型不匹配：{d['type']} != {AchievementTemplate.chunk_type_name}"
                )
            try:
                if "others" in d:
                    d["others"] = pickle.loads(base64.b64decode(d["others"]))
            except SystemError as e:
                if e.args[0] == "unknown opcode":
                    Base.log(
                        "E",
                        "由于版本变化，无法加载lambda，请手动修改",
                        "AchievementTemplate.from_string",
                    )
                    d.pop("others")
                else:
                    raise e
            d.pop("type")
            uuid = d.pop("uuid")
            archive_uuid = d.pop("archive_uuid")
            obj = AchievementTemplate(**d)
            obj.uuid = uuid
            obj.archive_uuid = archive_uuid
            obj.active = True
            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

    class Achievement(Object):
        "一个真实被达成的成就"

        chunk_type_name: Literal["Achievement"] = "Achievement"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "Achievement" = None
        "空的成就实例"

        @staticmethod
        def new_dummy():
            "创建一个空的成就实例"
            return Achievement(
                AchievementTemplate.new_dummy(),
                Student.new_dummy(),
                "1970-01-01 00:00:00.000",
                0,
            )

        def __init__(
            self,
            template: "AchievementTemplate",
            target: "Student",
            reach_time: str = None,
            reach_time_key: int = None,
        ):
            """一个成就的实例。

            :param template: 成就模板
            :param target: 成就的获得者
            :param reach_time: 达成时间
            :param reach_time_key: 达成时间键值
            """
            if reach_time is None:
                reach_time = Base.gettime()
            if reach_time_key is None:
                reach_time_key = utc()
            self.time = reach_time
            self.time_key = reach_time_key
            self.temp = template
            self.target = target
            self.sound = self.temp.sound
            self.archive_uuid = ClassDataObj.archive_uuid

        def give(self):
            "发放成就"
            Base.log(
                "I",
                f"发放成就：target={repr(self.target)}, "
                f"time={repr(self.time)}, key={self.time_key}",
            )
            self.target.achievements[self.time_key] = self

        def delete(self):
            "删除成就"
            Base.log(
                "I",
                f"删除成就：target={repr(self.target)}, "
                f"time={repr(self.time)}, key={self.time_key}",
            )
            del self

        def to_string(self):
            "将成就对象转换为字符串。"
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "time": self.time,
                    "time_key": self.time_key,
                    "template": self.temp.uuid,
                    "target": self.target.uuid,
                    "sound": self.sound,
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str):
            "从字符串加载成就对象。"
            d: Dict[str, Any] = json.loads(string)
            if d["type"] != Achievement.chunk_type_name:
                raise ValueError(
                    f"类型不匹配：{d['type']} != {Achievement.chunk_type_name}"
                )
            obj = Achievement(
                template=ClassDataObj.LoadUUID(d["template"], AchievementTemplate),
                target=ClassDataObj.LoadUUID(d["target"], Student),
                reach_time=d["time"],
                reach_time_key=d["time_key"],
            )
            obj.sound = d["sound"]
            obj.uuid = d["uuid"]
            obj.archive_uuid = d["archive_uuid"]
            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

    class AttendanceInfo(Object):
        "考勤信息"

        chunk_type_name: Literal["AttendanceInfo"] = "AttendanceInfo"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "AttendanceInfo" = None
        "空的考勤信息实例"

        @staticmethod
        def new_dummy():
            "返回一个空考勤信息"
            return AttendanceInfo()

        def __init__(
            self,
            target_class: str = "CLASS_TEST",
            is_early: List["Student"] = None,
            is_late: List["Student"] = None,
            is_late_more: List["Student"] = None,
            is_absent: List["Student"] = None,
            is_leave: List["Student"] = None,
            is_leave_early: List["Student"] = None,
            is_leave_late: List["Student"] = None,
        ):
            """考勤信息

            :param target_class: 目标班级
            :param is_early: 早到的学生
            :param is_late: 晚到的学生
            :param is_late_more: 晚到得相当抽象的学生
            :param is_absent: 缺勤的学生
            :param is_leave: 临时请假的学生
            :param is_leave_early: 早退的学生
            :param is_leave_late: 晚退的学生，特指某些"热爱学校"的人（直接点我名算了）"""

            if is_early is None:
                is_early = []
            if is_late is None:
                is_late = []
            if is_late_more is None:
                is_late_more = []
            if is_absent is None:
                is_absent = []
            if is_leave is None:
                is_leave = []
            if is_leave_early is None:
                is_leave_early = []
            if is_leave_late is None:
                is_leave_late = []

            self.target_class = target_class
            "目标班级"
            self.is_early = is_early
            "早到的学生"
            self.is_late = is_late
            "晚到（7:25-7:30）的学生"
            self.is_late_more = is_late_more
            "7:30以后到的"
            self.is_absent = is_absent
            "缺勤的学生"
            self.is_leave = is_leave
            "请假的学生"
            self.is_leave_early = is_leave_early
            "早退的学生"
            self.is_leave_late = is_leave_late
            "晚退的学生"
            self.archive_uuid = ClassDataObj.archive_uuid
            "存档UUID"

        def to_string(self) -> str:
            "将考勤记录对象转为字符串。"
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "target_class": self.target_class,
                    "is_early": [s.uuid for s in self.is_early],
                    "is_late": [s.uuid for s in self.is_late],
                    "is_late_more": [s.uuid for s in self.is_late_more],
                    "is_absent": [s.uuid for s in self.is_absent],
                    "is_leave": [s.uuid for s in self.is_leave],
                    "is_leave_early": [s.uuid for s in self.is_leave_early],
                    "is_leave_late": [s.uuid for s in self.is_leave_late],
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str) -> "AttendanceInfo":
            "从字符串加载出勤信息对象。"
            d = json.loads(string)
            if d["type"] != AttendanceInfo.chunk_type_name:
                raise ValueError(
                    f"类型不匹配：{d['type']} != {AttendanceInfo.chunk_type_name}"
                )
            obj = AttendanceInfo(
                target_class=d["target_class"],
                is_early=[ClassDataObj.LoadUUID(s, Student) for s in d["is_early"]],
                is_late=[ClassDataObj.LoadUUID(s, Student) for s in d["is_late"]],
                is_late_more=[ClassDataObj.LoadUUID(s, Student) for s in d["is_late_more"]],
                is_absent=[ClassDataObj.LoadUUID(s, Student) for s in d["is_absent"]],
                is_leave=[ClassDataObj.LoadUUID(s, Student) for s in d["is_leave"]],
                is_leave_early=[
                    ClassDataObj.LoadUUID(s, Student) for s in d["is_leave_early"]
                ],
                is_leave_late=[
                    ClassDataObj.LoadUUID(s, Student) for s in d["is_leave_late"]
                ],
            )
            obj.uuid = d["uuid"]
            obj.archive_uuid = d["archive_uuid"]
            return obj

        def is_normal(self, target_class: "Class") -> List["Student"]:
            "正常出勤的学生，没有缺席"
            return [
                s
                for s in target_class.students.values()
                if s.num not in [abnormal_s.num for abnormal_s in (self.is_absent)]
            ]

        @property
        def all_attended(self) -> bool:
            "今天咱班全部都出勤了（不过基本不可能）"
            return len(self.is_absent) == 0

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

    class DayRecord(Object):
        "一天的记录"

        chunk_type_name: Literal["DayRecord"] = "DayRecord"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        dummy: "DayRecord" = None
        "空的每日记录对象"

        @staticmethod
        def new_dummy():
            "返回一个空的每日记录对象"
            return DayRecord(Class.new_dummy(), 0, 0, AttendanceInfo.new_dummy())

        def __init__(
            self,
            target_class: "Class",
            weekday: int,
            create_utc: float,
            attendance_info: "AttendanceInfo",
        ):
            """构造函数。

            :param target_class: 目标班级
            :param weekday: 星期几（1-7）
            :param create_utc: 时间戳
            :param attendance_info: 考勤信息
            """
            self.weekday = weekday
            self.utc = create_utc
            self.attendance_info = attendance_info
            self.target_class = target_class
            self.archive_uuid = ClassDataObj.archive_uuid

        def to_string(self):
            "将每日记录对象转为字符串。"
            if isinstance(self.target_class, dict):
                self.target_class = self.target_class[self.target_class.keys()[0]]
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "target_class": self.target_class.uuid,
                    "weekday": self.weekday,
                    "utc": self.utc,
                    "attendance_info": self.attendance_info.uuid,
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(string: str) -> "DayRecord":
            "从字符串加载每日记录对象。"
            d = json.loads(string)
            if d["type"] != DayRecord.chunk_type_name:
                raise ValueError(
                    f"类型不匹配：{d['type']} != {DayRecord.chunk_type_name}"
                )
            obj = DayRecord(
                target_class=ClassDataObj.LoadUUID(d["target_class"], Class),
                weekday=d["weekday"],
                create_utc=d["utc"],
                attendance_info=ClassDataObj.LoadUUID(d["attendance_info"], AttendanceInfo),
            )
            obj.uuid = d["uuid"]
            obj.archive_uuid = d["archive_uuid"]
            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self

    class History(Object):
        "每次重置保留的历史记录"

        chunk_type_name: Literal["History"] = "History"
        "类型名"

        is_unrelated_data_type = False
        "是否是与其他班级数据类型无关联的数据类型"

        def __init__(
            self,
            classes: Dict[str, "Class"],
            weekdays: Dict[str, Dict[float, "DayRecord"]],
            save_time: Optional[float] = None,
        ):
            self.classes = dict(classes)
            self.time = save_time or time.time()
            weekdays = weekdays.copy()

            self.weekdays: Dict[str, Dict[float, "DayRecord"]] \
                = weekdays
            
            self.uuid = self.archive_uuid = ClassDataObj.archive_uuid
            # IMPORTANT: 这里的对象uuid和归档uuid是一样的

        def __repr__(self):
            return f"<History object at time {self.time:.3f}>"

        def to_string(self):
            "将历史记录转换为字符串。"
            for _class, item in self.weekdays.items():
                if isinstance(item, list):
                    self.weekdays[_class] = {d.utc: d for d in item}

            return json.dumps(
                {
                    "classes": {k: v.uuid for k, v in self.classes.items()},
                    "time": self.time,
                    "weekdays": [[(_class, time_key, day.uuid) for time_key, day in item.items()] \
                                    for _class, item in self.weekdays.items()],
                    "uuid": self.uuid,
                    "archive_uuid": self.archive_uuid,
                }
            )

        @staticmethod
        def from_string(s: str) -> "History":
            "从字符串加载历史记录。"
            d = json.loads(s)
            if d["type"] != History.chunk_type_name:
                raise ValueError(
                    f"类型不匹配：{d['type']} != {History.chunk_type_name}"
                )
            obj = History(
                classes={
                    k: ClassDataObj.LoadUUID(v, Class) for k, v in d["classes"].items()
                },
                weekdays={},
                save_time=d["time"],
            )
            for _class, time_key, day_uuid in d["weekdays"]:
                if _class not in obj.weekdays:
                    obj.weekdays[_class] = {}
                obj.weekdays[_class][time_key] = ClassDataObj.LoadUUID(day_uuid, DayRecord)
            obj.uuid = d["uuid"]
            obj.archive_uuid = d["archive_uuid"]
            assert obj.uuid == obj.archive_uuid, (
                "对于一个历史记录, 它的对象uuid和归档uuid必须保持一致"
                f"（当前一个是{obj.uuid}, 另一个是{obj.archive_uuid}）"
            )
            return obj

        def inst_from_string(self, string: str):
            "将字符串加载与本身。"
            obj = self.from_string(string)
            self.__dict__.update(obj.__dict__)
            return self


class ClassObjectEvents:
    "班级数据对象的事件"
    NewStudentCreated = EventType("NewStudentCreated", ClassDataObj.Student)
    "新学生创建"
    StudentRemoved = EventType("StudentRemoved", ClassDataObj.Student)
    "学生移除"
    StudentModified = EventType("StudentModified", ClassDataObj.Student)
    "学生修改"
    StudentAddedToGroup = EventType("StudentAddedToGroup", ClassDataObj.Group)
    "学生加入小组"
    StudentRemovedFromGroup = EventType("StudentRemovedFromGroup", ClassDataObj.Group)
    "学生移出小组"
    StudentAttendanceChanged = EventType("StudentAttendanceChanged", ClassDataObj.Student)
    "学生出勤状态改变"
    StudentScoreChanged = EventType("StudentScoreChanged", ClassDataObj.Student)
    "学生分数改变"
    StudentScoreModified = EventType("StudentScoreModified", ClassDataObj.Student)
    "学生分数修改"
    StudentScoreReset = EventType("StudentScoreReset", ClassDataObj.Student)
    "学生分数重置"
    StudentScoreRemoved = EventType("StudentScoreRemoved", ClassDataObj.Student)
    "学生分数移除"

class ClassStatusObserver(Object):

    "班级状态侦测器"

    on_active: bool
    "是否激活"
    student_count: int
    "学生人数"
    student_total_score: float
    "学生总分"
    class_id: str
    "班级ID"
    stu_score_ord: dict
    "学生分数排序"
    classes: Dict[str, "Class"]
    "所有班级，是一个字典（ID, 班级对象）"
    target_class: "Class"
    "目标班级"
    templates: Dict[str, "ScoreModificationTemplate"]
    "所有模板"
    opreation_record: Stack
    "操作记录"
    groups: Dict[str, "Group"]
    "所有小组"
    base: "ClassDataObj"
    "后面用到的ClassObjects，算法基层"
    last_update: float
    "上次更新时间"
    tps: int
    "最大每秒更新次数"
    rank_non_dumplicate: List[Tuple[int, "Student"]]
    "去重排名"
    rank_dumplicate: List[Tuple[int, "Student"]]
    "不去重排名"


class AchievementStatusObserver(Object):
    "成就状态侦测器"

    on_active: bool
    "是否激活"
    class_id: str
    "班级ID"
    classes: Dict[str, "Class"]
    "所有班级"
    achievement_templates: Dict[str, "AchievementTemplate"]
    "所有成就模板"
    class_obs: ClassStatusObserver
    "班级状态侦测器"
    display_achievement_queue: Queue
    "成就显示队列"
    achievement_displayer: Callable[[str, "Student"], Any]
    "成就显示函数"
    last_update: float
    "上次更新时间"
    base: "ClassDataObj"
    "算法基层"
    tps: int
    "最大每秒更新次数"


# 标准输出重定向（停用）
# stdout = sys.stdout
# stderr = sys.stderr
# Base.clear_oldfile(Base.log_file_keepcount)


Student = ClassDataObj.Student

dummy_student = ClassDataObj.dummy_student
StrippedStudent = ClassDataObj.SimpleStudent

Class = ClassDataObj.Class
Group = ClassDataObj.Group

AttendanceInfo = ClassDataObj.AttendanceInfo

ScoreModification = ClassDataObj.ScoreModification
ScoreModificationTemplate = ClassDataObj.ScoreModificationTemplate

Achievement = ClassDataObj.Achievement
AchievementTemplate = ClassDataObj.AchievementTemplate

HomeworkRule = ClassDataObj.HomeworkRule
DayRecord = ClassDataObj.DayRecord
Day = ClassDataObj.DayRecord


ClassData = ClassDataObj.ClassData
History = ClassDataObj.History


Student.dummy = default_student = Student.new_dummy()
Class.dummy = default_class = Class.new_dummy()
Group.dummy = default_group = Group.new_dummy()
Day.dummy = default_day = Day.new_dummy()
HomeworkRule.dummy = default_homework_rule = HomeworkRule.new_dummy()
ScoreModification.dummy = default_score_modification = ScoreModification.new_dummy()
ScoreModificationTemplate.dummy = default_score_template = (
    ScoreModificationTemplate.new_dummy()
)
Achievement.dummy = default_achievement = Achievement.new_dummy()
AchievementTemplate.dummy = default_achievement_template = (
    AchievementTemplate.new_dummy()
)
