from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Self, override

from ...algorithm import SupportsKeyOrdering, update_object_mapping

from ..basetype import ClassDataType, DataProperty, StringObjectDataKind
from ..classdataloader import ClassDataLoader
from .datatag import DataTag, TagSigned

if TYPE_CHECKING:
    from .student import Student


class Group(ClassDataType, SupportsKeyOrdering, TagSigned):
    "一个小组"

    chunk_type_name: str = "Group"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @classmethod
    def new_dummy(cls) -> Self:
        "创建一个空的小组"
        from .student import Student

        return cls("dummy", "dummy", Student.new_dummy(), [], "dummy")

    def __init__(
        self,
        key: str,
        name: str,
        leader: Student,
        members: list[Student],
        belongs_to: str,
        further_desc: str = "这个小组的组长还没有为这个小组提供详细描述",
        tags: list[DataTag] | None = None,
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

        self._key = key
        self._name = name
        self._leader = leader
        self._members = members
        self.further_desc = further_desc
        "详细描述"
        self.belongs_to = belongs_to
        "所属班级"
        self.archive_uuid = ClassDataLoader.get_archive_uuid()
        "归档uuid"
        self.tags = tags or []

    @DataProperty
    def key(self):
        "在dict中对应的key"
        return self._key

    @key.setter
    def key(self, value: str):
        self._key = value

    @DataProperty
    def name(self):
        "名称"
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @DataProperty
    def leader(self):
        "组长"
        return self._leader

    @leader.setter
    def leader(self, value: Student):
        self._leader = value

    @DataProperty
    def members(self):
        "所有成员（包括组长）"
        return self._members

    @members.setter
    def members(self, value: list[Student]):
        self._members = value

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
                    (sum([s.score for s in self.members]) - min(*[s.score for s in self.members]))
                    / (len(self.members) - 1),
                    2,
                )
            )
            if len(self.members) > 1
            else 0.0
        )

    # 如果只有一人则返回0

    def has_member(self, student: Student):
        "查看一个学生是否在这个小组。"
        return any([s.num == student.num for s in self.members])

    def dump_members(self) -> list[str]:
        "将小组的所有成员的uuid转化为字符串列表。"
        return [str(s.uuid) for s in self.members]

    @staticmethod
    def load_members(d: dict[str, Any]) -> list[Student]:
        "从字典加载小组的所有成员。"
        from .student import Student
        members: list[Student] = []
        for s in d["members"]:
            item = ClassDataLoader.LoadUUID(s, Student)
            assert item is not None, f"目标学生{s}加载失败"
            members.append(item)
        return members

    def dump_tags(self) -> list[str]:
        "将小组的所有标签的uuid转化为字符串列表。"
        return [str(t.uuid) for t in self.tags]
    
    @staticmethod
    def load_tags(d: dict[str, Any]) -> list[DataTag]:
        "从字典加载小组的所有标签。"
        from .datatag import DataTag
        tags: list[DataTag] = []
        for t in d["tags"]:
            item = ClassDataLoader.LoadUUID(t, DataTag)
            assert item is not None, f"目标标签{t}加载失败"
            tags.append(item)
        return tags

    @staticmethod
    def load_leader(d: dict[str, Any]) -> Student:
        "从字典加载小组的组长。"
        from .student import Student
        leader = ClassDataLoader.LoadUUID(d["leader"], Student)
        assert leader is not None, f"目标组长{d['leader']}加载失败"
        return leader

    def to_string(self) -> StringObjectDataKind[Self]:
        "将小组对象转化为字符串。"
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "key": self.key,
                "name": self.name,
                "leader": str(self.leader.uuid),
                "members": self.dump_members(), 
                "belongs_to": self.belongs_to,
                "further_desc": self.further_desc,
                "tags": self.dump_tags(),
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @classmethod
    def from_string(cls, string: str) -> Self:
        "将字符串转化为小组对象。"

        data = json.loads(string)
        if data["type"] != cls.chunk_type_name:
            raise TypeError(f"类型不匹配：{data['type']} != {cls.chunk_type_name}")
        obj = cls(
            key=data["key"],
            name=data["name"],
            leader=cls.load_leader(data),
            members=cls.load_members(data),
            belongs_to=data["belongs_to"],
            further_desc=data["further_desc"],
            tags=cls.load_tags(data)
        )
        obj.uuid = data["uuid"]
        obj.archive_uuid = data["archive_uuid"]

        return obj

    def inst_from_string(self, string: str):
        "将字符串转化为小组对象。"
        obj = self.from_string(string)
        update_object_mapping(self, obj.__dict__)
        return self

    @override
    def to_pydantic(self):
        """
        转换为Pydantic模型。

        :return: Pydantic模型实例
        """
        from ..dataloaders.pydantic_loader.models.group import GroupModel
        return GroupModel.from_class_data(self)

    def __repr__(self):
        return (
            f"Group(key={self.key!r}, "
            f"name={self.name!r}, "
            f"leader={self.leader!r}, "
            f"members={self.members!r}, "
            f"belongs_to={self.belongs_to!r}, "
            f"further_desc={self.further_desc!r}"
        )

