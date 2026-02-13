from __future__ import annotations

import json
from typing import TYPE_CHECKING, Self

from ...algorithm import SupportsKeyOrdering, update_object_mapping

from ..basetype import ClassDataType, DataProperty, StringObjectDataKind
from ..classdataobj import ClassDataObj
from .datatag import DataTag, TagSigned

if TYPE_CHECKING:
    from .student import Student


class Group(ClassDataType, SupportsKeyOrdering, TagSigned):
    "一个小组"

    chunk_type_name: str = "Group"
    "类型名"

    is_unrelated_data_type = False
    "是否是与其他班级数据类型无关联的数据类型"

    @staticmethod
    def new_dummy():
        "创建一个空的小组"
        from .student import Student

        return Group("dummy", "dummy", Student.new_dummy(), [], "dummy")

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
        self.archive_uuid = ClassDataObj.get_archive_uuid()
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

    def to_string(self) -> StringObjectDataKind[Self]:
        "将小组对象转化为字符串。"
        return StringObjectDataKind(json.dumps(
            {
                "type": self.chunk_type_name,
                "key": self.key,
                "name": self.name,
                "leader": str(self.leader.uuid),
                "members": [str(s.uuid) for s in self.members],
                "belongs_to": self.belongs_to,
                "further_desc": self.further_desc,
                "tags": [str(t.uuid) for t in self.tags],
                "uuid": str(self.uuid),
                "archive_uuid": str(self.archive_uuid),
            }
        ))

    @staticmethod
    def from_string(string: str):
        "将字符串转化为小组对象。"
        from .student import Student

        data = json.loads(string)
        if data["type"] != Group.chunk_type_name:
            raise TypeError(f"类型不匹配：{data['type']} != {Group.chunk_type_name}")
        obj = Group(
            key=data["key"],
            name=data["name"],
            leader=ClassDataObj.LoadUUID(data["leader"], Student),
            members=[ClassDataObj.LoadUUID(s, Student) for s in data["members"]],
            belongs_to=data["belongs_to"],
            further_desc=data["further_desc"],
            tags=[ClassDataObj.LoadUUID(t, DataTag) for t in data["tags"]]
        )
        obj.uuid = data["uuid"]
        obj.archive_uuid = data["archive_uuid"]

        return obj

    def inst_from_string(self, string: str):
        "将字符串转化为小组对象。"
        obj = Group.from_string(string)
        update_object_mapping(self, obj.__dict__)
        return self

    def __repr__(self):
        return (
            f"Group(key={self.key!r}, "
            f"name={self.name!r}, "
            f"leader={self.leader!r}, "
            f"members={self.members!r}, "
            f"belongs_to={self.belongs_to!r}, "
            f"further_desc={self.further_desc!r}"
        )
