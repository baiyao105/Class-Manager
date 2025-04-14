"""
班级数据类型
"""
import base64
import copy
import time
import json
import traceback
from queue import Queue
from typing import (Union, TypeVar, Generic, Optional, Dict, Any,
                    Callable, Type, Literal, Tuple, List, overload,
                    Iterable)


import pickle           # pylint: disable=unused-import
import dill as pickle   # pylint: disable=shadowed-import


from utils.basetypes import Base, Object
from utils.consts import inf, debug, runtime_flags
from utils.algorithm import SupportsKeyOrdering, OrderedKeyList, Stack
from utils.functions import send_notice as _send_notice, utc
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
