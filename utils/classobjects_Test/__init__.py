"""
班级数据类型
"""

from typing import TypeVar, Generic


import pickle  # pylint: disable=unused-import
import dill as pickle  # pylint: disable=shadowed-import


_UT = TypeVar("_UT")


class UUIDKind(Generic[_UT], str):
    "uuid类型, UUIDKind[Student]代表这个uuid可以加载出一个学牲"

    def __init__(self, uuid: str, data_type):
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
