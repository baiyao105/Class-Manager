from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, Self, override
from uuid import UUID

from ...consts import inf
from ...basetypes import Base
from ...algorithm import TemplateList, SupportsKeyOrdering, update_object_mapping

from ..basetype import ClassDataType, ClassDataTypeUUID, DataProperty, StringObjectDataKind
from ..classdataloader import ClassDataLoader

if TYPE_CHECKING:
    from .group import Group
    from .homeworkrule import HomeworkRule
    from .student import Student


class Class(ClassDataType, SupportsKeyOrdering):
    "一个班级"

    chunk_type_name: str = "Class"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "返回一个空班级"
        return cls("工具人班寄", "dummy", {}, "dummy", {}, {}, {})

    def __init__(
        self,
        name: str,
        owner: str,
        students: dict[int, Student],  # 学生不要用OrderedKeyList，有歧义
        key: str,
        groups: dict[str, Group] | TemplateList[Group],
        cleaning_mapping: dict[int, dict[Literal["member", "leader"], list[Student]]] | None = None,
        homework_rules: dict[str, HomeworkRule] | TemplateList[HomeworkRule] | None = None,
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
        super().__init__()
        self._name = name
        self._owner = owner
        self.groups = groups if isinstance(groups, dict) else groups.to_dict()
        self.students = students
        self._key = key
        self.cleaning_mapping = cleaning_mapping or {}
        self.homework_rules = TemplateList(homework_rules or [])
        self.archive_uuid = ClassDataLoader.get_archive_uuid()

    @DataProperty
    def name(self):
        "班级名称"
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @DataProperty
    def owner(self):
        "班主任"
        return self._owner

    @owner.setter
    def owner(self, value: str):
        self._owner = value

    @DataProperty
    def key(self):
        "在self.classes中对应的key"
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

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
        return dict(enumerate(sorted(list(self.students.values()), key=lambda a: a.score), start=1))

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
        stu_list2: list[tuple[int, Student]] = []
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
        stu_list2: list[tuple[int, Student]] = []
        last = inf
        last_ord = 0
        for stu in stu_list:
            if stu.score != last:
                last_ord += 1
                last = stu.score
            stu_list2.append((last_ord, stu))

        return stu_list2

    def reset(self):
        "重置班级"
        Base.log("W", f" -> 重置班级：{self.name} ({self.key})")
        for s in self.students.values():
            s.reset()
        self.refresh_uuid()


    @staticmethod
    def load_student_list(uuid_list: list[str]) -> list[Student]:
        "从UUID字符串列表加载学生列表。"
        from .student import Student
        result: list[Student] = []
        for s in uuid_list:
            stu = ClassDataLoader.LoadUUID(
                ClassDataTypeUUID(Student, UUID(s)), Student
            )
            assert stu, f"学生列表中有一项加载失败, uuid={s}"
            result.append(stu)
        return result


    def dump_student_dict(self) -> list[tuple[int, str]]:
        "将班级的学生字典转换为UUID列表。"
        return [(n, str(s.uuid)) for n, s in self.students.items()]

    @staticmethod
    def load_student_dict(stu_list: list[tuple[int, str]]) -> dict[int, Student]:
        "从UUID列表加载学生字典。"
        from .student import Student
        result: dict[int, Student] = {}
        for n, s in stu_list:
            stu = ClassDataLoader.LoadUUID(ClassDataTypeUUID(Student, UUID(s)), Student)
            assert stu, f"学生{n}加载失败"
            result[n] = stu
        return result
        
    def dump_group_dict(self) -> list[tuple[str, str]]:
        "将班级的小组字典转换为UUID列表。"
        return [(n, str(g.uuid)) for n, g in self.groups.items()]
    
    @staticmethod
    def load_group_dict(group_list: list[tuple[str, str]]) -> dict[str, Group]:
        "从UUID列表加载小组字典。"
        from .group import Group
        result: dict[str, Group] = {}
        for n, g in group_list:
            group = ClassDataLoader.LoadUUID(ClassDataTypeUUID(Group, UUID(g)), Group)
            assert group, f"小组{n}加载失败"
            result[n] = group
        return result

    def dump_cleaning_mapping(self) \
        -> dict[int, dict[Literal["member", "leader"], list[str]]] | None:
        "将班级的清理映射转换为UUID字典。"
        return {
            k: {t: [str(_s.uuid) for _s in s] for t, s in v.items()}
            for k, v in self.cleaning_mapping.items()
        } if self.cleaning_mapping else None
    
    @staticmethod
    def load_cleaning_mapping(data: dict[int, dict[Literal["member", "leader"], list[str]]] | None) \
        -> dict[int, dict[Literal["member", "leader"], list[Student]]] | None:
        "从UUID字典加载清理映射。"
        if data is None:
            return None
        result: dict[int, dict[Literal["member", "leader"], list[Student]]] = {}
        for k, v in data.items():
            result[int(k)] = {}
            for t, s in v.items():
                result[int(k)][t] = Class.load_student_list(s)
        return result

    def dump_homework_rules(self) -> list[tuple[str, str]]:
        "将班级的作业规则转换为字符串列表。"
        return [(n, h.to_string()) for n, h in self.homework_rules.items()]

    @staticmethod
    def load_homework_rules(rules_list: list[tuple[str, str]]) \
        -> dict[str, HomeworkRule]:
        "从字符串列表加载作业规则。"
        from .homeworkrule import HomeworkRule
        result: dict[str, HomeworkRule] = {}
        for n, h in rules_list:
            rule = HomeworkRule.from_string(h)
            assert rule, f"作业规则{n}加载失败"
            result[n] = rule
        return result

    def to_string(self) -> StringObjectDataKind[Self]:
        "将班级对象转换为字符串。"
        if hasattr(self, "cleaing_mapping") and not hasattr(self, "cleaning_mapping"):
            self.cleaning_mapping: dict[int, dict[Literal["member", "leader"], list[Student]]] | None = (
                getattr(self, "cleaing_mapping")
            )
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "key": self.key,
                "name": self.name,
                "owner": self.owner,
                "students": self.dump_student_dict(),
                "groups": self.dump_group_dict(),
                "cleaning_mapping": self.dump_cleaning_mapping(),
                "homework_rules": self.dump_homework_rules(),
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "从字符串加载班级对象。"

        d = json.loads(string)
        if d["type"] != cls.chunk_type_name:
            raise ValueError(f"类型不匹配：{d['type']} != {cls.chunk_type_name}")

        obj = cls(
            name=d["name"],
            owner=d["owner"],
            students=cls.load_student_dict(d["students"]),
            key=d["key"],
            groups=cls.load_group_dict(d["groups"]),
            cleaning_mapping=cls.load_cleaning_mapping(d["cleaning_mapping"]),
            homework_rules=cls.load_homework_rules(d["homework_rules"]),
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
        from ..dataloaders.pydantic_loader.models.classtype import ClassModel
        return ClassModel.from_class_data(self)