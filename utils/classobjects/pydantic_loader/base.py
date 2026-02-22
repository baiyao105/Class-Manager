"""
Pydantic基础模型类定义。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, ClassVar, Generic, Self, TypeVar, cast
from uuid import UUID

from pydantic import BaseModel, Field, PrivateAttr

from ..basetype import ClassDataType, ClassDataTypeUUID


T = TypeVar("T", bound=ClassDataType)


def convert_uuid_to_str(value: Any) -> Any:
    """
    将UUID转换为字符串。

    如果值是UUID类型，返回其字符串表示；
    如果值是列表，递归转换列表中的元素；
    如果值是字典，递归转换字典中的值；
    否则返回原值。

    :param value: 要转换的值
    :return: 转换后的值
    """
    if isinstance(value, UUID):
        return value.__str__()
    if isinstance(value, list):
        return [convert_uuid_to_str(item) for item in value]  # type: ignore[misc]
    if isinstance(value, dict):
        return {k: convert_uuid_to_str(v) for k, v in value.items()}  # type: ignore[misc]
    return value


class PydanticModelBase(BaseModel, ABC, Generic[T]):
    """
    所有Pydantic数据模型的基类。

    提供与ClassDataType的双向转换接口。
    """

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "use_enum_values": True,
    }

    chunk_type_name: ClassVar[str]
    "类型名"

    _target_class: ClassVar[type[ClassDataType]]
    "对应的ClassDataType类型"

    uuid: ClassDataTypeUUID[T]
    "对象唯一标识符"

    archive_uuid: UUID | None = Field(default=None)
    "归档UUID"

    created_at: datetime = Field(default_factory=datetime.now)
    "创建时间"

    updated_at: datetime = Field(default_factory=datetime.now)
    "更新时间"

    @classmethod
    @abstractmethod
    def from_class_data(cls, data: T) -> Self:
        """
        从ClassDataType对象创建Pydantic模型。

        :param data: ClassDataType对象
        :return: Pydantic模型实例
        """

    @abstractmethod
    def to_class_data(self) -> ClassDataType:
        """
        转换为ClassDataType对象。

        :return: ClassDataType对象实例
        """

    @classmethod
    def get_target_class(cls) -> type[ClassDataType]:
        "获取对应的目标ClassDataType类型。"
        return cls._target_class

    def model_dump_for_db(self) -> dict[str, Any]:
        """
        导出为适合数据库存储的格式。

        处理UUID引用，将对象引用转换为UUID字符串。
        """
        data = self.model_dump()
        result: dict[str, Any] = {}
        for key, value in data.items():
            result[key] = convert_uuid_to_str(value)
        return result


RefType = TypeVar("RefType", bound=ClassDataType)
FromType = TypeVar("FromType", bound=ClassDataType)

_type_registry: dict[str, type[ClassDataType]] = {}
"类型名称到类型的映射"


def register_type(type_cls: type[ClassDataType]) -> None:
    """
    注册类型。

    :param type_cls: 要注册的类型
    """
    _type_registry[type_cls.chunk_type_name] = type_cls


def get_type_by_name(type_name: str) -> type[ClassDataType] | None:
    """
    根据类型名称获取类型。

    :param type_name: 类型名称
    :return: 类型或None
    """
    return _type_registry.get(type_name)


class PydanticReference(BaseModel, Generic[RefType]):
    """
    对象引用模型。

    用于在序列化时表示对其他对象的引用，避免循环依赖。
    """

    model_config = {
        "frozen": False,
    }

    uuid: ClassDataTypeUUID[RefType]
    "被引用对象的UUID"

    type_name: str
    "类型名称，用于序列化和反序列化"

    _dtype: type[ClassDataType] | None = PrivateAttr(default=None)
    "缓存的类型对象"

    @staticmethod
    def from_object(obj: FromType) -> PydanticReference[FromType]:
        """
        从ClassDataType对象创建引用。

        :param obj: ClassDataType对象
        :return: PydanticReference实例
        """
        ref = PydanticReference(
            uuid=obj.uuid,
            type_name=type(obj).chunk_type_name
        )
        ref._dtype = type(obj)
        return ref

    @classmethod
    def from_uuid(cls, uuid: UUID, dtype: type[RefType]) -> PydanticReference[RefType]:
        """
        从UUID创建引用。

        :param uuid: 对象UUID
        :param dtype: ClassDataType类型
        :return: PydanticReference实例
        """
        ref = cls(
            uuid=ClassDataTypeUUID(dtype, uuid),
            type_name=dtype.chunk_type_name
        )
        ref._dtype = dtype
        return ref

    @property
    def dtype(self) -> type[ClassDataType]:
        """
        获取类型。

        :return: ClassDataType类型
        """
        if self._dtype is not None:
            return self._dtype
        type_cls = get_type_by_name(self.type_name)
        if type_cls is None:
            raise ValueError(f"未知的类型名称: {self.type_name}")
        self._dtype = type_cls  # type: ignore[assignment]
        return self._dtype

    def resolve(self) -> RefType:
        """
        解析引用，返回实际对象。

        :return: ClassDataType对象
        """
        from ..classdataloader import ClassDataLoader
        return cast(RefType, ClassDataLoader.LoadUUID(self.uuid, self.dtype))
