from __future__ import annotations

import copy
import json
from typing import (Literal, Optional, TYPE_CHECKING, 
                    Tuple, Union, List, Dict)
from utils.consts import inf
from utils.algorithm import OrderedKeyList
from ..classdataobj import ClassDataObj
from ..basetype import ClassDataType
from utils.basetypes import Base

if TYPE_CHECKING:
    from .student import Student
    from .group import Group
    from .homeworkrule import HomeworkRule


class Class(ClassDataType):
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
                Dict[int, Student], OrderedKeyList[Student]
            ],
            key: str,
            groups: Union[
                Dict[str, Group], OrderedKeyList[Group]
            ],
            cleaning_mapping: Optional[
                Dict[int, Dict[Literal["member", "leader"], List[Student]]]
            ] = None,
            homework_rules: Optional[
                Union[
                    Dict[str, HomeworkRule],
                    OrderedKeyList[HomeworkRule],
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
            self.archive_uuid = ClassDataObj.get_archive_uuid()

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
            stu_list2: List[Tuple[int, Student]] = []
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
            stu_list2: List[Tuple[int, Student]] = []
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
                        int, Dict[Literal["member", "leader"], List[Student]]
                    ]
                ] = getattr(self, "cleaing_mapping")
            return json.dumps(
                {
                    "type": self.chunk_type_name,
                    "key": self.key,
                    "name": self.name,
                    "owner": self.owner,
                    "students": [(s.num, str(s.uuid)) for s in self.students.values()],
                    "groups": [(g.key, str(g.uuid)) for g in self.groups.values()],
                    "cleaning_mapping": [
                        (k, [(t, [str(_s.uuid) for _s in s]) for t, s in v.items()])
                        for k, v in self.cleaning_mapping.items()
                    ],
                    "homework_rules": [
                        (n, h.to_string()) for n, h in self.homework_rules.items()
                    ],
                    "uuid": str(self.uuid),
                    "archive_uuid": str(self.archive_uuid),
                }
            )

        @staticmethod
        def from_string(string: str) -> "Class":
            "从字符串加载班级对象。"
            from .student import Student
            from .group import Group
            from .homeworkrule import HomeworkRule
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
                        t: [ClassDataObj.LoadUUID(d, Student) for d in s]
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