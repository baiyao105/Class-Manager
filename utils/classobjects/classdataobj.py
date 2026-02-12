from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, TypeVar
from uuid import UUID

from .basetype import ClassDataType, ClassDataTypeUUID
from .objects import *

if TYPE_CHECKING:
    from .default import *
    # 这里先别导入，不然会循环
    # （default依赖于objects，objects依赖于observers，observers又依赖于default）
    # 不过最后还是会导入的，放心


default_user = "default"


current_archive_uuid: UUID | None = None
"当前存档的UUID，全局的"



UUIDType = TypeVar("UUIDType", bound=ClassDataType)


class ClassDataObj:
    class OpreationError(Exception):
        "操作错误。"

    class ObserverError(Exception):
        "侦测器错误。"

    @staticmethod
    def LoadUUID(uuid: ClassDataTypeUUID[UUIDType], type: type[UUIDType]) -> UUIDType:
        "以一个ClassDataTypeUUID加载数据类型。"
        raise NotImplementedError("ClassDataObj.LoadUUID在没有被设置的时候被调用")

    @staticmethod
    def get_archive_uuid():
        "获取当前存档的UUID。"
        global current_archive_uuid
        if current_archive_uuid is None:
            current_archive_uuid = uuid.uuid4()
        return current_archive_uuid

    @staticmethod
    def set_archive_uuid(value: UUID):
        "设置当前存档的UUID。"
        global current_archive_uuid
        current_archive_uuid = value

